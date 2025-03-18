file_path = "C:\\Users\\Partha-Sarathi.Das\\OneDrive - Shell\\Documents\\AWS docs\\AWS-at-Shell-Platform-Engineering\\SharedServicesAccount\\resources-prod.json"


#master dict containing resource info
import json
import os
import subprocess
dict_resources = dict()
with open(file_path, 'r') as json_file:
    data = json.load(json_file)

# Access the dictionary and print its contents
print(data)
dict_resources = data
dev_varfile="dev.tfvars"
uat_varfile="uat.tfvars"
prod_varfile="prod.tfvars"


def terraform_init():
      try:
            cmd = 'terraform init'
            print("Command to be executed: ",cmd)
            output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, universal_newlines=True)
            print("Command output:")
            print(output)
      except subprocess.CalledProcessError as exception:
            print("Exception occurred while executing terraform init:\n", exception.output)

terraform_init()

def import_aws_vpc (tfvars_file, region, tf_resource_name, parametername):
    try:  
          cmd = 'terraform import -var-file="{}" "module.vpc-module-{}.aws_vpc.{}[0]" "{}"'.format(tfvars_file, region, tf_resource_name, parametername)
          print("Command to be executed: ",cmd)
          output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, universal_newlines=True)
          
          print("Command output:")
          print(output)

    except subprocess.CalledProcessError as exception:
        print("Exception occurred while importing AWS VPC:\n", exception.output)
    except Exception as exception:
            print("Exception occurred while importing AWS VPC {}".format(str(exception)))


tf_resource_name = ["shared_vpc"]
var = prod_varfile
for i in dict_resources["aws_vpc"]:
      tf_resource_name_current=tf_resource_name[0]
      resource = dict_resources["aws_vpc"][i][0]
      import_aws_vpc(var,i,tf_resource_name_current,resource)



#import_aws_subnet

def import_aws_subnet (tfvars_file, region, tf_resource_name, parametername):
    try:  
          cmd = 'terraform import -var-file="{}" "module.vpc-module-{}.aws_subnet.{}[0]" "{}"'.format(tfvars_file, region, tf_resource_name, parametername)
          print("Command to be executed: ",cmd)
          output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, universal_newlines=True)
          print("Command output:")
          print(output)
    except subprocess.CalledProcessError as exception:
        print("Exception occurred while importing AWS Subnet:\n", exception.output)
    except Exception as exception:
            print("Exception occurred while importing AWS Subnet {}".format(str(exception)))


tf_resource_name = ["subnet1a"]
var = prod_varfile
for i in dict_resources["aws_subnet"]:
      az=str(i)+'a'
      tf_resource_name_current=tf_resource_name[0]
      resource = dict_resources["aws_subnet"][i][az]
      import_aws_subnet(var,i,tf_resource_name_current,resource)

tf_resource_name = ["subnet1b"]
var = prod_varfile
for i in dict_resources["aws_subnet"]:
      az=str(i)+'b'
      tf_resource_name_current=tf_resource_name[0]
      resource = dict_resources["aws_subnet"][i][az]
      import_aws_subnet(var,i,tf_resource_name_current,resource)




#import_aws_avm_iam_policies

def import_aws_avm_iam_policies (tfvars_file, tf_resource_name, parametername):
    try:  
          cmd = 'terraform import -var-file="{}" "module.iam-module.aws_iam_policy.{}" "{}"'.format(tfvars_file, tf_resource_name, parametername)
          print("Command to be executed: ",cmd)
          output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, universal_newlines=True)
          print("Command output:")
          print(output)

    except subprocess.CalledProcessError as exception:
        print("Exception occurred while importing AVM IAM Policies:\n", exception.output)
    except Exception as exception:
            print("Exception occurred while importing AVM IAM Policies {}".format(str(exception)))


# call import_aws_avm_iam_policies (tfvars_file, tf_resource_name, parametername)
var = dev_varfile
for i in dict_resources["aws_iam_policy"]:
      tf_resource_name_current=i
      parametername=dict_resources["aws_iam_policy"][i]
      import_aws_avm_iam_policies(var,tf_resource_name_current,parametername)


# call import_aws_avm_iam_roles (tfvars_file, tf_resource_name, parametername)

def import_aws_avm_iam_roles (tfvars_file, tf_resource_name, parametername):
    try:  
          cmd = 'terraform import -var-file="{}" "module.iam-module.aws_iam_role.{}" "{}"'.format(tfvars_file, tf_resource_name, parametername)
          print("Command to be executed: ",cmd)
          output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, universal_newlines=True)
          print("Command output:")
          print(output)

    except subprocess.CalledProcessError as exception:
        print("Exception occurred while importing AVM IAM Roles:\n", exception.output)
    except Exception as exception:
            print("Exception occurred while importing AVM IAM Roles {}".format(str(exception)))



