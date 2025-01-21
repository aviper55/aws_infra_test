import boto3
import botocore
import botocore.exceptions


class S3Acl:
    def __init__(self, bucket, s3=None):
        self.bucket = bucket
        if s3:
            self.s3 = s3
        else:
            self.s3 = boto3.client('s3')

    def hasPublicAccess(self):
        try:

            response = self.s3.get_public_access_block(Bucket=self.bucket)
        except botocore.exceptions.ClientError as error:
            code = error.response.get("Error")['Code']
            if code == "NoSuchPublicAccessBlockConfiguration":
                return False
            print("Error: ", error)
            raise error
        PublicAccessBlockConfiguration = response.get(
            "PublicAccessBlockConfiguration", None)
        if PublicAccessBlockConfiguration:
            return PublicAccessBlockConfiguration != {
                'BlockPublicAcls': True,
                'IgnorePublicAcls': True,
                'BlockPublicPolicy': True,
                'RestrictPublicBuckets': True

            }
        return True

    def addPublicAccess(self):
        response = self.s3.put_public_access_block(
            Bucket=self.bucket, PublicAccessBlockConfiguration={
                'BlockPublicAcls': False,
                'IgnorePublicAcls': False,
                'BlockPublicPolicy': False,
                'RestrictPublicBuckets': False

            })
        if response.get("HTTPStatusCode", 0) == 200:
            return True
        return False

    def blockPublicAccess(self):
        response = self.s3.put_public_access_block(
            Bucket=self.bucket,
            PublicAccessBlockConfiguration={
                'BlockPublicAcls': True,
                'IgnorePublicAcls': True,
                'BlockPublicPolicy': True,
                'RestrictPublicBuckets': True

            })
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            return True
        return False

    def removePublicAccess(self):
        if self.hasPublicAccess():
            success = self.blockPublicAccess()
            if success:
                print("Removed public access for bucket:", self.bucket)
                return True
            else:
                print("Failed removing public access for bucket:", self.bucket)
        else:
            print("No Public access found")

        return False
