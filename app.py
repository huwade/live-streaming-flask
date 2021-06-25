#!/usr/bin/env python
from threading import Lock
from flask import Flask, render_template, session, request
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect

from utils import  WebCamera
import cv2
import webbrowser

# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option gased on installed packages.
async_mode = "eventlet"

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()
FPS = 30

# vs1 = WebCamera(src=0)
# vs1.start()
vs1 = cv2.VideoCapture(0)


def get_frame():
    try:
        _, frame = vs1.read()
        return frame
    except Exception as e:
        print(e)
        socketio.emit('err', str(e), namespace='/state')
        return cv2.imread('./static/stream_error.jpg')

def background_thread():
    """Example of how to send server generated events to clients."""
    count = 0

    while True:
        
        
        socketio.sleep(1.0 / FPS)
        frame = get_frame()

        _, image = cv2.imencode('.jpg', frame)
        count += 1
        socketio.emit('frame',image.tobytes(), namespace='/stream')

        # socketio.emit('my_response',
        #               {'data': 'Server generated event', 'count': count},
        #               namespace='/test')


@app.route('/')
def index():
    return render_template('index.html', async_mode=socketio.async_mode)


@socketio.on('connect', namespace='/test')
def test_connect():
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(background_thread)
    emit('my_response', {'data': 'Connected', 'count': 0})




if __name__ == '__main__':
    webbrowser.open_new('http://127.0.0.1:5000/')
    socketio.run(app, debug=True)