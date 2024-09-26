import socket
import tkinter as tk

MAX_REQ_SIZE = 5
gui_msg = None

class TicTacToeBoard:
    size = None
    table = None
    connected = False
    game_started = False
    game_finished = False
    message = None
    window = None
    my_turn = False
    current_player = None
    
    def __init__(self):
        

        self.window = tk.Tk()
        self.window.title("Tic-Tac-Toe")
        self.window.geometry("600x400")

        self.message = tk.Label(self.window, font=("Arial", 10))
        self.message.place(relx = 1.0, rely = 0.0, anchor ='ne')

        return
    
    def start(self):
        global BOARD_SIZE
        BOARD_SIZE = 0
        
        self.b3 = tk.Button(self.window, text='3x3 Mode', width=5, height=3, command= lambda: self.make_game(3))
        self.b4 = tk.Button(self.window, text='4x4 Mode', width=5, height=3, command= lambda: self.make_game(4))
        self.b5 = tk.Button(self.window, text='5x5 Mode', width=5, height=3, command= lambda: self.make_game(5))

        self.b3.grid(row=5, column=0)
        self.b4.grid(row=5, column=1)
        self.b5.grid(row=5, column=2)

        self.message.config(text="Select Board Size:")
        return

    def make_game(self, i):
        self.size = i
        self.table = [[] for _ in range(self.size)]
        for i in range(self.size):
            for j in range(self.size):
                self.table[i][j] = -1
        
        self.b3.destroy()
        self.b4.destroy()
        self.b5.destroy()
        
        self.message.config(text="click to find match!")

        #button for connecting to server and finding a match
        # self.find_match_but = tk.Button(self.root, text="find match", width=10, height=3, command= self.find_match)
        # self.find_match_but.place(x=500, y= 100)
        
        # Initialize empty board and current player
        self.board = [[' ' for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.current_player = 'X'

        # Create buttons for each cell
        self.buttons = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                button = tk.Button(self.root, text='', width=5, height=3,
                                command=lambda i=i, j=j: self.make_move(i, j))
                button.grid(row=i, column=j)
                self.buttons[i][j] = button

        return

    def update_text(self, msg):
        self.message.config(text=msg)
        return
    
    def set_gui_msg(self, msg):
        gui_msg = msg
        return

def send_msg(message, sock): # send message through socket
    message = f"{len(message):<{MAX_REQ_SIZE}}" + message
    # print(f"Sent this message:{message}")
    sock.send(bytes(message, encoding='utf-8'))
    return

def recv_msg(sock): # receive message through socket
    req_len = int(sock.recv(MAX_REQ_SIZE).decode('utf-8'))
    return sock.recv(req_len).decode('utf-8')

def wait_for_gui():
    global gui_msg
    while(gui_msg == None):
        pass
    msg = gui_msg
    gui_msg = None
    return msg

port = 9990
server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_sock.connect(("localhost", port))

print(f"Connected to server {server_sock.getpeername()}")

server_msg = recv_msg(server_sock)
if (server_msg == "game mode?"):
    mode = input("Choose your game mode (3/4/5):") # set the game mode (3/4/5)
send_msg(mode, server_sock)

game_started = False
while (game_started == False): # wait for an opponent
    server_msg = recv_msg(server_sock)
    if (server_msg == "game started"):
        game_started = True

board_state = recv_msg(server_sock)
print(board_state)

game_finished = False
while (game_finished == False):
    server_msg = recv_msg(server_sock)

    if (server_msg == "not your turn"): # it's our opponent's turn
        print("Waiting for your opponent's move...")

    elif(server_msg == "tie"):
        board_state = recv_msg(server_sock)
        print(board_state)
        print("It's a tie!")
        game_finished = True

    elif (server_msg == "lost"): # you lost the game
        board_state = recv_msg(server_sock)
        print(board_state)
        print("You lost the game!")
        game_finished = True

    else: # it's our turn
        board_state = recv_msg(server_sock)
        print(board_state)
        move = input("Make a move!(x,y):")
        send_msg(move, server_sock)

        valid = False
        while(valid == False): # get input until a valid move is made
            server_msg = recv_msg(server_sock)

            if(server_msg == "invalid format"): # the move wasn't in the valid format
                move = input("Invalid format; Try again:")
                send_msg(move, server_sock)

            elif (server_msg == "invalid move"): # the move was invalid
                move = input("Invalid move; Try again:")
                send_msg(move, server_sock) 
 
            else: # the move was valid
                valid = True
                board_state = recv_msg(server_sock)
                print(board_state)

                response = recv_msg(server_sock) # check if the move ended the game
                if (response == "won"):
                    print("You won the game!")
                    game_finished = True
                
                elif (response == "tie"):
                    print("It's a tie!")
                    game_finished = True