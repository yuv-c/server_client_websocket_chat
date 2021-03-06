import socketio

sio = socketio.Client()


def send_msg():
    msg = input()
    sio.send(msg)


@sio.on('json')
def json(data):
    msg = data['msg']
    name = data['name']
    room = data['room']
    print('%s: %s, room: %s' % (name, msg, room))


@sio.on('message')
def message(msg):
    print(msg)


@sio.event
def get_rooms(rooms_dict):
    print("These are the available rooms. which one would you like to join?")

    text = []
    for room_num in rooms_dict:
        text.append(str(room_num) + ") " + rooms_dict[room_num])

    print("\n".join([str(x) for x in text]))
    room_to_join = input("waiting for input...")
    sio.emit('join', room_to_join)


@sio.event
def ready_for_messages(data):
    print("Write whatever you'd like!")
    while True:
        send_msg()


@sio.event
def send_me_name(sid):
    name = input("What's your name?")
    sio.emit('get_name', data=name)


if __name__ == "__main__":
    sio.connect('http://localhost:5000')
    sio.wait()  # wait for connection to end
