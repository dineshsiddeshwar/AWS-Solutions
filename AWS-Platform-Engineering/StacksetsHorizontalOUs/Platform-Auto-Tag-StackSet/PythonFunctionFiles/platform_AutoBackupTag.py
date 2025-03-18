import boto3


class AutoTag(object):
    """Class to apply tag to resources"""

    def __init__(self, event, context):
        """constructor function will create the event"""
        print(" Init Function")
        self.event = event
        self.res_value = {}
        self.account_id = context.invoked_function_arn.split(":")[4]
        print("Account ID=", self.account_id)

    def extract_resource(self):

        """method for extracting resouce from events"""
        try:
            resource_id = self.event['detail']['resourceId']
            resource_type = self.event['detail']['newEvaluationResult'] \
                ['evaluationResultIdentifier']['evaluationResultQualifier']['resourceType']
            compliance_status = self.event['detail']['newEvaluationResult']['complianceType']
            self.res_value['region'] = self.event['region']
            self.res_value['extract_resource'] = "PASSED"
            self.res_value['resource_id'] = resource_id
            self.res_value['resource_type'] = resource_type
            self.res_value['compliance_status'] = compliance_status
            return self.res_value
        except Exception as exception:
            print("send(..) failed executing extracting resource from event(..):{} ".format(
                str(exception)))
            self.res_value['extract_resource'] = "FAILED"
            self.res_value['reason_data'] = str(exception)
            return self.res_value

    def get_tag_values(self):
        """method for reading tag values from SSM Parameter"""
        print("In get_tag_values")
        try:
            tag_list = []
            client = boto3.client('ssm')
            ssm_response = client.get_parameters_by_path(
                Path='/Platform-Backup-Tag/'
            )
            for parameter in ssm_response['Parameters']:
                tag_dict = {}
                tag_name = (parameter['Name'].split('/'))[2]
                tag_dict['Key'] = tag_name
                tag_dict['Value'] = parameter['Value']
                tag_list.append(tag_dict)
            print(tag_list)
            self.res_value['get_tag_values'] = "PASSED"
            self.res_value['Tag_list'] = tag_list
            return self.res_value
        except Exception as exception:
            print("send(..) failed executing extracting resource from event(..):{} ".format(
                str(exception)))
            self.res_value['get_tag_values'] = "FAILED"
            self.res_value['reason_data'] = str(exception)
            return self.res_value

    def tag_resource(self):
        """method for tagging resouce from events"""
        try:

            self.extract_resource()

            # Tag resource only if the status is non-compliant and resources not owned by platform or AWS  Control Tower
            if self.res_value['compliance_status'] == 'COMPLIANT' \
                    or 'AWSControlTower' in self.res_value['resource_id'] or 'Platform' in self.res_value[
                'resource_id']:
                self.res_value['tag_resource'] = "PASSED"
                return self.res_value

            # method to get tag values
            self.get_tag_values()
            print("Tagging the resource:", self.res_value['resource_id'])
            # Tag resources
            # Tag Ec2 instances, security group, nic
            if 'EC2' in self.res_value['resource_type']:
                client = boto3.client('ec2')
                response = client.create_tags(
                    Resources=[
                        self.res_value['resource_id']
                    ],
                    Tags=self.res_value['Tag_list']
                )
                print(response)
                self.res_value['EC2_tag'] = "PASSED"

            # Tag RDS
            elif 'RDS' in self.res_value['resource_type']:
                print("Inside RDS tags START................")
                client = boto3.client('rds')
                response = client.describe_db_instances()
                print("Inside RDS describe db instance and response is:", response)
                for db_instance in response['DBInstances']:
                        print("Inside for loop db_instance_name")
                        db_instance_name = db_instance['DBInstanceIdentifier']
                        print("Inside for loop db_instance_name output is:", db_instance_name)
                        rdsinstanceARN = "arn:aws:rds:" + self.res_value['region'] + ":" + self.account_id + ":db:" + db_instance_name
                        print("Inside for loop db_instance_name arn is:", rdsinstanceARN)
                        response = client.add_tags_to_resource(
                           ResourceName=rdsinstanceARN,
                           Tags=self.res_value['Tag_list']
                        )
                        print("Inside for loop db_instance_name tag response:", response)
                print(response)
                self.res_value['RDS_tag'] = "PASSED"
                print("Inside RDS tags COMPLETE................")

            else:
                print("Resource Type not supported")
                self.res_value['tag_resource'] = "FAILED"
                return self.res_value
            self.res_value['tag_resource'] = "PASSED"
            return self.res_value
        except Exception as exception:
            print(" failed executing tag resource(..):{} ".format(
                str(exception)))
            self.res_value['tag_resource'] = "FAILED"
            self.res_value['reason_data'] = str(exception)
            return self.res_value

def lambda_handler(event, context):
    """Starting point of the function"""
    try:
        result_value = {}
        print(event)
        auto_tag_object = AutoTag(event, context)
        result_value.update(auto_tag_object.tag_resource())
        result_value['AutoTag'] = "PASSED"
        print(result_value)
        return result_value
    except Exception as exception:
        print("send(..) failed lambda_handler (..):{} ".format(
            str(exception)))
        result_value['AutoTag'] = "FAILED"
        result_value['response_status'] = "FAILED"
        result_value['reason_data'] = str(exception)
        return result_value
