import boto3
import time
import CREDENTIALS


def sendMsg(filename, number=CREDENTIALS.AWS_SNS, *args, **kwargs):
    # print('ARGS:', args)
    # print('KWARGS:', kwargs)
    awsSNS = boto3.client('sns')
    response = awsSNS.publish(
        TopicArn=number,
        Message='Home has detected movement.\n\nLink:\n' + CREDENTIALS.S3VIDLOC + filename + '\n' # + kwargs['videoname']
    )
    with open('message-log', 'a') as fin:
        timenow = time.strftime('%b-%d %H-%M', time.localtime(time.time()))
        fin.write('{0}::{1}\n'.format(timenow, response))


if __name__ == '__main__':
    sendMsg('CaptureDec-01_16-19_5.mkv', CREDENTIALS.AWS_SNS, 0, 8, 9, videoname='http.test')
