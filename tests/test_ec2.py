'''
This test will mock entire vpc,ec2, subnet,iam services for tests 
'''
import moto
from boto3 import resource, client
from unittest import TestCase
import json
import sys
# autopep8: off
sys.path.append('./src/boto_public')
sys.path.append('./src/')

from boto_public import Ec2  # type: ignore
# autopep8: on


trust_policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "",
            "Effect": "Allow",
            "Principal": {
                "Service": "ec2.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}
ssm_policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ssm:DescribeAssociation",
                "ssm:GetDeployablePatchSnapshotForInstance",
                "ssm:GetDocument",
                "ssm:DescribeDocument",
                "ssm:GetManifest",
                "ssm:GetParameter",
                "ssm:GetParameters",
                "ssm:ListAssociations",
                "ssm:ListInstanceAssociations",
                "ssm:PutInventory",
                "ssm:PutComplianceItems",
                "ssm:PutConfigurePackageResult",
                "ssm:UpdateAssociationStatus",
                "ssm:UpdateInstanceAssociationStatus",
                "ssm:UpdateInstanceInformation"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "ssmmessages:CreateControlChannel",
                "ssmmessages:CreateDataChannel",
                "ssmmessages:OpenControlChannel",
                "ssmmessages:OpenDataChannel"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "ec2messages:AcknowledgeMessage",
                "ec2messages:DeleteMessage",
                "ec2messages:FailMessage",
                "ec2messages:GetEndpoint",
                "ec2messages:GetMessages",
                "ec2messages:SendReply"
            ],
            "Resource": "*"
        }
    ]
}


ssm_policy_deny = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Deny",
            "Action": [
                "ssm:DescribeAssociation",
                "ssm:GetDeployablePatchSnapshotForInstance",
                "ssm:GetDocument",
                "ssm:DescribeDocument",
                "ssm:GetManifest",
                "ssm:GetParameter",
                "ssm:GetParameters",
                "ssm:ListAssociations",
                "ssm:ListInstanceAssociations",
                "ssm:PutInventory",
                "ssm:PutComplianceItems",
                "ssm:PutConfigurePackageResult",
                "ssm:UpdateAssociationStatus",
                "ssm:UpdateInstanceAssociationStatus",
                "ssm:UpdateInstanceInformation"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "ssmmessages:CreateControlChannel",
                "ssmmessages:CreateDataChannel",
                "ssmmessages:OpenControlChannel",
                "ssmmessages:OpenDataChannel"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "ec2messages:AcknowledgeMessage",
                "ec2messages:DeleteMessage",
                "ec2messages:FailMessage",
                "ec2messages:GetEndpoint",
                "ec2messages:GetMessages",
                "ec2messages:SendReply"
            ],
            "Resource": "*"
        }
    ]
}


@moto.mock_aws
class TestSampleEC2(TestCase):
    """
    Test class for Ec2
    """

    # Test Setup
    def setUp(self) -> None:
        """
        Create mocked resources for use during tests
        """

        # [2] Mock environment & override resources

        iam = client('iam', region_name="us-east-1")
        instance_profile = iam.create_instance_profile(
            InstanceProfileName='Webserver')

        role_name = "WebserverRoleTest"
        description = 'ec2 test role'

        iam.create_role(
            Path="/",
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description=description,
            MaxSessionDuration=3600
        )

        iam.add_role_to_instance_profile(
            InstanceProfileName='Webserver',
            RoleName=role_name
        )

        iam.create_policy(
            PolicyName='ec2-ssm',
            PolicyDocument=json.dumps(ssm_policy)
        )
        iam.attach_role_policy(
            PolicyArn='arn:aws:iam::123456789012:policy/ec2-ssm',
            RoleName=role_name,
        )

        ec2_resource = resource('ec2', region_name="us-east-1")
        instances = ec2_resource.create_instances(
            ImageId='ami-00beae93a2d981137',
            MinCount=1,
            MaxCount=1,
            InstanceType='t2.micro'

        )

        ec2_client = client('ec2', region_name="us-east-1")
        instance_profile = instance_profile['InstanceProfile']
        ec2_client.associate_iam_instance_profile(
            IamInstanceProfile={
                "Name": instance_profile['InstanceProfileName'],
                "Arn": instance_profile['Arn']
            },
            InstanceId=instances[0].id
        )
        self.instances = instances
        self.ec2 = Ec2(ec2_client, iam)

    def test_has_ssm(self) -> None:
        """
        test instance contains ssm polocy
        """

        response = self.ec2.hasSSMPolicy()

        self.assertEqual(response, {
            'exists': True,
            'NewPolicy': {
                'policy_arn': 'arn:aws:iam::123456789012:policy/ec2-ssm',
                'new_policy_document': ssm_policy_deny
            }
        })

    def test_remove_policy(self) -> None:
        """
        test deny ssm policy from role
        """

        response = self.ec2.hasSSMPolicy()

        self.assertEqual(response, {
            'exists': True,
            'NewPolicy': {
                'policy_arn': 'arn:aws:iam::123456789012:policy/ec2-ssm',
                'new_policy_document': ssm_policy_deny
            }
        })
        response = self.ec2.removeSSMPolicy()

        self.assertEqual(response, True)
        response = self.ec2.hasSSMPolicy()

        self.assertEqual(response, {
            "exists": False,
            'NewPolicy': None
        })

    def tearDown(self) -> None:

        # [13] Remove (mocked!)  Objects
        ec2_client = client("ec2", region_name="us-east-1")

        ec2_client.stop_instances(
            InstanceIds=list(map(lambda x: x.id, self.instances)))
