from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import random

# Create a Flask app
app = Flask(__name__)

# Create a SocketIO instance
socketio = SocketIO(app)

# Store connected users
# Key is socketid. Value is username and avatarUrl
users = {}

@app.route('/')
def index():
    return render_template('index.html')

# We're listening for the connect event
@socketio.on("connect")
def handle_connect():
    username = f"User_{random.randint(1000, 9999)}"
    # Our API requires us to send girl/boy
    gender = random.choice(["girl", "boy"])
    # https://avatar.iran.liara.run/public/boy?username=User_123 
    avatarUrl = f"https://avatar.iran.liara.run/public/{gender}?username={username}"
    
    users[request.sid] = { "username": username, "avatar": avatarUrl }
    
    # Notify others
    emit("user_joined", {"username": username, "avatar": avatarUrl }, broadcast=True)
    emit("set_username", {"username": username})


@socketio.on("disconnect")
def handle_disconnect():
    user = users.pop(request.sid, None)
    if user:
        emit("user_left", {"username": user["username"]}, broadcast=True)
        
@socketio.on("send_message")
def message(data):
    user = users.get(request.sid)
    if user:
        emit("new_message", {
            "username": user["username"],
            "avatar": user["avatar"],
            "message": data["message"]
        }, broadcast=True)


@socketio.on("update_username")
def handle_update_username(data):
    old_username = users[request.sid]["username"]
    new_username = data["username"]
    users[request.sid]["username"] = new_username
    
    emit("username_updated", {
        "old_username": old_username,
        "new_username": new_username
    },broadcast=True)

if __name__ == "__main__":
    socketio.run(app)