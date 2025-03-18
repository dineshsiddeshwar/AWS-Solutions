def aws_check_if_vpc_endpoint_exists(ec2_client, region, servicename):
    try:
        name="com.amazonaws.{}.{}".format(region, servicename)
        vpce_response = ec2_client.describe_vpc_endpoints(
            Filters=[
                {
                    'Name': 'service-name',
                    'Values': [name]
                }
            ]
        )
        if len(vpce_response['VpcEndpoints']) > 0:
            print("VPC Endpoint found, id is {}".format(vpce_response['VpcEndpoints'][0]['VpcEndpointId']))
            return True
        else:
            print("VPC Endpoint with servicename <{}> not found".format(name))
            return False
    except Exception as e:
        print("Error occurred while aws_check_if_vpc_endpoint_exists and error is {}".format(e))
        return False

def aws_check_if_hosted_zone_exists(r53_client,servicename,region):
    # hostedzone_ids = {"us-east-1": {}, "eu-west-1": {}, "ap-southeast-1" : {} }
    try:
        response = r53_client.list_hosted_zones_by_name()
        hostedzones_all=[]
        hostedzones = response['HostedZones']
        hostedzones_all.extend(hostedzones)
        while response['IsTruncated']:
            response = r53_client.list_hosted_zones_by_name(DNSName=response['NextDNSName'], HostedZoneId=response['NextHostedZoneId'])
            hostedzones = response['HostedZones']
            hostedzones_all.extend(hostedzones)
        searchstring="{}.{}.".format(servicename,region)
        for h in hostedzones_all:
            if searchstring in h['Name']:
                print("Hosted Zone found, id is {}".format(h['Id']))
                print("Hosted Zone name is {}".format(h['Name']))
                recordsets=r53_client.list_resource_record_sets(HostedZoneId=h['Id'])['ResourceRecordSets']
                for r in recordsets:
                    if r['Type']=='A':
                        r_name = r['Name']
                        if searchstring in r_name:
                            print("RecordSet found, name is {}".format(r_name))
                            return True
                        else:
                            print("RecordSet with name <{}> not found".format(searchstring))
                            return False
                    else:
                        print("A record containing <{}> not found".format(searchstring))
                        return False
            
        print("Hosted Zone containing <{}> not found".format(searchstring))
        return False
    except Exception as e:
        print("Error occurred while aws_check_if_hosted_zone_exists and error is {}".format(e))
        return False