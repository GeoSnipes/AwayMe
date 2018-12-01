import numpy as np
import cv2
import socket

import CREDENTIALS

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.settimeout(5)
    s.connect((CREDENTIALS.HOST, CREDENTIALS.PORT))

    dataS = 'Hello from Client-' + socket.gethostname()

    # send intro to server
    s.send(bytes(dataS, 'UTF-8'))

    # receive intro form server and print
    dataR = s.recv(1024).decode('UTF-8')
    print(dataR)

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        cap.open(0)

    cap.set(3, 640)
    cap.set(4, 480)

    print('Width: ', cap.get(3))
    print('Height: ', cap.get(4))
    while True:
        try:
            ret, frame = cap.read()
            data = cv2.imencode('.jpg', frame)[1].tostring()
            s.send(data)
            s.send(b'END!')
        except Exception as e:
            print('connection closed', e)
            break

    cap.release()