var = dev_varfile
for i in dict_resources["aws_iam_role"]:
      tf_resource_name_current=i
      parametername= dict_resources["aws_iam_role"][i]
      import_aws_avm_iam_roles(var,tf_resource_name_current,parametername)

#call import_aws_avm_iam_instance_profile_roles (tfvars_file, region, tf_resource_name, parametername):
def import_aws_avm_iam_instance_profile_roles (tfvars_file, tf_resource_name, parametername):
    try:  
          cmd = 'terraform import -var-file="{}" "module.iam-module.aws_iam_instance_profile.{}" {}'.format(tfvars_file, tf_resource_name, parametername)
          print("Command to be executed: ",cmd)
          output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, universal_newlines=True)
          print("Command output:")
          print(output)

    except subprocess.CalledProcessError as exception:
        print("Exception occurred while importing AVM IAM Instance Profile Roles:\n", exception.output)
    except Exception as exception:
            print("Exception occurred while importing AVM IAM Instance Profile Roles {}".format(str(exception)))


tf_resource_name = "platform_ServiceNow_ITOM_Discovery_Child_InstanceProfile"
var = dev_varfile
resource = dict_resources["aws_iam_instance_profile"]
import_aws_avm_iam_instance_profile_roles(var,tf_resource_name,resource)
      

# call import_aws_security_group (tfvars_file, region, tf_resource_name, parametername)

def import_aws_security_group (tfvars_file, region, tf_resource_name, parametername):
    try:  
          cmd = 'terraform import -var-file="{}" "module.sg-module-{}.aws_security_group.{}[0]" "{}"'.format(tfvars_file, region, tf_resource_name, parametername)
          print("Command to be executed: ",cmd)
          output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, universal_newlines=True)
          print("Command output:")
          print(output)
    except subprocess.CalledProcessError as exception:
        print("Exception occurred while importing AWS Security Group:\n", exception.output)
    except Exception as exception:
            print("Exception occurred while importing AWS Security Group {}".format(str(exception)))

tf_resource_name = ["sharedvpcsecgroup"]
var = prod_varfile
for i in dict_resources["aws_security_group"]:
      tf_resource_name_current=tf_resource_name[0]
      resource = dict_resources["aws_security_group"][i][0]
      import_aws_security_group(var,i,tf_resource_name_current,resource)


# call import_aws_route53_resolver_endpoint(tfvars_file, region, tf_resource_name, parametername)
def import_aws_route53_resolver_endpoint (tfvars_file, region, tf_resource_name, parametername):
    try:  
          cmd = 'terraform import -var-file="{}" "module.route53-module-{}.aws_route53_resolver_endpoint.{}" "{}"'.format(tfvars_file, region, tf_resource_name, parametername)
          print("Command to be executed: ",cmd)
          output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, universal_newlines=True)
          print("Command output:")
          print(output)

    except subprocess.CalledProcessError as exception:
        print("Exception occurred while importing Route53 Resolver Endpoint:\n", exception.output)
    except Exception as exception:
            print("Exception occurred while importing Route53 Resolver Endpoint {}".format(str(exception)))

tf_resource_name = ["shell_domain_resolver"]
var = prod_varfile
for i in dict_resources["aws_route53_resolver_endpoint"]:
      tf_resource_name_current=tf_resource_name[0]
      resource = dict_resources["aws_route53_resolver_endpoint"][i][0]
      import_aws_route53_resolver_endpoint(var,i,tf_resource_name_current,resource)

# call import_aws_route53_resolver_rule(tfvars_file, region, tf_resource_name, parametername)

def import_aws_route53_resolver_rule (tfvars_file, region, tf_resource_name, parametername):
    try:  
          cmd = 'terraform import -var-file="{}" "module.route53-module-{}.aws_route53_resolver_rule.{}" "{}"'.format(tfvars_file, region, tf_resource_name, parametername)
          print("Command to be executed: ",cmd)
          output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, universal_newlines=True)
          print("Command output:")
          print(output)
    except subprocess.CalledProcessError as exception:
        print("Exception occurred while importing Route53 Resolver Rule:\n", exception.output)
    except Exception as exception:
            print("Exception occurred while importing Route53 Resolver Rule {}".format(str(exception)))

tf_resource_name = ["shell_domain_forwarder_rule"]
var = prod_varfile
for i in dict_resources["aws_route53_resolver_rule"]:
      tf_resource_name_current=tf_resource_name[0]
      resource = dict_resources["aws_route53_resolver_rule"][i][0]
      import_aws_route53_resolver_rule(var,i,tf_resource_name_current,resource)

