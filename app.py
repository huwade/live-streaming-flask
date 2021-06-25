from threading import Lock
from flask import Flask, send_from_directory, request, render_template, jsonify
from flask_compress import Compress
from flask_socketio import SocketIO
from flask_httpauth import HTTPBasicAuth
import cv2
import time
import os
import webbrowser

#######################################
#           configure start           #
#######################################
# if platform.system() == 'Windows':
#     camera = cv2.VideoCapture(0)
# elif platform.system() == 'Linux':
#     camera = cv2.VideoCapture('/dev/video0')
camera = cv2.VideoCapture(0)

FPS = 30
# frames per second, it based on your device performance. I think 10~40 is ok.

FRAMES_IN_MEM_LIMIT = 64
# motion frames that cached in memory and can be shown in web page.

# UPDATE_FREQ = 0
# update frames even no motion detected every UPDATE_FREQ frames
# set 0 to disable update, set 1 to send every frame to clients.

async_mode = "eventlet"
# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on installed packages.
#######################################
#           configure end             #
#######################################

app = Flask(__name__)
Compress(app)
app.config['SECRET_KEY'] = 'secret!!!'
socketio = SocketIO(app, async_mode=async_mode)
auth = HTTPBasicAuth()
users = {
    'user': '1234'
}

@auth.get_password
def get_pwd(username):
    print(request.headers)
    if username in users:
        return users.get(username)
    else:
        return None

thread      = None
thread_lock = Lock()


@app.route('/')
@app.route('/index.html')
@auth.login_required
def index():
    return send_from_directory(filename='chart.html', directory='static')

def get_frame():
    try:
        _, frame = camera.read()
        return frame
    except Exception as e:
        print(e)
        socketio.emit('err', str(e), namespace='/state')
        return cv2.imread('./static/stream_error.jpg')

def background_thread():
    """send openCV motion frames to clients."""
    print('start')
    while (True):
        socketio.sleep(1.0 / FPS)
        frame = get_frame()
        image = cv2.imencode('.jpg', frame)

        socketio.emit('frame',image.tobytes(), namespace='/stream')

        print('exit stream.')
    


def when_connect():
    global thread
    
    print('new connect with sid:', request.sid)
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(background_thread)
    socketio.emit('my_response', {'data': 'Connected', 'count': 0})


if __name__ == '__main__':
    # run this script with `python3 app.py` instead of `flask run`
    webbrowser.open_new('http://127.0.0.1:5000/')
    socketio.run(app, port=5000)