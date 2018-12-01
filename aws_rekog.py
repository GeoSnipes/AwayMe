import boto3
from cv2 import imencode, VideoCapture, imwrite
from sys import getsizeof
import length_of_time_codeclock
import CREDENTIALS
import time

def get_imagelabels(image, frameLable, lock):
    client = boto3.client('rekognition')

    #convert frame from cv2 source into binary for ttransfer to aws
    jpg_as_text = imencode('.jpg', image)[1].tostring()
    # print('Size of image is', getsizeof(jpg_as_text)/1000, 'KB')

    #aws api to implement AWS Rekognition
    with length_of_time_codeclock.CodeTimer('Rekog Frame'):
        response = client.detect_labels(
            Image={
                'Bytes': jpg_as_text      
            },
            MaxLabels=10,
            MinConfidence= 70
        )

    # AWS return all labels meeting the minimum requirements. 
    # Check if the human or person laabel is present
    for label in response['Labels']:
        if label['Name'] == 'Human' or label['Name'] == 'Person':
            # labels.append((label['Name'], round(label['Confidence'], 3)))
            print('Human/Person detected with confidence:', round(float(label['Confidence']), 3))
            with lock:
                frameLable.append(1)
            break
    # If not present just return 0
    with lock:
        if len(frameLable) == 0:
            frameLable.append(0)
    print(f"{time.strftime('%Y-%b-%d %H-%M', time.localtime(time.time()))}:\t{frameLable}")

if __name__ == '__main__':
    import threading
    # import length_of_time_codeclock

    cap = VideoCapture(0)
    retval, image = cap.read()
    cap.release()
    imwrite('img.jpg', image)
    with length_of_time_codeclock.CodeTimer('Time AWS'):
        get_imagelabels(image, [], threading.Lock())
