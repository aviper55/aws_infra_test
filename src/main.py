'''
Sample for removing public access in Rds,Ec2 or S3 
'''
from boto_public.s3_acl import S3Acl
from boto_public.rds import Rds
from boto_public.ec2 import Ec2


def removePublicAccessFromBucket(bucket="app3buckettest"):

    s3 = S3Acl(bucket)
    s3.removePublicAccess()


def removePublicAccessDatabase():

    rds = Rds(db_id="test_db_id")
    rds.removePublicAccess()


def removeSSMPolicyFromEc2():

    rds = Ec2()
    rds.removeSSMPolicy()
