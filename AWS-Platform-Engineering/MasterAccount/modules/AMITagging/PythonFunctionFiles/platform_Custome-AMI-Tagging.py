import boto3


class CustomAMI(object):
    """Class to tag ami created by user"""

    def __init__(self, event, context):
        session = boto3.session.Session()
        self.ec2_client = session.client('ec2')
        ssm_client = session.client('ssm')
        ssm_store = ssm_client.get_parameter(Name='ami_tags')
        self.ssm_store = (ssm_store['Parameter']['Value']).split(',')

    def tag_resources(self,event):
        """function to tag resources"""
        for snapshot in event['resources']:
            snap_name = (snapshot.split('/'))[1]
            print(snap_name)
            response = self.ec2_client.describe_snapshots(SnapshotIds=[snap_name])
            print(response)
            for snapshot in response['Snapshots']:
                print(snapshot['Description'])
                vsnapshot = snapshot['SnapshotId']
                desc = snapshot['Description']
                desc_list = desc.split(" ")
                print(">>>>>>" + str(desc_list))
                for word in desc_list:
                    if word.startswith('ami-'):
                        self.tag_ami(word)
                    else:
                        tag_resource = self.ec2_client.create_tags(Resources=[str(vsnapshot)],
                            Tags=[{'Key': self.ssm_store[0], 'Value': self.ssm_store[1]}])

    def tag_ami(self,word):
        """Tag the ami"""
        resource_list = []
        print("AMI Id is", word)
        resource_list.append(word)
        ami_id = word
        print(ami_id)
        res = self.ec2_client.describe_images(ImageIds=[str(resource_list[0])])
        print(res)
        image_list = res['Images']
        for item in image_list:
            for k in item['BlockDeviceMappings']:
                print(type(k))
                snap_list = k['Ebs']['SnapshotId']
                resource_list.append(snap_list)
        print(resource_list)
        for item in resource_list:
            tag_resource = self.ec2_client.create_tags(Resources=[str(item)],
                                                       Tags=[{'Key': self.ssm_store[0], 'Value': self.ssm_store[1]}])
def lambda_handler(event, context):
    """Main function"""
    try:
        result_values = {}
        result_values.update(event)
        print("Event {}".format(event))
        custom_ami_object = CustomAMI(event, context)
        custom_ami_object.tag_resources(event)
        return result_values
    except Exception as exception:
        print("Exception in Lambda Handler", exception)
        event['Cloudwatch_association_creation'] = "FAILED"
        return event