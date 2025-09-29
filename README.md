# ♟️ Networked Tic-Tac-Toe (Python)

A simple networked **Tic‑Tac‑Toe** game implemented in **Python** with a server for matchmaking and a Tkinter-based client GUI.  
The repo contains two main scripts: `server.py` (game server) and `client.py` (game client).

## ✨ Features
- Matchmaking server that pairs players for games
- Supports multiple board sizes (3×3, 4×4, 5×5) — choose when the client connects
- Threaded server to handle concurrent players
- Client GUI built with **tkinter** for interactive play

## 🧱 Project Structure
```
server.py      # Matchmaking server & game logic (threaded, socket-based)
client.py      # Tkinter GUI client that connects to the server
images/        # assets the GUI uses
```

## 🔧 Requirements
- Python 3.7+
- Standard library only: `socket`, `threading`, `tkinter` (tkinter is included with most Python installs; on some Linux distributions install `python3-tk`)

## 🚀 Run (local, simple)
1. Start the server on a machine (or locally):
```bash
python3 server.py
# Server listens on port 9990 by default
```

2. Start one or more clients (on same machine or other machines that can reach the server):
```bash
python3 client.py
# The client connects to localhost:9990 by default; edit client.py if you need to connect to a remote host
```

3. When a client connects it will be prompted to choose a game mode (`3`, `4`, or `5` for board size). Wait for the server to match another player; once matched the GUI will show the board and you can play by clicking.

## 🎮 Controls & Notes
- Use the GUI to click cells and make moves. The client sends moves to the server and updates the game state based on server messages.
- The server handles win/tie detection and informs clients when a game ends.
- Run multiple clients to play against yourself locally, or host the server on a reachable machine for remote play.

## 🛡️ Security & Usage
- This is a learning/demo project — it uses plain TCP sockets and no authentication. Do **not** expose the server to untrusted networks without adding proper security (authentication, input validation, rate limiting).
- If you share the server on the internet, consider firewall rules and running behind a VPN.

---

Made with Python 🐍 — enjoy building on it!
