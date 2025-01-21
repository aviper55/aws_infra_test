import boto3
import botocore
import botocore.exceptions
import json


class Ec2:
    def __init__(self, ec2=None, iam=None):
        if ec2:
            self.ec2 = ec2
        else:
            self.ec2 = boto3.client('ec2')
        if iam:
            self.iam = iam
        else:
            self.iam = boto3.client('iam')

    def removeSSMPolicy(self, NewPolicy=None):
        if NewPolicy is None:
            NewPolicy = self.hasSSMPolicy()['NewPolicy']

        policy_arn = NewPolicy['policy_arn']
        new_policy_document = NewPolicy['new_policy_document']
        # print(new_policy_document)
        try:
            response = self.iam.create_policy_version(
                PolicyArn=policy_arn,
                PolicyDocument=json.dumps(new_policy_document),
                SetAsDefault=True
            )

            if response['PolicyVersion']:
                return True
            return False
        except botocore.exceptions.ClientError as error:
            print("Error: ", error)
            raise error

    def hasSSMPolicy(self):
        try:

            instances = self.ec2.describe_instances()
            reservations = instances.get('Reservations')
            instances_reservations = reservations[0]['Instances'][0]
            instance_profile_ec2 = instances_reservations['IamInstanceProfile']

            instance_profile_name = instance_profile_ec2['Arn'].split('/')[1]
            instance_profile = self.iam.get_instance_profile(
                InstanceProfileName=instance_profile_name)
            roles = instance_profile['InstanceProfile']['Roles']

            policies_attached = self.iam.list_attached_role_policies(
                RoleName=roles[0]['RoleName'])['AttachedPolicies']

            for policy in policies_attached:
                policy_arn = policy['PolicyArn']
                policy_data = self.iam.get_policy(PolicyArn=policy_arn)
                policy_version = policy_data['Policy']['DefaultVersionId']
                print('hasSSMPolicy version ', policy_version)
                policy_version = self.iam.get_policy_version(
                    PolicyArn=policy_arn,
                    VersionId=policy_version)
                policy_document = policy_version['PolicyVersion']['Document']
                policy_document_st = policy_document['Statement']

                for st in policy_document_st:
                    Action = st['Action']
                    Effect = st['Effect']
                    index = 'ssm:'
                    Ssm = list(filter(lambda x: index in x, Action))
                    print(Effect)
                    if Ssm and Effect == "Allow":

                        st['Effect'] = "Deny"
                        response = {
                            'exists': True,
                            'NewPolicy': {
                                'policy_arn': policy_arn,
                                'new_policy_document': policy_document
                            }
                        }
                        # print(policy_version_data)
                        return response
            return {
                "exists": False,
                'NewPolicy': None
            }
        except botocore.exceptions.ClientError as error:
            print("Error: ", error)
            raise error
