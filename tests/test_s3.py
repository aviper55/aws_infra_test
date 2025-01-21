from unittest import TestCase
from boto3 import resource, client
import moto
import os
import sys
# autopep8: off

sys.path.append('./src/boto_public')
sys.path.append('./src/')

from boto_public import S3Acl
# autopep8: on


@moto.mock_aws
class TestSampleS3(TestCase):
    """
    Test class for S3
    """

    # Test Setup
    def setUp(self) -> None:
        """
        Create mocked resources for use during tests
        """

        # [2] Mock environment & override resources

        self.test_s3_bucket_name = "unit_test_s3_bucket"
        os.environ["S3_BUCKET_NAME"] = self.test_s3_bucket_name

        # [3b] Set up the services: construct a (mocked!) S3 Bucket table
        s3_client = client('s3', region_name="us-east-1")
        s3_client.create_bucket(Bucket=self.test_s3_bucket_name,
                                ACL="public-read")


        mocked_s3_resource = client("s3")


        self.s3acl = S3Acl(self.test_s3_bucket_name, mocked_s3_resource)

    def test_public_access(self) -> None:
        """
        Verify if s3 has public access enabled
        """

        public = self.s3acl.hasPublicAccess()

        # Test
        self.assertEqual(public, False)
        self.s3acl.addPublicAccess()

        public = self.s3acl.hasPublicAccess()

        # Test
        self.assertEqual(public, True)

    def test_remove_public_access(self) -> None:
        """
        Verify if can remove s3 public access acl with success
        """

        self.s3acl.addPublicAccess()
        public = self.s3acl.hasPublicAccess()

        # Test
        self.assertEqual(public, True)

        self.s3acl.removePublicAccess()

        public = self.s3acl.hasPublicAccess()
        self.assertEqual(public, False)

    def tearDown(self) -> None:

        # [13] Remove (mocked!) S3 Objects and Bucket
        s3_resource = resource("s3", region_name="us-east-1")
        s3_bucket = s3_resource.Bucket(self.test_s3_bucket_name)
        for key in s3_bucket.objects.all():
            key.delete()
        s3_bucket.delete()
