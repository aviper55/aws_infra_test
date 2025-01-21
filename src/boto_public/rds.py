import boto3
import botocore
import botocore.exceptions

class Rds:
    def __init__(self,db_id,rds=None):
        self.db_id=db_id
        if rds:
            self.rds=rds
        else:
            self.rds = boto3.client('rds')

    def hasPublicAccess(self):
        try:
            response= self.rds.describe_db_instances(DBInstanceIdentifier=self.db_id)
            return response.get("DBInstances")[0]['PubliclyAccessible']

        except botocore.exceptions.ClientError as error:

            print("Error: ", error)
            raise error
    def addPublicAccess(self):

        try:
            response= self.rds.modify_db_instance(DBInstanceIdentifier=self.db_id,PubliclyAccessible=True)
            return response.get("DBInstance")['PubliclyAccessible']

        except botocore.exceptions.ClientError as error:

            print("Error: ", error)
            raise error        
    def removePublicAccess(self):

        try:
            response= self.rds.modify_db_instance(DBInstanceIdentifier=self.db_id,PubliclyAccessible=False)
            return response.get("DBInstance")['PubliclyAccessible'] == False

        except botocore.exceptions.ClientError as error:

            print("Error: ", error)
            raise error
        
    
    
