import socket
import boto3
from botocore.client import Config

import CREDENTIALS


def send_frame_for_process(frame_file_name, result, frameQLock):
    print('Uploading frame to S3: send frame for process')
    try:

        s3 = boto3.client('s3', config=Config(s3={'addressing_style': 'path'}))

        # Upload tmp.txt to bucket-name at key-name
        s3.upload_file(frame_file_name, CREDENTIALS.S3_BUCKET_NAME, "process/" + frame_file_name)
        print('Uploaded', frame_file_name)
    except Exception as e:
        print(e)
    try:
        HOST = CREDENTIALS.AWS_EC2_HOST
        PORT = CREDENTIALS.AWS_EC2_PORT
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            print('Connect to aws on {} on port {}'.format(HOST, PORT))
            s.send(bytes(frame_file_name, 'UTF-8'))

            # print('Waiting on frame process result')
            dataR = s.recv(1024).decode('UTF-8')
            # print('Received frame process result')
            result.append(int(dataR))
            print('Human Detected' if int(dataR) else 'No Human detected')
            # print('Closing thread send frame')
    except ConnectionRefusedError:
        print("Could not connect")
