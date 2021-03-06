from flask import Flask, request
from flask_socketio import SocketIO, send, join_room, leave_room, rooms, disconnect
import logging

# logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'topsecret'
socketio = SocketIO(app)

connected_clients = {}
list_of_rooms = {1: "Room 1", 2: "Room 2"}


@socketio.on('message')
def echo_message(msg):
    sender_name = connected_clients[request.sid]
    print('Message: ' + msg + ' from ' + sender_name)
    for room in [x for x in rooms(sid=request.sid) if not x == request.sid]:  # broadcast to all the rooms of the client
        msg_to_broadcast = {
            'msg': msg,
            'name': sender_name,
            'room': room
        }
        send(msg_to_broadcast, room=room, json=True)


@socketio.on('connect')
def handle_connect():
    clients_sid = request.sid
    print("client SID = %s has connected, Requesting name" % clients_sid)
    socketio.emit("send_me_name", room=clients_sid)


@socketio.on('get_name')
def get_name(name):
    logging.debug("got name from client: %s", name)
    clients_sid = request.sid
    connected_clients[clients_sid] = name  # request.sid is populated through the context of the call
    socketio.emit("get_rooms", data=list_of_rooms, room=clients_sid)


@socketio.on('join')
def add_user_to_room(room):
    clients_sid = request.sid
    name = connected_clients[clients_sid]
    try:
        room = int(room)
        list_of_rooms[room]  # verify the key exists

    except KeyError:
        socketio.send("Room Doesn't exist! Reconnect to join a room", room=clients_sid)
        disconnect()
    except TypeError:
        socketio.send("Invalid room argument! Reconnect to join a room", room=clients_sid)
        disconnect()
    except ValueError:
        socketio.send("Invalid room argument! Reconnect to join a room", room=clients_sid)
        disconnect()

    join_room(room)  # sid of client is used by context
    logging.debug("user %s has joined room %s", name, room)
    socketio.emit("ready_for_messages", room=clients_sid)
    send("%s has entered the room" % name, room=room)


@socketio.on('disconnect')
def handle_disconnected_user():
    name_of_client = connected_clients[request.sid]
    logging.info("Client %s has disconnected", name_of_client)
    for room in [x for x in rooms(sid=request.sid) if not x == request.sid]:
        socketio.send("%s has left" % name_of_client, room=room)
        leave_room(room)
    del connected_clients[request.sid]


if __name__ == '__main__':
    socketio.run(app, debug=True, log_output=False)
