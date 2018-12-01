import boto3
import time
import CREDENTIALS


def sendMsg(message, number=CREDENTIALS.AWS_SNS, *args, **kwargs):
    print('ARGS:', args)
    print('KWARGS:', kwargs)
    awsSNS = boto3.client('sns')
    response = awsSNS.publish(
        TopicArn=number,
        Message='Home has detected movement.\n\nLink:\n' + message
    )
    with open('message-log', 'a') as fin:z
        timenow = time.strftime('%b-%d %H-%M', time.localtime(time.time()))
        fin.write('{0}::{1}\n'.format(timenow, response))


if __name__ == '__main__':
    sendMsg('Test 3', CREDENTIALS.AWS_SNS, 0, 8, 9)
