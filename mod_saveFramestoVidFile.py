import CREDENTIALS

from threading import Thread
import boto3
from botocore.client import Config
from cv2 import VideoWriter, VideoWriter_fourcc, VideoCapture, imshow, waitKey, destroyAllWindows

from time import time, strftime, localtime, sleep

from os import remove

import sendMessage

import random


class Store_Video(Thread):
    def __init__(self, name, q, queueLock, vid_start_time):
        Thread.__init__(self)
        self.name = name
        self.camframes = q
        self.queueLock = queueLock
        self.vid_start_time = vid_start_time
        self.check = vid_start_time + 30
        self.vid_end_time = vid_start_time + 40
        self.exit_Videoflag = 0

    def run(self):
        self.save_video()

    def save_video(self):
        print('Recording in thread', self.name)

        # Define the codec and create VideoWriter object
        videoname = 'Capture' + strftime('%b-%d_%H-%M', localtime(time())) + '_{}.mkv'.format(random.randint(1, 60))
        fourcc = VideoWriter_fourcc(*'XVID')
        out = VideoWriter(videoname, fourcc, 24.0, (640, 480))

        sleepThread = False
        # each video should last for 10 minutes
        # while time.time() < self.vid_start_time + 10: #wont work because most of the time it is waiting on the queue to get populated
        while time() < self.vid_end_time:  # not self.exit_Videoflag: #framecount (24 fframes per second = 240 frames for 10 secs)
            if self.exit_Videoflag == 1:
                break
            if sleepThread:
                sleep(2)
                pass

            with self.queueLock:
                if self.camframes.empty():
                    sleepThread = True
                    continue
                frame = self.camframes.get()
            sleepThread = False
            if frame is None:
                continue
            out.write(frame)
            imshow('Laptop', frame)
            waitKey(1)

        out.release()
        destroyAllWindows()

        if self.exit_Videoflag == 2:
            self.upload_to_s3(videoname)
            self.send_sms_notification()
        elif self.exit_Videoflag == 0:
            print('removing ' + videoname)
            remove(videoname)

        print(self.name, 'thread closing.')

    def upload_to_s3(self, videoname):
        # upload to s3
        print('uploading to s3')
        s3 = boto3.client('s3', config=Config(s3={'addressing_style': 'path'}))
        s3.upload_file(videoname, CREDENTIALS.S3_BUCKET_NAME, "video_history/" + videoname)

    def send_sms_notification(self):
        awsSNS = Thread(target=sendMessage.sendMsg, args=('testmsg', CREDENTIALS.AWS_SNS))
        awsSNS.start()
        awsSNS.join()


if __name__ == '__main__':
    videoname = 'Capture' + strftime('%b-%d %H-%M', localtime(time())) + '_{}.mkv'.format(random.randint(1, 60))
    fourcc = VideoWriter_fourcc(*'XVID')
    out = VideoWriter(videoname, fourcc, 25, (640, 480))

    cap = VideoCapture(0)
    cap.open(0)
    cap.set(3, 640)
    cap.set(4, 480)
    timenow = time()
    while time() < timenow + 60:
        try:
            ret, frame = cap.read()
            out.write(frame)
        except KeyboardInterrupt:
            break
        imshow('exit', frame)
        if waitKey(10) == ord('q'):
            break

    destroyAllWindows()
    cap.release()
    out.release()