# call import_aws_route53_resolver_rule_association(tfvars_file, region, tf_resource_name, parametername)

def import_aws_route53_resolver_rule_association (tfvars_file, region, tf_resource_name, parametername):
    try:  
          cmd = 'terraform import -var-file="{}" "module.route53-module-{}.aws_route53_resolver_rule_association.{}" "{}"'.format(tfvars_file, region, tf_resource_name, parametername)
          print("Command to be executed: ",cmd)
          output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, universal_newlines=True)
          print("Command output:")
          print(output)
    except subprocess.CalledProcessError as exception:
        print("Exception occurred while importing Route53 RR Association:\n", exception.output)
    except Exception as exception:
            print("Exception occurred while importing Route53 RR Association {}".format(str(exception)))

tf_resource_name = ["shell_domain_forwarder_rule_association"]
var = prod_varfile
for i in dict_resources["aws_route53_resolver_rule_association"]:
      tf_resource_name_current=tf_resource_name[0]
      resource = dict_resources["aws_route53_resolver_rule_association"][i]
      import_aws_route53_resolver_rule_association(var,i,tf_resource_name_current,resource)

# call import_aws_ram_resource_share(tfvars_file, region, tf_resource_name, parametername)

def import_aws_ram_resource_share (tfvars_file, region, tf_resource_name, parametername):
    try:  
          cmd = 'terraform import -var-file="{}" "module.route53-module-{}.aws_ram_resource_share.{}" "{}"'.format(tfvars_file, region, tf_resource_name, parametername)
          print("Command to be executed: ",cmd)
          output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, universal_newlines=True)
          print("Command output:")
          print(output)
    except subprocess.CalledProcessError as exception:
        print("Exception occurred while importing RAM ResourceShare:\n", exception.output)
    except Exception as exception:
            print("Exception occurred while importing RAM ResourceShare {}".format(str(exception)))

tf_resource_name = ["shell_domain_resolver_share"]
var = prod_varfile
for i in dict_resources["aws_ram_resource_share"]:
      tf_resource_name_current=tf_resource_name[0]
      resource = dict_resources["aws_ram_resource_share"][i][0]
      import_aws_ram_resource_share(var,i,tf_resource_name_current,resource)

# call import_aws_ram_principal_association(tfvars_file, region, tf_resource_name, parametername)

def import_aws_ram_principal_association (tfvars_file, region, tf_resource_name, parameter1, parameter2):
    try:  
          cmd = 'terraform import -var-file="{}" \"module.route53-module-{}.aws_ram_principal_association.this["""{}"""]\" "{}","{}"'.format(tfvars_file, region, tf_resource_name, parameter1, parameter2)
          print("Command to be executed: ",cmd)
          output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, universal_newlines=True)
          print("Command output:")
          print(output)
    except subprocess.CalledProcessError as exception:
        print("Exception occurred while importing RAM principal association:\n", exception.output)
    except Exception as exception:
            print("Exception occurred while importing RAM principal association {}".format(str(exception)))


var = prod_varfile
for i in dict_resources["aws_ram_principal_association"]:
      for y in dict_resources["aws_ram_principal_association"][i]:
              tf_resource_name_current = y[0]
              parameter1= y[2]
              parameter2= y[1]
              import_aws_ram_principal_association(var,i,tf_resource_name_current,parameter1,parameter2)


#import_aws_vpc_endpoint, aws_route53_zone, 

def import_aws_vpc_endpoint (tfvars_file, region, tf_resource_name, parametername):
    try:  
          cmd = 'terraform import -var-file="{}" \"module.vpcendpoint-module-{}.aws_vpc_endpoint.this["""{}"""]\" "{}"'.format(tfvars_file, region, tf_resource_name, parametername)
          print("Command to be executed: ",cmd)
          output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, universal_newlines=True)
          print("Command output:")
          print(output)
    except subprocess.CalledProcessError as exception:
        print("Exception occurred while importing AWS VPC Endpoint:\n", exception.output)
    except Exception as exception:
            print("Exception occurred while importing AWS VPC Endpoint {}".format(str(exception)))

var = prod_varfile
for i in dict_resources["aws_vpc_endpoint"]:
      for j in dict_resources["aws_vpc_endpoint"][i]:
            tf_resource_name_current=j
            resource=dict_resources["aws_vpc_endpoint"][i][j]
            import_aws_vpc_endpoint(var,i,tf_resource_name_current,resource)

