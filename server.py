from threading import Thread, Lock
import socket

MAX_REQ_SIZE = 5 # bound for number of digits of the string's length that can be sent or received through socket

waiting_player3 = None # we save the the player that's waiting for an opponent in each game mode;
waiting_player4 = None # so the second player would be matched with the previous waiting player
waiting_player5 = None

waiting_game3 = None # corresponding to each waiting player in each game mode,
waiting_game4 = None # we would have a waiting game
waiting_game5 = None

mtx3 = Lock() # if multiple players attempt to connect to the server at once,
mtx4 = Lock() # race condition could happen so we set a lock for each game mode
mtx5 = Lock()

class Game: # an object which contains all the informations and operations of a single game
    
    def __init__(self, s, player): # initialize the object
        self.size = s
        self.player1 = player
        self.player2 = None
        self.curr_player = None
        self.turn = 1
        self.finish = False
        self.winner = None
        self.start = False
        self.tie = False
        self.board = [[-1 for _ in range(self.size)] for _ in range(self.size)]
        
    def board_str(self): # transform the board table to string format for printing
        s = ""
        for i in range(self.size):
            for j in range(self.size):
                sign = ""
                if (self.board[i][j] == -1):
                    sign = " "
                elif (self.board[i][j] == 1):
                    sign = "X"
                else:
                    sign = "O"

                if (j != self.size - 1):
                    s += sign + "|"
                else:
                    s += sign
                    
            if (i != self.size - 1):        
                s += "\n" + "-" * ((2*self.size) - 1) + "\n"

        return s
    
    def set_player2(self, player): # the second player is found and game can start
        self.player2 = player
        self.start = True
        self.curr_player = self.player1

    def check_turn(self, player): # check if it is the turn of the given player
        if (player == self.player1 and self.turn == 1):
            return True
        if (player == self.player2 and self.turn == 2):
            return True
        return False

    def is_valid(self, x, y): # check if a given move is valid
        x = x - 1
        y = y - 1
        
        if ( x < 0 or x > self.size - 1 or y < 0 or y > self.size - 1):
            return False
        
        if (self.board[x][y] != -1):
            return False

        return True
    
    def is_tie(self): # check if the game tie
        if (self.finish == True):
            return False

        for i in range(self.size):
            for j in range(self.size):
                if (self.board[i][j] == -1):
                    return False
        
        return True
    
    def win(self): # check if any of the two players of the game has won
        if (self.size == 3):

            for i in range(3): # check rows
                row = self.board[i]
                if (row == [0, 0, 0] or row == [1, 1, 1]):
                    return True

            for i in range(3): # check columns
                column = self.board[:][i]
                if (column == [0, 0, 0] or column == [1, 1, 1]):
                    return True
            
            diagonal1 = [self.board[i][i] for i in range(3)] # check the diagonals
            if (diagonal1 == [0, 0, 0] or diagonal1 == [1, 1, 1]):
                return True
            
            diagonal2 = [self.board[i][2 - i] for i in range(3)]
            if (diagonal2 == [0, 0, 0] or diagonal2 == [1, 1, 1]):
                return True

        if (self.size == 4):

            for i in range(4):
                for offset in range(2):
                    row = self.board[i][offset : offset + 3]
                    if (row == [0, 0, 0] or row == [1, 1, 1]):
                        return True

            for i in range(4):
                for offset in range(2):
                    column = [self.board[j + offset][i] for j in range(3)]
                    if (column == [0, 0, 0] or column == [1, 1, 1]):
                        return True
                    
            for offset_x in range(2):
                for offset_y in range(2):
                    diagonal1 = [self.board[i + offset_x][i + offset_y] for i in range(3)]
                    if (diagonal1 == [0, 0, 0] or diagonal1 == [1, 1, 1]):
                        return True
                    
                    diagonal2 = [self.board[i + offset_x][3 - i - offset_y] for i in range(3)]
                    if (diagonal2 == [0, 0, 0] or diagonal2 == [1, 1, 1]):
                        return True
                    
        if (self.size == 5):
            for i in range(5):
                for offset in range(2):
                    row = self.board[i][offset : offset + 4]
                    if (row == [0, 0, 0, 0] or row == [1, 1, 1, 1]):
                        return True

            for i in range(5):
                for offset in range(2):
                    column = [self.board[offset + j][i] for j in range(4)]
                    if (column == [0, 0, 0, 0] or column == [1, 1, 1, 1]):
                        return True
                    
            for offset_x in range(2):
                for offset_y in range(2):
                    diagonal1 = [self.board[i + offset_x][i + offset_y] for i in range(4)]
                    if (diagonal1 == [0, 0, 0, 0] or diagonal1 == [1, 1, 1, 1]):
                        return True
                    
                    diagonal2 = [self.board[i + offset_x][4 - i - offset_y] for i in range(4)]
                    if (diagonal2 == [0, 0, 0, 0] or diagonal2 == [1, 1, 1, 1]):
                        return True
                    
        return False
    
    def set_move(self, x, y): # set the given move
        x = x - 1
        y = y - 1

        if (self.turn == 1):
            movement = 0
        else:
            movement = 1
        
        self.board[x][y] = movement

        if (self.win()): # check if the move caused a win
            self.finish = True
            if(self.turn == 1):
                self.winner = self.player1
            else:
                self.winner = self.player2
        else:
            if(self.is_tie()):
                self.finish = True
                self.tie = True
        
        if (self.turn == 1):
            self.turn = 2
            self.curr_player = self.player2
        else:
            self.turn = 1
            self.curr_player = self.player1

