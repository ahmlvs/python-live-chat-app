from flask import Flask, request, session, redirect, render_template, url_for
from flask_socketio import SocketIO, send, join_room, leave_room
import random
from string import ascii_uppercase
from dotenv import load_dotenv
import os

load_dotenv()



app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
socketio = SocketIO(app)

rooms = {}

def generate_unique_code(length=4):
    code = ''.join(random.choices(ascii_uppercase, k=length))
    if code in rooms:
        return generate_unique_code(length)
    return code


@app.route('/', methods=['GET', 'POST'])
def home():
    session.clear()
    if request.method == 'POST':
        name = request.form.get('name')
        code = request.form.get('code')
        join = request.form.get('join', False)
        create = request.form.get('create', False)

        if not name:
            return render_template('home.html', 
                                   error="Pls enter a name.",
                                   name=name,
                                   code=code,)
        
        if join != False and not code:
            return render_template('home.html', 
                                   error="Pls enter a room code.",
                                   name=name,
                                   code=code,)
        
        room = code
        if create != False:
            room = generate_unique_code()
            rooms[room] = {'members': 0, 'messages': []}
        elif code not in rooms:
            return render_template('home.html', 
                                   error="Room not exists.",
                                   name=name,
                                   code=code,)
        
        session['name'] = name
        session['room'] = room

        return redirect(url_for('room'))

    return render_template('home.html')

@app.route('/room/')
def room():
    room = session.get('room')
    name = session.get('name')
    if room is None or name is None or room not in rooms:
        return redirect(url_for('home'))

    return render_template('room.html', room=room, messages=rooms[room]['messages'])


@socketio.on('connect')
def connect(auth):
    room = session.get('room')
    name = session.get('name')

    if not room or not name:
        return
    
    if room not in rooms:
        leave_room(room)
        return
    
    join_room(room)
    send({'name': name, 'message': 'has entered the room.'}, to=room)
    rooms[room]['members'] += 1
    print(f'{name} has entered the room {room}.')


@socketio.on('disconnect')
def disconnect():
    room = session.get('room')
    name = session.get('name')
    
    leave_room(room)

    if room in rooms:
        rooms[room]['members'] -= 1
        if rooms[room]['members'] <= 0:
            del rooms[room]

    send({'name': name, 'message': 'has left the room.'}, to=room)
    print(f'{name} has left the room {room}.')


@socketio.on('message')
def message(data):
    room = session.get('room')
    if room not in rooms:
        return

    name = session.get('name')
    message = data['message'].strip()
    if not message:
        return
    
    content = {
        'name': name,
        'message': message
    }

    send(content, to=room)
    rooms[room]['messages'].append(content)
    print(f'{name} said: {message}')


if __name__ == "__main__":
    socketio.run(app, debug=True)
