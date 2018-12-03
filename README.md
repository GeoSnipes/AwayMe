# HomeVideoSurveillance
Build an surveillance system that records when human in view and notifies respective party.

Note: Frames form camera is placed in a queue.


# Need an AWS account and also:
* AWS Rekognition
* AWS S3
* AWS SNS

Note: S3 can be substituted for your own internal storage location. Replace 'def upload_to_s3(self, vidname):' with whatever solution you have for storing your videos.


# Required

CREDENTIALS.py is required and is where you save your AWS credentials and other stuff you don't want to share with the public.


AWS_SNS -> AWS SNS Topic ARN
S3_BUCKET_NAME -> AWS S3 bucket name
S3VIDLOC -> base link of where video is stored on S3 (without video name)