def import_aws_route53_zone (tfvars_file, region, tf_resource_name, parametername):
    try:  
          cmd = 'terraform import -var-file="{}" \"module.vpcendpoint-module-{}.aws_route53_zone.this["""{}"""]\" "{}"'.format(tfvars_file, region, tf_resource_name, parametername)
          print("Command to be executed: ",cmd)
          output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, universal_newlines=True)
          print("Command output:")
          print(output)
    except subprocess.CalledProcessError as exception:
        print("Exception occurred while importing AWS Route53 HostedZone:\n", exception.output)
    except Exception as exception:
            print("Exception occurred while importing AWS Route53 HostedZone {}".format(str(exception)))

def import_aws_route53_record (tfvars_file, region, tf_resource_name, parametername):
    try:  
          cmd = 'terraform import -var-file="{}" \"module.vpcendpoint-module-{}.aws_route53_record.this["""{}"""]\" "{}"'.format(tfvars_file, region, tf_resource_name, parametername)
          print("Command to be executed: ",cmd)
          output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, universal_newlines=True)
          print("Command output:")
          print(output)
    except subprocess.CalledProcessError as exception:
        print("Exception occurred while importing AWS Route53 HostedRecord:\n", exception.output)
    except Exception as exception:
            print("Exception occurred while importing AWS Route53 HostedRecord {}".format(str(exception)))


var = prod_varfile
for i in dict_resources["aws_route53_zone"]:
      for j in dict_resources["aws_route53_zone"][i]:
            if j=="ecs-telemetry-Endpoint" or j=="ecs-agent-Endpoint":
                  tf_resource_name_current=j
                  hostedzone_resource=dict_resources["aws_route53_zone"][i][j][0]
                  import_aws_route53_zone(var,i,tf_resource_name_current,hostedzone_resource)



i="ap-southeast-1"
for j in dict_resources["aws_route53_zone"][i]:
            tf_resource_name_current=j
            hostedzone_resource=dict_resources["aws_route53_zone"][i][j][0]
            import_aws_route53_zone(var,i,tf_resource_name_current,hostedzone_resource)

for j in dict_resources["aws_route53_zone"][i]:
            tf_resource_name_current=j
            hostedzone_resource=dict_resources["aws_route53_zone"][i][j][1]
            import_aws_route53_record(var,i,tf_resource_name_current,hostedzone_resource)

var = prod_varfile
for i in dict_resources["aws_route53_zone"]:
      for j in dict_resources["aws_route53_zone"][i]:
            if j=="ecs-telemetry-Endpoint" or j=="ecs-agent-Endpoint":
                  tf_resource_name_current=j
                  hostedzone_resource=dict_resources["aws_route53_zone"][i][j][1]
                  import_aws_route53_record(var,i,tf_resource_name_current,hostedzone_resource)

def import_aws_avm_vpc_flowlogs_creation (tfvars_file, region, tf_resource_name, parametername):
    try:  
          cmd = 'terraform import -var-file="{}" \"module.vpc-module-{}.aws_flow_log.{}\" "{}"'.format(tfvars_file, region, tf_resource_name, parametername)
          print("Command to be executed: ",cmd)
          output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, universal_newlines=True)
          print("Command output:")
          print(output)
    except subprocess.CalledProcessError as exception:
        print("Exception occurred while importing VPC flow log creation:\n", exception.output)
    except Exception as exception:
        print("Exception occurred while importing VPC flow log creation:\n", str(exception))

tf_resource_name = ["enable_vpc_flowlogs"]
var = prod_varfile
for i in dict_resources["aws_flow_log"]:
      tf_resource_name_current=tf_resource_name[0]
      resource = dict_resources["aws_flow_log"][i]
      import_aws_avm_vpc_flowlogs_creation(var,i,tf_resource_name_current,resource)

         
#import ECRDockerWildCard-HostedRecord
#only for UAT AND PROD env

def import_aws_route53_ECRDockerWildCard_hostedrecord (tfvars_file, region, parametername):
      try:  
          cmd = 'terraform import -var-file="{}" \"module.vpcendpoint-module-{}.aws_route53_record.ECRDockerWildCard-HostedRecord[0]" "{}"'.format(tfvars_file, region, parametername)
          print("Command to be executed: ",cmd)
          output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, universal_newlines=True)
          print("Command output:")
          print(output)
      except subprocess.CalledProcessError as exception:
        print("Exception occurred while importing AWS Route53 HostedRecord:\n", exception.output)
      except Exception as exception:
            print("Exception occurred while importing AWS Route53 HostedRecord {}".format(str(exception)))

var = prod_varfile
for i in dict_resources["aws_route53_zone"]:
      for j in dict_resources["aws_route53_zone"][i]:
            if j == "ECRDocker-Endpoint":
                  hostedzone_resource=dict_resources["aws_route53_zone"][i][j][2]
                  print(hostedzone_resource)
                  import_aws_route53_ECRDockerWildCard_hostedrecord(var,i,hostedzone_resource)              