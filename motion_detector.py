# import the necessary packages
import mod_saveFramestoVidFile
import mod_getFramesFromCam
# import send_framev1
import aws_rekog
import CREDENTIALS

# import socket
import cv2
import imutils
import numpy

import time
import threading
import queue

exit_flag = 0
exit_Videoflag = 0

getCamFramesQueueLock = threading.Lock()
getCamFramesQueue = queue.Queue(0)

saveVidFramesQueueLock = threading.Lock()
saveVidQueue = queue.Queue(0)

lock = threading.Lock()

getSource = False
saveVideo = False

awsFrameResponse = []

last_rekog_time = int(time.time())
if getSource:
    # get frames over the internet
    stream = mod_getFramesFromCam.FrameFromSocket('Socket Get Frames', getCamFramesQueue, getCamFramesQueueLock)
    stream.start()
else:
    # get frames locally
    capture = mod_getFramesFromCam.FramesFromSourceCam('Capture Frames from Camera', getCamFramesQueue,
                                                       getCamFramesQueueLock)
    capture.start()

# initialize the first frame in the video stream
firstFrame = None

alreadySent = False
alreadyRecording = False

# loop over the frames of the video
while True:
    sendFrame = False
    try:
        # grab the current frame and initialize the occupied/unoccupied text
        with getCamFramesQueueLock:
            if getCamFramesQueue.empty():
                continue
            else:
                frame = getCamFramesQueue.get()
                if frame is None:
                    continue

        frameBackup = numpy.copy(frame)

        # frame = frame if args.get("video", None) is None else frame[1]
        text = "Unoccupied"

        # resize the frame, convert it to grayscale, and blur it
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)

        # if the first frame is None, initialize it
        if firstFrame is None:
            firstFrame = gray
            continue

        # compute the absolute difference between the current frame and first frame
        frameDelta = cv2.absdiff(firstFrame, gray)
        thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]

        # dilate the thresholded image to fill in holes, then find contours on thresholded image
        thresh = cv2.dilate(thresh, None, iterations=2)
        cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0] if imutils.is_cv2() else cnts[1]

        # loop over the contours
        for c in cnts:
            # if the contour is too small, ignore it
            if cv2.contourArea(c) < 2000:
                continue

            # compute the bounding box for the contour, draw it on the frame,
            # and update the text
            (x, y, w, h) = cv2.boundingRect(c)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            text = "Occupied"

            timeFound = time.time()
            sendFrame = True
            saveVideo = True

        if saveVideo and not alreadyRecording:
            print('Start recording thread')
            alreadyRecording = True
            saveVidFile = mod_saveFramestoVidFile.Store_Video('Save Video', saveVidQueue, saveVidFramesQueueLock,
                                                              timeFound)
            saveVidFile.start()

        if saveVideo and alreadyRecording:
            with saveVidFramesQueueLock:
                saveVidQueue.put(frameBackup)
            if not saveVidFile.isAlive():
                with saveVidFramesQueueLock:
                    saveVidQueue = queue.Queue(0)
                alreadyRecording = False
                saveVideo = False

        # draw the text and timestamp on the frame
        cv2.putText(frame, "Room Status: {}".format(text), (10, 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        cv2.putText(frame, time.strftime('%Y-%b-%d %H:%M', time.localtime(time.time())),
                    (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)

        # show the frame and record if the user presses a key
        cv2.imshow("Security Feed", frame)
        # cv2.imshow("Thresh", thresh)
        # cv2.imshow("Frame Delta", frameDelta)
        if cv2.waitKey(10) == ord('q'):
            break

        # without this, code calls AWS rekog a lot in a short period of time
        # this helps to limit it to once every second
        if int(time.time()) > last_rekog_time + 1:
            # print(last_rekog_time + 1, int(time.time()))
            last_rekog_time = int(time.time())

            if sendFrame and not alreadySent:
                alreadySent = True

                if False:
                    # noinspection PyUnreachableCode
                    processFrameFileName = 'Process ' + time.strftime('%Y-%b-%d %H-%M', time.localtime(timeFound)) + '.jpg'
                    cv2.imwrite(processFrameFileName, frameBackup)

                    # AWS_process_frame_Thread = threading.Thread(target = send_framev1.send_frame_for_process, args = (processFrameFileName, awsFrameResponse, lock))
                    # AWS_process_frame_Thread.start()
                else:
                    AWS_process_frame_Thread = threading.Thread(target=aws_rekog.get_imagelabels,
                                                                args=(frameBackup, awsFrameResponse, lock))
                    AWS_process_frame_Thread.start()

            try:
                if not AWS_process_frame_Thread.isAlive():
                    if len(awsFrameResponse) == 0:
                        continue

                    awsFrameRes = awsFrameResponse

                    if awsFrameRes[0] == True:
                        if time.time() > saveVidFile.check and saveVidFile.isAlive():
                            with saveVidFramesQueueLock:
                                saveVidFile.check = saveVidFile.vid_end_time
                                saveVidFile.vid_end_time += + 10

                        # 0: keep running until timer then delete
                        # 1: stop now and leave file
                        # 2: keep running until timer then save to s3
                        if saveVidFile.exit_Videoflag < 2:
                            saveVidFile.exit_Videoflag = 2

                    with lock:
                        awsFrameResponse.clear()

                    alreadySent = False

            except NameError:
                pass

    except KeyboardInterrupt:
        break

print('Cleaning up')
cv2.destroyAllWindows()
try:
    if getSource:
        stream.exit_flag = 1
        stream.join()
        print('finish stream')
    else:
        capture.exit_flag = 1
        capture.join()
        print('finish cam')

    saveVidFile.exit_Videoflag = 1
    saveVidFile.join()

    print('finish vidave')
except Exception as e:
    print(e)

print("All done")
