import cv2
import threading

import socket
import numpy

import CREDENTIALS


class FramesFromSourceCam(threading.Thread):
    exit_flag = 0

    def __init__(self, name, q, queueLock):
        threading.Thread.__init__(self)
        self.name = name
        self.q = q
        self.queueLock = queueLock

    def run(self):
        self.capture_frames()

    def capture_frames(self):
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            cap.open(0)
        for x in range(30):
            ret, frame = cap.read()
        while not self.exit_flag:
            ret, frame = cap.read()
            if frame is None:
                continue

            self.queueLock.acquire()
            self.q.put(frame)
            self.queueLock.release()
        print(self.name, 'thread closing.')
        cap.release()


class FrameFromSocket(threading.Thread):
    exit_flag = 0

    def __init__(self, name, q, queueLock):
        threading.Thread.__init__(self)
        self.name = name
        self.q = q
        self.queueLock = queueLock

    def run(self):
        self.process_data()
        print(self.name, 'thread closing.')

    def process_data(self):  # socket connect to receive frames from source
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((CREDENTIALS.HOST, CREDENTIALS.PORT))
            s.listen(1)
            (conn, addr) = s.accept()

            dataS = 'Hello from Server-' + socket.gethostname()

            # receive intro from client and print
            dataR = conn.recv(1024).decode('UTF-8')
            print(dataR)

            # send intro to server
            conn.send(bytes(dataS, 'UTF-8'))

            while not self.exit_flag:
                data = b''
                while 1:
                    try:
                        r = conn.recv(90456)
                        if len(r) == 0:
                            exit(0)
                        a = r.find(b'END!')
                        if a != -1:
                            data += r[:a]
                            break
                        data += r
                    except Exception as e:
                        print(e)
                        continue
                nparr = numpy.fromstring(data, numpy.uint8)
                frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                self.queueLock.acquire()
                self.q.put(frame)
                self.queueLock.release()
