import boto3
from datetime import datetime,timedelta
import pandas as pd
import xlsxwriter

def get_number_of_https_coount(metric,region,alb):
    try:
        end_time = datetime.now()
        start_time = end_time - timedelta(days=90)
        cw_client = boto3.client('cloudwatch', region_name=region)
        name = alb.split("/")[1]+"/"+alb.split("/")[2]+"/"+alb.split("/")[3]
        response = cw_client.get_metric_statistics(
            Namespace='AWS/ApplicationELB',
            MetricName=metric,
            Dimensions=[
                {'Name': 'LoadBalancer', 'Value': name}
            ],
            StartTime=start_time,
            EndTime=end_time,
            Period=86400, 
            Statistics=['Sum']
        )
        if response['Datapoints']:
            count = sum(datapoint['Sum'] for datapoint in response['Datapoints'])
        else:
            count = 0
        
        return count
    except Exception as ex:
        raise ex
    
def main():
    try:
        regions = ['us-east-1']
        http_data = []
        No_LB_data = []
        account_id = boto3.client('sts').get_caller_identity()['Account']
        for region in regions:
            lb_client = boto3.client('elbv2',region_name=region)
            lb_response = lb_client.describe_load_balancers()
            lb_list = lb_response['LoadBalancers']
            no_targets_lb = []
            other_lb = []
            while 'NextMarker' in lb_response.keys():
                lb_response = lb_client.describe_load_balancers(Marker=lb_response['NextMarker'])
                lb_list.extend(lb_response['LoadBalancers'])
            for lb in lb_list:
                if lb['Type'] in ['application']:
                    target_response = lb_client.describe_target_groups(LoadBalancerArn=lb['LoadBalancerArn'])
                    if len(target_response['TargetGroups']) == 0:
                        no_targets_lb.append(lb['LoadBalancerArn'])
                        tag_response = lb_client.describe_tags(ResourceArns=[lb['LoadBalancerArn']])
                        tag_dict = {tag['Key'] : tag['Value'] for tag in tag_response['TagDescriptions'][0]['Tags']}
                        productowner = tag_dict.get('ProductOwnerEmail','NA')
                        applicationID = tag_dict.get('ApplicationID','NA')
                        No_LB_data.append({"AccountID":account_id,"Region":region,"Loadbalancer":lb['LoadBalancerArn'],"Type":"application","ProductOwner":productowner,"ApplicationID":applicationID})
                    else:
                        other_lb.append(lb['LoadBalancerArn'])
            no_instance_elb = []
            elb_client = boto3.client('elb',region_name=region)
            elb_response = elb_client.describe_load_balancers()
            elb_list = elb_response['LoadBalancerDescriptions']
            other_elb = []
            while 'NextMarker' in elb_response.keys():
                elb_response = elb_client.describe_load_balancers(Marker=elb_response['NextMarker'])
                elb_list.extend(elb_response['LoadBalancerDescriptions'])
            for elb in elb_list:
                if 'Instances' in elb and len(elb['Instances']) == 0:
                    no_instance_elb.append(elb['LoadBalancerName'])
                    tag_response = elb_client.describe_tags(LoadBalancerNames=[elb['LoadBalancerName']])
                    tag_dict = {tag['Key'] : tag['Value'] for tag in tag_response['TagDescriptions'][0]['Tags']}
                    productowner = tag_dict.get('ProductOwnerEmail','NA')
                    applicationID = tag_dict.get('ApplicationID','NA')
                    No_LB_data.append({"AccountID":account_id,"Region":region,"Loadbalancer":elb['LoadBalancerName'],"Type":"classic","ProductOwner":productowner,"ApplicationID":applicationID})
                else:
                    other_elb.append(elb['LoadBalancerName'])
            metric_list = ['HTTPCode_ELB_4XX_Count','HTTPCode_ELB_5XX_Count','HTTPCode_ELB_504_Count','HTTPCode_Target_2XX_Count']
            for alb in other_lb:
                tag_response = lb_client.describe_tags(ResourceArns=[alb])
                tag_dict = {tag['Key'] : tag['Value'] for tag in tag_response['TagDescriptions'][0]['Tags']}
                productowner = tag_dict.get('ProductOwnerEmail','NA')
                applicationID = tag_dict.get('ApplicationID','NA')
                for metric in metric_list:
                    count = get_number_of_https_coount(metric,region,alb)
                    http_data.append({"Name":alb.split("/")[1]+"/"+alb.split("/")[2]+"/"+alb.split("/")[3],"AccountID":account_id,"Region":region,"LoadBalancer":alb,"Metric":metric,"Countin90Days":count,"ApplicationID":applicationID,"ProductOwner":productowner})
        https = pd.DataFrame(http_data)
        nolbdata = pd.DataFrame(No_LB_data)
        with pd.ExcelWriter('LoadbalancerDetails.xlsx', engine='xlsxwriter') as writer:
            https.to_excel(writer,sheet_name='HTTPSCodes',index=False)
            nolbdata.to_excel(writer,sheet_name='Notargets',index=False)
        return True
    except Exception as ex:
        raise ex
if __name__ == '__main__':
    main()
