import boto3
import datetime


class UpdateScoreindb():
    """
    # Class: UpdateScoreindb
    # Description: Updates CIS Report Score in Dynamo DB
    """

    def __init__(self, event, context):
        self.event = event
        self.context = context
        try:
            # get relevant input params from event
            session = boto3.Session()
            self.ssm_client = session.client('ssm')
            self.dd_client = session.client(
                'dynamodb', region_name="us-east-1")
            self.s3_client = session.client('s3', region_name="us-east-1")
            self.c_year = str(datetime.datetime.now().strftime('%Y'))
            self.c_month = str(datetime.datetime.now().strftime('%m'))
            self.c_day = str(datetime.datetime.now().strftime('%d'))
            self.ami_id = event['ami_id']
            self.ami_name = event['ami_name']
            self.instanceid = event['Instance_ID']
            self.score_table = 'CIS-Score-Report'
            print(self.c_year, self.c_month, self.c_day)

            self.s3_name = self.ssm_client.get_parameter(
                Name='platform_cis_ami_reports')
            self.s3_name = (self.s3_name['Parameter']['Value'])
            print(self.s3_name)
        except Exception as exception:
            print(exception)

    def UpdateScoreindb(self):
        """
        The following method is used to read the report file and updates the
        score in Dynamo DB.
        """
        try:
            if (self.ami_name == 'Windows_Server-2019-English-Full-Base*'):
                key = 'Windows-2019/' + str(self.c_year) + '/' + \
                    str(self.c_month) + '/' + str(self.c_day) + '/'
            elif self.ami_name == 'Windows_Server-2016-English-Full-Base*':
                key = 'Windows-2016/' + str(self.c_year) + '/' + \
                    str(self.c_month) + '/' + str(self.c_day) + '/'
            elif (self.ami_name == 'Windows_Server-2016-English-Full-ECS_Optimized-*'):
                key = 'Windows-2016-ECS/' + str(self.c_year) + \
                    '/' + str(self.c_month) + '/' + str(self.c_day) + '/'
            elif (self.ami_name == 'Windows_Server-2019-English-Full-ECS_Optimized-*'):
                key = 'Windows-2019-ECS/' + str(self.c_year) + '/' + \
                    str(self.c_month) + '/' + str(self.c_day) + '/'
            elif (self.ami_name == 'RHEL-7.7*'):
                key = 'RHEL7/' + str(self.c_year) + '/' + str(self.c_month) + \
                    '/' + str(self.c_day) + '/'
            elif (self.ami_name == 'RHEL-8*'):
                key = 'RHEL8/' + str(self.c_year) + '/' + str(self.c_month) + \
                    '/' + str(self.c_day) + '/'
            elif (self.ami_name == 'amzn2-ami-hvm*'):
                key = 'Amazon-linux2/' + str(self.c_year) + '/' + \
                    str(self.c_month) + '/' + str(self.c_day) + '/'
            elif (self.ami_name == 'amzn2-ami-ecs-hvm-*'):
                key = 'Amazon-linux2-ecs/' + str(self.c_year) + '/' + \
                    str(self.c_month) + '/' + str(self.c_day) + '/'
            elif (self.ami_name == 'amazon-eks-node-*'):
                key = 'Amazon-linux2-eks/' + str(self.c_year) + '/' + \
                    str(self.c_month) + '/' + str(self.c_day) + '/'
            elif (self.ami_name == 'ubuntu/images/hvm-ssd/ubuntu-bionic-*'):
                key = 'ubuntu18/' + str(self.c_year) + '/' + \
                    str(self.c_month) + '/' + str(self.c_day) + '/'
            else:
                print('Unknown AMI {}'.format(self.ami_name))

            bucketname = self.s3_name

            self.s3_response = self.s3_client.list_objects(
                Bucket=bucketname,
                Marker=key
            )
            
        except Exception as exception:
            self.reason_data = "DynamoDB details update failed  %s" % exception
            print("ERROR DynamoDB update", exception)
            return exception
            
    def db_update(self):
        res_dict = {}
        try:
            print("s3_response", self.s3_response['Name'])
            if 'Contents' in self.s3_response:
                file_key = self.s3_response['Contents'][0].get('Key')
                csvfile = self.s3_client.get_object(
                    Bucket=self.s3_response['Name'], Key=file_key)
                csvcontent = None
                csvcontent = str(csvfile['Body'].read()).split(',')
                check_score = any([x for x in csvcontent if 'Score' in x])
                if check_score == True:
                    score_value = [x for x in csvcontent if 'Score' in x]
                    cis_score = (score_value[0].split(
                        ':')[1].split('%')[0].strip())

                    response = self.dd_client.put_item(TableName=self.score_table,
                                                       Item={'AMI_ID': {"S": self.ami_id, },
                                                             'AMI_Name': {"S": self.ami_name, },
                                                             'CIS_Score': {"N": cis_score, },
                                                             'TimeStamp': {"S": str(
                                                                 datetime.datetime.now().strftime('%d-%m-%Y')), }
                                                             }
                                                       )
                    res_dict['ami_id'] = self.ami_id
                    res_dict['ami_name'] = self.ami_name
                    res_dict['Instance_ID'] = self.instanceid
                    res_dict['DB_Tablename'] = self.score_table
                    res_dict['Score'] = 'True'
                    return res_dict
                else:
                    res_dict['ami_id'] = self.ami_id
                    res_dict['ami_name'] = self.ami_name
                    res_dict['Instance_ID'] = self.instanceid
                    res_dict['DB_Tablename'] = self.score_table
                    res_dict['CIS-Report-File'] = 'True'
                    res_dict['Score'] = 'False'
                    return res_dict
            else:
                res_dict['ami_id'] = self.ami_id
                res_dict['ami_name'] = self.ami_name
                res_dict['Instance_ID'] = self.instanceid
                res_dict['DB_Tablename'] = self.score_table
                res_dict['CIS-Report-File'] = 'False'
                res_dict['Score'] = 'False'
                return res_dict
            
        except Exception as exception:
            return exception


def lambda_handler(event, context):
    """
    Lamda handler that calls the UpdateScoreindb function
    """
    try:
        result_value = {}
        result_value.update(event)
        print("Received an event {}".format(event))
        update_score = UpdateScoreindb(event, context)
        update_score.UpdateScoreindb()
        output_value = update_score.db_update()
        print("Output of the function : " + str(output_value))
        result_value.update(output_value)
        return result_value

    except Exception as exception:
        print("Error in Lambda Handler", exception)
        return exception