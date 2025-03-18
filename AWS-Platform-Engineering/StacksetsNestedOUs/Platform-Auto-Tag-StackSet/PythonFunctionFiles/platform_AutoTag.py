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
                Path='/Platform-Tag/'
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
            # Tag S3 Buckets
            if 'S3' in self.res_value['resource_type']:
                client = boto3.client('s3')
                tags=[]
                try:
                    bucket_tagging = client.get_bucket_tagging(Bucket=self.res_value['resource_id'])
                    print('Tagging: ',bucket_tagging)
                    tags = bucket_tagging['TagSet']
                except Exception as exception:
                    str_exc = str(exception)
                    print("No tags available")
                    if str_exc in 'NoSuchTagSetError':
                        pass
                res_vals=self.res_value['Tag_list']
                for res_v in res_vals:
                    tags.append(res_v)                    
                response = client.put_bucket_tagging(Bucket=self.res_value['resource_id'],Tagging={'TagSet': tags})
                print(response)
                self.res_value['S3_tag'] = "PASSED"
            # Tag Ec2 instances, security group, nic
            elif 'EC2' in self.res_value['resource_type']:
                client = boto3.client('ec2')
                response = client.create_tags(
                    Resources=[
                        self.res_value['resource_id']
                    ],
                    Tags=self.res_value['Tag_list']
                )
                print(response)
                self.res_value['EC2_tag'] = "PASSED"

            # Tag DynamoDB Table
            elif 'DynamoDB' in self.res_value['resource_type']:
                client = boto3.client('dynamodb')
                response = client.tag_resource(
                    ResourceArn="arn:aws:dynamodb:" + self.res_value['region'] + ":" + self.account_id + ":table/" +
                                self.res_value['resource_id'],
                    Tags=self.res_value['Tag_list']
                )
                print(response)
                self.res_value['DynamoDB_tag'] = "PASSED"

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
            # Tag Redshift
            elif 'Redshift' in self.res_value['resource_type']:
                resource_arn = self.tag_redshift()
                client = boto3.client('redshift')
                if resource_arn:
                    response = client.create_tags(
                        ResourceName=resource_arn,
                        Tags=self.res_value['Tag_list']
                    )
                    print(response)
                self.res_value['Redshift'] = "PASSED"
            elif 'ElasticLoadBalancingV2' in self.res_value['resource_type']:
                client = boto3.client('elbv2')
                print(self.res_value['resource_id'])
                response = client.add_tags(
                    ResourceArns=[
                        self.res_value['resource_id']
                    ],
                    Tags=self.res_value['Tag_list']
                )
                print(response)
                self.res_value['ElasticLoadBalancingV2'] = "PASSED"
            elif 'ElasticLoadBalancing' in self.res_value['resource_type']:
                client = boto3.client('elb')
                response = client.add_tags(
                    LoadBalancerNames=[
                        self.res_value['resource_id']
                    ],
                    Tags=self.res_value['Tag_list']
                )
                print(response)
                self.res_value['ElasticLoadBalancing'] = "PASSED"

            elif 'ACM' in self.res_value['resource_type']:
                client = boto3.client('acm')
                response = client.add_tags_to_certificate(
                    CertificateArn=self.res_value['resource_id'],
                    Tags=self.res_value['Tag_list']
                )
                print(response)

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

    def tag_redshift(self):

        """method for tagging redshift resources"""
        try:
            header = "arn:aws:redshift:"
            client = boto3.client('redshift')
            resource_arn = " "
            if self.res_value['resource_type'] == "AWS::Redshift::Cluster":
                resource_arn = header + self.res_value['region'] + ":" + self.account_id \
                               + ":cluster:" + self.res_value['resource_id']
            elif self.res_value['resource_type'] == "AWS::Redshift::ClusterSnapshot":
                snap_response = client.describe_cluster_snapshots(
                    SnapshotIdentifier=self.res_value['resource_id'],
                )
                print(snap_response['Snapshots'][0]['ClusterIdentifier'])
                resource_arn = header + self.res_value['region'] + ":" + self.account_id \
                               + ":snapshot:" + snap_response['Snapshots'][0]['ClusterIdentifier'] + "/" + \
                               self.res_value['resource_id']
            elif self.res_value['resource_type'] == "AWS::Redshift::ClusterSubnetGroup":
                resource_arn = header + self.res_value['region'] + ":" + self.account_id \
                               + ":subnetgroup:" + self.res_value['resource_id']
            elif self.res_value['resource_type'] == "AWS::Redshift::ClusterParameterGroup":
                resource_arn = header + self.res_value['region'] + ":" + self.account_id \
                               + ":parametergroup:" + self.res_value['resource_id']

            elif self.res_value['resource_type'] == "AWS::Redshift::ClusterSecurityGroup":
                resource_arn = header + self.res_value['region'] + ":" + self.account_id \
                               + ":securitygroup:" + self.res_value['resource_id']
            else:
                print("Tagging not supported")
            return resource_arn
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