def split_move(move_str): # transform the move string into x and y
    index = -1
    for i in range(len(move_str)):
        if (move_str[i] == ','):
            index = i
            break

    x = int(move_str[:index])
    y = int(move_str[index + 1:])

    return x, y

def check_format(move_str): # check if the move is in the format: x,y
    length = len(move_str)
    index = -1
    for i in range(length):
        if (move_str[i] == ','):
            index = i
            break

    if (index == -1 or index == 0 or index == length - 1):
        return False
    
    if (move_str[:index].isdigit() == False or move_str[index + 1:].isdigit() == False):
        return False
    
    return True

def send_msg(message, sock): # send message through socket
    message = f"{len(message):<{MAX_REQ_SIZE}}" + message
    sock.send(bytes(message, encoding='utf-8'))
    return

def recv_msg(sock): # receive message through socket
    req_len = int(sock.recv(MAX_REQ_SIZE).decode('utf-8'))
    return sock.recv(req_len).decode('utf-8')

def handle_player(player_sock, curr_game): # handle the player on the current working thread
    global waiting_player3, waiting_player4, waiting_player5, waiting_game3, waiting_game4, waiting_game5

    send_msg("game mode?", player_sock)
    game_mode = recv_msg(player_sock)

    if (game_mode == "3"):
        mtx3.acquire()
        if (waiting_player3 == None):
            waiting_player3 = player_sock
            curr_game = Game(3, player_sock)
            waiting_game3 = curr_game
            mtx3.release()
            while(curr_game.start == False):
                continue
        else:
            curr_game = waiting_game3
            curr_game.set_player2(player_sock)
            waiting_player3 = None
            waiting_game3 = None
            mtx3.release()

    elif (game_mode == "4"):
        mtx4.acquire()
        if (waiting_player4 == None):
            waiting_player4 = player_sock
            curr_game = Game(4, player_sock)
            waiting_game4 = curr_game
            mtx4.release()
            while(curr_game.start == False):
                continue
        else:
            curr_game = waiting_game4
            curr_game.set_player2(player_sock)
            waiting_player4 = None
            waiting_game4 = None
            mtx4.release()

    elif (game_mode == "5"):
        mtx5.acquire()
        if (waiting_player5 == None):
            waiting_player5 = player_sock
            curr_game = Game(5, player_sock)
            waiting_game5 = curr_game
            mtx5.release()
            while(curr_game.start == False):
                continue
        else:
            curr_game = waiting_game5
            curr_game.set_player2(player_sock)
            waiting_player5 = None
            waiting_game5 = None
            mtx5.release()

    send_msg("game started", player_sock)
    send_msg(curr_game.board_str(), player_sock)

    flag = False
    while(flag == False):

        if(curr_game.curr_player != player_sock): # have to wait for opponent's move

            send_msg("not your turn", player_sock)
            while(curr_game.curr_player != player_sock): # do nothing until the opponent makes their move
                continue

        else: # it's player's turn
            if(curr_game.finish == True): # the game is over

                if(curr_game.tie == False): # the opponent won
                    send_msg("lost", player_sock)
                    send_msg(curr_game.board_str(), player_sock)

                else: # it's a tie
                    send_msg("tie", player_sock)
                    send_msg(curr_game.board_str(), player_sock)
                flag = True # the game is over
            else:
                send_msg("your turn", player_sock)
                send_msg(curr_game.board_str(), player_sock)

            valid = False
            while(valid == False):
                player_move = recv_msg(player_sock) # get the player's move

                if(check_format(player_move) == False): # check if the move is in the format: x,y
                    send_msg("invalid format", player_sock)
                    continue

                x_move, y_move = split_move(player_move)

                if(curr_game.is_valid(x_move, y_move) == False): # invalid move
                    send_msg("invalid move", player_sock)

                else: # valid move
                    send_msg("valid move", player_sock)
                    curr_game.set_move(x_move, y_move)
                    send_msg(curr_game.board_str(), player_sock)
                    valid = True

                    if (curr_game.finish == True): # check if the game is over
                        if (curr_game.tie == True):
                            send_msg("tie", player_sock)
                        else:
                            send_msg("won", player_sock)
                        flag = True # the game is over
                    else:
                        send_msg("not yet", player_sock)
            
if __name__ == '__main__':
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # make socket object
    port = 9990
    sock.bind(('localhost', port)) # bind to local host and a free port for listening

    while(True):
        sock.listen()
        print(f"listening on port {port}")
        sock_obj, address_info = sock.accept()
        print(f"connected to a client: IP: {address_info}")
        new_thread = Thread(target = handle_player, args = (sock_obj, None,)) # a new thread is made for handling any new player(client)
        new_thread.start()