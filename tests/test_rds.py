from unittest import TestCase
from boto3 import client
from botocore import exceptions
import moto
import sys
# autopep8: off
sys.path.append('./src/boto_public')
sys.path.append('./src/')


from boto_public import Rds
# autopep8: on


@moto.mock_aws
class TestSampleRds(TestCase):
    """
    Test class for the application sample AWS Lambda Function
    """

    # Test Setup
    def setUp(self) -> None:
        """
        Create mocked resources for use during tests
        """

        mocked_ec2_client = client("ec2", 'us-east-1')

        vpc = mocked_ec2_client.create_vpc(CidrBlock="10.0.0.0/16")['Vpc']

        subnet1 = mocked_ec2_client.create_subnet(
            VpcId=vpc['VpcId'], CidrBlock="10.0.1.0/24")['Subnet']
        subnet2 = mocked_ec2_client.create_subnet(
            VpcId=vpc['VpcId'], CidrBlock="10.0.2.0/24")['Subnet']
        igw = mocked_ec2_client.create_internet_gateway()['InternetGateway']
        vpc = mocked_ec2_client.attach_internet_gateway(
            InternetGatewayId=igw['InternetGatewayId'], VpcId=vpc['VpcId'])
        self.db_id = "db-id-1"
        mocked_rds_client = client("rds")
        self.mocked_rds_client = mocked_rds_client
        subnet_ids = [subnet1["SubnetId"], subnet2["SubnetId"]]

        mocked_rds_client.create_db_subnet_group(
            DBSubnetGroupName="db_subnet",
            DBSubnetGroupDescription="my db subnet",
            SubnetIds=subnet_ids,
        )

        mocked_rds_client.create_db_instance(
            DBInstanceIdentifier=self.db_id,
            DBInstanceClass="db.r5.large",
            Engine="aurora-mysql",
            PubliclyAccessible=True,
            EnableIAMDatabaseAuthentication=False,
            DBSubnetGroupName="db_subnet",
        )

        self.rds = Rds(self.db_id, mocked_rds_client)

    def test_exception(self) -> None:
        """
        Verify if raise error for non existent db
        """


        with self.assertRaises(expected_exception=exceptions.ClientError):
            rds_with_error_db = Rds("null-db", self.mocked_rds_client)
            rds_with_error_db.hasPublicAccess()

    def test_public_access(self) -> None:
        """
        Verify if rds has public access enabled
        """

        response = self.rds.hasPublicAccess()

        # Test
        self.assertEqual(response, True)

    def test_remove_public_access(self) -> None:
        """
        Verify if can remove rds public access with success
        """

        response = self.rds.hasPublicAccess()

        # Test
        self.assertEqual(response, True)

        response = self.rds.removePublicAccess()

        # Test
        self.assertEqual(response, True)

        response = self.rds.hasPublicAccess()

        print(response)
        # Test
        self.assertEqual(response, False)

    def test_add_public(self) -> None:
        """
        Verify if can add rds public access with success
        """

        response = self.rds.removePublicAccess()

        # Test
        self.assertEqual(response, True)

        response = self.rds.hasPublicAccess()

        self.assertEqual(response, False)

        response = self.rds.addPublicAccess()

        # Test
        self.assertEqual(response, True)

        response = self.rds.hasPublicAccess()

        self.assertEqual(response, True)

    def tearDown(self) -> None:

        # [13] Remove (mocked!) RDS instance
        rds_client = client("rds", region_name="us-east-1")
        rds_client.delete_db_instance(DBInstanceIdentifier=self.db_id)
