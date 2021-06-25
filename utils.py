import cv2
from threading import Thread

class WebCamera():
    def __init__(self, src=0, name="WebcamVideoStream"):
        self.video = cv2.VideoCapture(src)
        self.w     = 256
        self.h     = 256
        (self.grabbed, self.frame) = self.video.read()
        # initialize the thread name
        self.name = name

        # initialize the variable used to indicate if the thread should
        # be stopped
        self.stopped = False

    def start(self):
        t = Thread(target=self.update, args=())
        t.daemon = True
        t.start()
        return self
        
    def update(self):
        while True:
            ret, self.frame = self.video.read()
            
    def __del__(self):
        self.video.release()        

    def read(self):
        return self.frame     
        
    def resize(self,w,h):
        self.w = int(w)
        self.h = int(h)