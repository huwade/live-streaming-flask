from threading import Lock
from flask import Flask, send_from_directory, request, render_template, jsonify
from flask_compress import Compress
from flask_socketio import SocketIO
from flask_httpauth import HTTPBasicAuth
import cv2
import time
import os
# import platform
from driver import FrameDiff, timestamps2xyz

#######################################
#           configure start           #
#######################################
# if platform.system() == 'Windows':
#     camera = cv2.VideoCapture(0)
# elif platform.system() == 'Linux':
#     camera = cv2.VideoCapture('/dev/video0')
camera = cv2.VideoCapture(0)
# camera = cv2.VideoCapture('vtest.avi')
# your camera

FPS = 30
# frames per second, it based on your device performance. I think 10~40 is ok.

SAVE_MOTION_FRAMES = True
# save all motion frames to disk

FRAMES_IN_MEM_LIMIT = 64
# motion frames that cached in memory and can be shown in web page.

KEEP_DETECT = True
# set False to keep detect run only when clients num > 0

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
    'user': 'change_it'
}


@auth.get_password
def get_pwd(username):
    print(request.headers)
    if username in users:
        return users.get(username)
    else:
        return None


thread = None
thread_lock = Lock()