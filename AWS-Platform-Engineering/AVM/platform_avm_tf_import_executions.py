import json

with open("parameters.json") as json_data:
    parameters_data = json.load(json_data)
    #print(parameters_data)

def update_vpc_file(main_file,resource,module_name, resource_name, resource_id,region):
    with open(main_file,'a') as new_file:
        new_file.seek(0,1)
        new_file.write("\n")
        new_file.write("\nimport {")
        new_file.write("\n  to = module."+module_name+"."+resource+"."+resource_name+"["+'"'+region+'"'+"]")
        new_file.write("\n  id = "+'"'+resource_id+'"')
        new_file.write("\n}")
        new_file.write("\n")
        new_file.close()

def update_vpc_route53_file(main_file,resource,module_name, resource_name, resource_id,value2):
    value = value2.split(':')
    with open(main_file,'a') as new_file:
        new_file.seek(0,1)
        new_file.write("\n")
        new_file.write("\nimport {")
        new_file.write("\n  to = module."+module_name+"."+resource+"."+resource_name+"["+'"'+value[0]+'"'+"]")
        new_file.write("\n  id = "+'"'+resource_id+'"')
        new_file.write("\n}")
        new_file.write("\n")
        new_file.close()

def update_file(main_file,resource,module_name, resource_name, resource_id):
    with open(main_file,'a') as new_file:
        new_file.seek(0,1)
        new_file.write("\n")
        new_file.write("\nimport {")
        new_file.write("\n  to = module."+module_name+"."+resource+"."+resource_name)
        new_file.write("\n  id = "+'"'+resource_id+'"')
        new_file.write("\n}")
        new_file.write("\n")
        new_file.close()

def update_file_with_index(main_file,resource,module_name, resource_name, resource_id):
    with open(main_file,'a') as new_file:
        new_file.seek(0,1)
        new_file.write("\n")
        new_file.write("\nimport {")
        new_file.write("\n  to = module."+module_name+"."+resource+"."+resource_name+"[0]")
        new_file.write("\n  id = "+'"'+resource_id+'"')
        new_file.write("\n}")
        new_file.write("\n")
        new_file.close()

for region,data in parameters_data['tf_import'].items():
    print("Importing resources in {}".format(region))  

    for key,value in data['Access_Analyzer'].items():
        for key1,value1 in value.items():
            try:
                update_file("accessanalyzer_main.tf","aws_accessanalyzer_analyzer",key, key1, value1)
            except Exception as exception:
                print(exception)

    try:
        if data['EBSEncryption']:
            for key,value in data['EBSEncryption'].items(): 
                for key1,value1 in value.items():
                    try:
                        update_file_with_index("ebsencryption_main.tf","aws_ebs_encryption_by_default",key, key1, value1)
                    except Exception as exception:
                        print(exception)
    except Exception as exception:
        print("No EBSEncryption : {} ".format(exception))

    try:
        if data['BackupVault']:
            for key,value in data['BackupVault'].items():
                for key1,value1 in value.items():
                    try:
                        update_file_with_index("backup_main.tf","aws_backup_vault",key, key1, value1)
                    except Exception as exception:
                        print(exception)
    except Exception as exception:
        print("No BackupVault : {} ".format(exception))

    try:
        if data['BackupVaultNotifications']:
            for key,value in data['BackupVaultNotifications'].items():
                for key1,value1 in value.items():
                    try:
                        update_file_with_index("backup_main.tf","aws_backup_vault_notifications",key, key1, value1)
                    except Exception as exception:
                        print(exception)
    except Exception as exception:
        print("No BackupVaultNotifications : {} ".format(exception))

    try:
        if data['SNSTopic']:
            for key,value in data['SNSTopic'].items(): 
                for key1,value1 in value.items():
                    try:
                        update_file_with_index("backup_main.tf","aws_sns_topic",key, key1, value1)
                    except Exception as exception:
                        print(exception)
    except Exception as exception:
        print("No SNSTopic : {} ".format(exception))

    try:
        if data['SNSTopicSubscription']:
            for key,value in data['SNSTopicSubscription'].items(): 
                for key1,value1 in value.items():
                    try:
                        update_file_with_index("backup_main.tf","aws_sns_topic_subscription",key, key1, value1)
                    except Exception as exception:
                        print(exception)
    except Exception as exception:
        print("No SNSTopicSubscription : {} ".format(exception))

    try:
        if data['Config']:                        
            for key,value in data['Config'].items(): 
                for key1,value1 in value.items():
                    try:
                        update_file_with_index("config_main.tf","aws_config_config_rule",key, key1, value1)
                    except Exception as exception:
                        print(exception)
    except Exception as exception:
        print("No Config : {} ".format(exception))

    try:
        if data['EMRBlockPublicAccess']:   
            for key,value in data['EMRBlockPublicAccess'].items(): 
                for key1,value1 in value.items():
                    try:
                        update_file_with_index("emrblockpublicaccess_main.tf", "aws_emr_block_public_access_configuration",key, key1, value1)
                    except Exception as exception:
                        print(exception)
    except Exception as exception:
        print("No EMRBlockPublicAccess : {} ".format(exception))
    
    try:
        if data['SecurityHubCustomInsights']:
            for key,value in data['SecurityHubCustomInsights'].items(): 
                for key1,value1 in value.items():
                    try:
                        update_file("securityhub_main.tf","aws_securityhub_insight",key, key1, value1)
                    except Exception as exception:
                        print(exception)
    except Exception as exception:
        print("No SecurityHubCustomInsights : {} ".format(exception))

    try:
        if data['SSMAssociations']:
            for key,value in data['SSMAssociations'].items(): 
                for key1,value1 in value.items():
                    try:
                        update_file_with_index("ssm_main.tf","aws_ssm_association",key, key1, value1)
                    except Exception as exception:
                        print(exception)
    except Exception as exception:
        print("No SSMAssociations : {} ".format(exception))    

    try:
        if data['SSMDocuments']:
            for key,value in data['SSMDocuments'].items(): 
                for key1,value1 in value.items():
                    try:
                        update_file_with_index("ssm_main.tf","aws_ssm_document",key, key1, value1)
                    except Exception as exception:
                        print(exception)
    except Exception as exception:
        print("No SSMDocuments : {} ".format(exception))  

    try:
        if data['SSMParameters']:
            for key,value in data['SSMParameters'].items():
                for key1,value1 in value.items():
                    try:
                        if type(value1) is list:
                            for value2 in value1:
                                with open("ssm_main.tf",'a') as new_file:
                                    new_file.seek(0,1)
                                    new_file.write("\n")
                                    new_file.write("\nimport {")
                                    new_file.write("\n  to = module."+key+".aws_ssm_parameter."+key1+"["+'"'+value2+'"'+"]")
                                    new_file.write("\n  id = "+'"/Platform-Tag/'+value2+'"')
                                    new_file.write("\n}")
                                    new_file.write("\n")
                                    new_file.close()
                        elif key1 == "create_account_level_ssm_parameters_backup":
                            with open("ssm_main.tf",'a') as new_file:
                                new_file.seek(0,1)
                                new_file.write("\n")
                                new_file.write("\nimport {")
                                new_file.write("\n  to = module."+key+".aws_ssm_parameter."+key1)
                                new_file.write("\n  id = "+'"'+value1+'"')
                                new_file.write("\n}")
                                new_file.write("\n")
                                new_file.close()                       
                    except Exception as exception:
                        print(exception)   
    except Exception as exception:
        print("No SSMParameters : {} ".format(exception))

    try:
        if data['VPC']:
            for key,value in data['VPC'].items(): 
                for key1,value1 in value.items():
                    try:
                        update_vpc_file("vpc_main.tf","aws_vpc", key, key1, value1,region)
                    except Exception as exception:
                        print(exception) 
    except Exception as exception:
        print("No VPC : {} ".format(exception))

    try:
        if data['Subnets']:
            for key,value in data['Subnets'].items(): 
                for key1,value1 in value.items():
                    try:
                        update_vpc_file("vpc_main.tf","aws_subnet", key, key1, value1,region)
                    except Exception as exception:
                        print(exception) 
    except Exception as exception:
        print("No Subnets : {} ".format(exception))
    
    try:
        if data['VPCFlowLogs']:
            for key,value in data['VPCFlowLogs'].items(): 
                for key1,value1 in value.items():
                    try:
                        update_vpc_file("vpc_main.tf", "aws_flow_log", key, key1, value1,region)
                    except Exception as exception:
                        print(exception) 
    except Exception as exception:
        print("No VPCFlowLogs : {} ".format(exception))

    try:
        if data['VPCEndpoints']:
            for key,value in data['VPCEndpoints'].items(): 
                for key1,value1 in value.items():
                    try:
                        update_vpc_file("vpc_main.tf","aws_vpc_endpoint", key, key1, value1,region)
                    except Exception as exception:
                        print(exception) 
    except Exception as exception:
        print("No VPCEndpoints : {} ".format(exception))

    try:
        if data['VPCAssociationAuthorization']:
            for key,value in data['VPCAssociationAuthorization'].items(): 
                for key1,value1 in value.items():
                    for value2 in value1:
                        try:
                            update_vpc_route53_file("vpc_main.tf","aws_route53_vpc_association_authorization", key, key1, value2,value2)
                        except Exception as exception:
                            print(exception) 
    except Exception as exception:
        print("No VPCAssociationAuthorization : {} ".format(exception))
    
    try:
        if data['VPCRoute53ZoneAssociation']:
            for key,value in data['VPCRoute53ZoneAssociation'].items(): 
                for key1,value1 in value.items():
                    for value2 in value1:
                        try:
                            update_vpc_route53_file("vpc_main.tf","aws_route53_zone_association", key, key1, value2,value2)
                        except Exception as exception:
                            print(exception)
    except Exception as exception:
        print("No VPCRoute53ZoneAssociation : {} ".format(exception))

    try:
        if data['ResolverRuleAssociation']:
            for key,value in data['ResolverRuleAssociation'].items(): 
                for key1,value1 in value.items():
                    try:
                        update_vpc_file("vpc_main.tf","aws_route53_resolver_rule_association", key, key1, value1,region)
                    except Exception as exception:
                        print(exception) 
    except Exception as exception:
        print("No ResolverRuleAssociation : {} ".format(exception))


    if region == "us-east-1":
        try:
            if data['SSMParameters']:
                for key,value in data['SSMParameters'].items():
                    for key1,value1 in value.items():
                        try:
                            if type(value1) is list:
                                pass
                            elif key1 == "create_account_level_ssm_parameters_backup":
                                pass                             
                            else:
                                with open("ssm_main.tf",'a') as new_file:
                                    new_file.seek(0,1)
                                    new_file.write("\n")
                                    new_file.write("\nimport {")
                                    new_file.write("\n  to = module."+key+".aws_ssm_parameter."+key1+'[0]')
                                    new_file.write("\n  id = "+'"'+value1+'"')
                                    new_file.write("\n}")
                                    new_file.write("\n")
                                    new_file.close()                   
                        except Exception as exception:
                            print(exception)   
        except Exception as exception:
            print("No SSMParameters : {} ".format(exception))

        try:
            if data['Budget']:
                for key,value in data['Budget'].items(): 
                    for key1,value1 in value.items():
                        try:
                            update_file("budget_main.tf","aws_budgets_budget",key, key1, value1)
                        except Exception as exception:
                            print(exception)
        except Exception as exception:
            print("No Budget : {} ".format(exception))

        try:
            if data['IAMRoles']:
                for key,value in data['IAMRoles'].items(): 
                    for key1,value1 in value.items():
                        try:
                            update_file("iam_main.tf","aws_iam_role",key, key1, value1)
                        except Exception as exception:
                            print(exception) 
        except Exception as exception:
            print("No IAMRoles : {} ".format(exception))

        try:
            if data['IAMInstanceProfile']:         
                for key,value in data['IAMInstanceProfile'].items(): 
                    for key1,value1 in value.items():
                        try:
                            update_file("iam_main.tf","aws_iam_instance_profile",key, key1, value1)
                        except Exception as exception:
                            print(exception) 
        except Exception as exception:
            print("No IAMInstanceProfile : {} ".format(exception))

        try:
            if data['IAMPolicies']:       
                for key,value in data['IAMPolicies'].items(): 
                    for key1,value1 in value.items():
                        try:
                            update_file("iam_main.tf","aws_iam_policy",key, key1, value1)
                        except Exception as exception:
                            print(exception) 
        except Exception as exception:
            print("No IAMPolicies : {} ".format(exception))

        try:
            if data['S3BlockPublicAccess']:         
                for key,value in data['S3BlockPublicAccess'].items(): 
                    for key1,value1 in value.items():
                        try:
                            update_file("s3blockpublicaccess_main.tf","aws_s3_account_public_access_block",key, key1, value1)
                        except Exception as exception:
                            print(exception) 
        except Exception as exception:
            print("No S3BlockPublicAccess : {} ".format(exception))

        try:
            if data['SSO']:
                for key,value in data['SSO'].items(): 
                    for key1,value1 in value.items():
                        try:
                            update_file("sso_main.tf","aws_ssoadmin_account_assignment",key, key1, value1)
                        except Exception as exception:
                            print(exception) 
        except Exception as exception:
            print("No SSO : {} ".format(exception))

        if parameters_data['VPC_cidr_extend_number_US'] != 0 :

            try:
                if data['VPCExtension1']:
                    for key,value in data['VPCExtension1'].items(): 
                        for key1,value1 in value.items():
                            try:
                                update_vpc_file("vpc_main.tf","aws_vpc_ipv4_cidr_block_association", key, key1, value1,region)
                            except Exception as exception:
                                print(exception) 
            except Exception as exception:
                print("No VPCExtension1 : {} ".format(exception))

            try:
                if data['VPCExtensionSubnets1']:
                    for key,value in data['VPCExtensionSubnets1'].items(): 
                        for key1,value1 in value.items():
                            try:
                                update_vpc_file("vpc_main.tf","aws_subnet", key, key1, value1,region)
                            except Exception as exception:
                                print(exception) 
            except Exception as exception:
                print("No VPCExtensionSubnets1 : {} ".format(exception))

            try:
                if data['VPCExtension2']:
                    for key,value in data['VPCExtension2'].items(): 
                        for key1,value1 in value.items():
                            try:
                                update_vpc_file("vpc_main.tf","aws_vpc_ipv4_cidr_block_association", key, key1, value1,region)
                            except Exception as exception:
                                print(exception)
            except Exception as exception:
                print("No VPCExtension2 : {} ".format(exception))

            try:
                if data['VPCExtensionSubnets2']:
                    for key,value in data['VPCExtensionSubnets2'].items(): 
                        for key1,value1 in value.items():
                            try:
                                update_vpc_file("vpc_main.tf","aws_subnet", key, key1, value1,region)
                            except Exception as exception:
                                print(exception) 
            except Exception as exception:
                print("No VPCExtensionSubnets2 : {} ".format(exception))

            try:
                if data['VPCExtension3']:
                    for key,value in data['VPCExtension3'].items(): 
                        for key1,value1 in value.items():
                            try:
                                update_vpc_file("vpc_main.tf","aws_vpc_ipv4_cidr_block_association", key, key1, value1,region)
                            except Exception as exception:
                                print(exception)
            except Exception as exception:
                print("No VPCExtension3 : {} ".format(exception))
    
            try:
                if data['VPCExtensionSubnets3']:
                    for key,value in data['VPCExtensionSubnets3'].items(): 
                        for key1,value1 in value.items():
                            try:
                                update_vpc_file("vpc_main.tf","aws_subnet", key, key1, value1,region)
                            except Exception as exception:
                                print(exception) 
            except Exception as exception:
                print("No VPCExtensionSubnets3 : {} ".format(exception))
            
        if parameters_data['Non_routable_requested_US'] == "Yes":

            try:
                if data['NonRoutableVPCExtension']:
                    for key,value in data['NonRoutableVPCExtension'].items(): 
                        for key1,value1 in value.items():
                            try:
                                update_vpc_file("vpc_main.tf","aws_vpc_ipv4_cidr_block_association", key, key1, value1,region)
                            except Exception as exception:
                                print(exception)
            except Exception as exception:
                print("No NonRoutableVPCExtension : {} ".format(exception))

            try:
                if data['NonRoutableVPCExtensionSubnets']:
                    for key,value in data['NonRoutableVPCExtensionSubnets'].items(): 
                        for key1,value1 in value.items():
                            try:
                                update_vpc_file("vpc_main.tf","aws_subnet", key, key1, value1,region)
                            except Exception as exception:
                                print(exception)  
            except Exception as exception:
                print("No NonRoutableVPCExtensionSubnets : {} ".format(exception))
            try:
                if data['NonRoutableRouteTables']:
                    for key,value in data['NonRoutableRouteTables'].items(): 
                        for key1,value1 in value.items():
                            try:
                                update_vpc_file("vpc_main.tf","aws_route_table", key, key1, value1,region)
                            except Exception as exception:
                                print(exception)  
            except Exception as exception:
                print("No NonRoutableRouteTables : {} ".format(exception))

            try:
                if data['NonRoutableRouteTableAssociations']:
                    for key,value in data['NonRoutableRouteTableAssociations'].items(): 
                        for key1,value1 in value.items():
                            try:
                                update_vpc_file("vpc_main.tf","aws_route_table_association", key, key1, value1,region)
                            except Exception as exception:
                                print(exception)  
            except Exception as exception:
                print("No NonRoutableRouteTableAssociations : {} ".format(exception))

            try:
                if data['NonRoutableRouteTableRoutes']:
                    for key,value in data['NonRoutableRouteTableRoutes'].items(): 
                        for key1,value1 in value.items():
                            try:
                                update_vpc_file("vpc_main.tf","aws_route", key, key1, value1,region)
                            except Exception as exception:
                                print(exception)  
            except Exception as exception:
                print("No NonRoutableRouteTableRoutes : {} ".format(exception))

            try:
                if data['NATGateway']:
                    for key,value in data['NATGateway'].items(): 
                        for key1,value1 in value.items():
                            try:
                                update_vpc_file("vpc_main.tf","aws_nat_gateway", key, key1, value1,region)
                            except Exception as exception:
                                print(exception)           
            except Exception as exception:
                print("No NATGateway : {} ".format(exception))

    if region == "eu-west-1":

        if parameters_data['VPC_cidr_extend_number_EU'] != 0:

            try:
                if data['VPCExtension1']:
                    for key,value in data['VPCExtension1'].items(): 
                        for key1,value1 in value.items():
                            try:
                                update_vpc_file("vpc_main.tf","aws_vpc_ipv4_cidr_block_association", key, key1, value1,region)
                            except Exception as exception:
                                print(exception) 
            except Exception as exception:
                print("No VPCExtension1 : {} ".format(exception))

            try:
                if data['VPCExtensionSubnets1']:
                    for key,value in data['VPCExtensionSubnets1'].items(): 
                        for key1,value1 in value.items():
                            try:
                                update_vpc_file("vpc_main.tf","aws_subnet" , key, key1, value1,region)
                            except Exception as exception:
                                print(exception) 
            except Exception as exception:
                print("No VPCExtensionSubnets1 : {} ".format(exception))

            try:
                if data['VPCExtension2']:
                    for key,value in data['VPCExtension2'].items(): 
                        for key1,value1 in value.items():
                            try:
                                update_vpc_file("vpc_main.tf","aws_vpc_ipv4_cidr_block_association", key, key1, value1,region)
                            except Exception as exception:
                                print(exception)
            except Exception as exception:
                print("No VPCExtension2 : {} ".format(exception))

            try:
                if data['VPCExtensionSubnets2']:
                    for key,value in data['VPCExtensionSubnets2'].items(): 
                        for key1,value1 in value.items():
                            try:
                                update_vpc_file("vpc_main.tf","aws_subnet" , key, key1, value1,region)
                            except Exception as exception:
                                print(exception) 
            except Exception as exception:
                print("No VPCExtensionSubnets2 : {} ".format(exception))

            try:
                if data['VPCExtension3']:
                    for key,value in data['VPCExtension3'].items(): 
                        for key1,value1 in value.items():
                            try:
                                update_vpc_file("vpc_main.tf","aws_vpc_ipv4_cidr_block_association", key, key1, value1,region)
                            except Exception as exception:
                                print(exception) 
            except Exception as exception:
                print("No VPCExtension3 : {} ".format(exception))

            try:
                if data['VPCExtensionSubnets3']:
                    for key,value in data['VPCExtensionSubnets3'].items(): 
                        for key1,value1 in value.items():
                            try:
                                update_vpc_file("vpc_main.tf","aws_subnet", key, key1, value1,region)
                            except Exception as exception:
                                print(exception) 
            except Exception as exception:
                print("No VPCExtensionSubnets3 : {} ".format(exception)) 

        if parameters_data['Non_routable_requested_EU'] == "Yes":

            try:
                if data['NonRoutableVPCExtension']:
                    for key,value in data['NonRoutableVPCExtension'].items(): 
                        for key1,value1 in value.items():
                            try:
                                update_vpc_file("vpc_main.tf","aws_vpc_ipv4_cidr_block_association", key, key1, value1,region)
                            except Exception as exception:
                                print(exception) 
            except Exception as exception:
                print("No NonRoutableVPCExtension : {} ".format(exception))

            try:
                if data['NonRoutableVPCExtensionSubnets']:
                    for key,value in data['NonRoutableVPCExtensionSubnets'].items(): 
                        for key1,value1 in value.items():
                            try:
                                update_vpc_file("vpc_main.tf","aws_subnet", key, key1, value1,region)
                            except Exception as exception:
                                print(exception) 
            except Exception as exception:
                print("No NonRoutableVPCExtensionSubnets : {} ".format(exception))  

            try:
                if data['NonRoutableRouteTables']:
                    for key,value in data['NonRoutableRouteTables'].items(): 
                        for key1,value1 in value.items():
                            try:
                                update_vpc_file("vpc_main.tf","aws_route_table", key, key1, value1,region)
                            except Exception as exception:
                                print(exception) 
            except Exception as exception:
                print("No NonRoutableRouteTables : {} ".format(exception))  

            try:
                if data['NonRoutableRouteTableAssociations']:
                    for key,value in data['NonRoutableRouteTableAssociations'].items(): 
                        for key1,value1 in value.items():
                            try:
                                update_vpc_file("vpc_main.tf","aws_route_table_association", key, key1, value1,region)
                            except Exception as exception:
                                print(exception) 
            except Exception as exception:
                print("No NonRoutableRouteTableAssociations : {} ".format(exception))  

            try:
                if data['NonRoutableRouteTableRoutes']:
                    for key,value in data['NonRoutableRouteTableRoutes'].items(): 
                        for key1,value1 in value.items():
                            try:
                                update_vpc_file("vpc_main.tf","aws_route", key, key1, value1,region)
                            except Exception as exception:
                                print(exception) 
            except Exception as exception:
                print("No NonRoutableRouteTableRoutes : {} ".format(exception))  

            try:
                if data['NATGateway']:
                    for key,value in data['NATGateway'].items(): 
                        for key1,value1 in value.items():
                            try:
                                update_vpc_file("vpc_main.tf","aws_nat_gateway", key, key1, value1,region)
                            except Exception as exception:
                                print(exception) 
            except Exception as exception:
                print("No NATGateway : {} ".format(exception))  

    if region == "ap-southeast-1":

        if parameters_data['VPC_cidr_extend_number_SG'] != 0:

            try:
                if data['VPCExtension1']:
                    for key,value in data['VPCExtension1'].items(): 
                        for key1,value1 in value.items():
                            try:
                                update_vpc_file("vpc_main.tf","aws_vpc_ipv4_cidr_block_association", key, key1, value1,region)
                            except Exception as exception:
                                print(exception) 
            except Exception as exception:
                print("No VPCExtension1 : {} ".format(exception)) 

            try:
                if data['VPCExtensionSubnets1']:
                    for key,value in data['VPCExtensionSubnets1'].items(): 
                        for key1,value1 in value.items():
                            try:
                                update_vpc_file("vpc_main.tf","aws_subnet" , key, key1, value1,region)
                            except Exception as exception:
                                print(exception) 
            except Exception as exception:
                print("No VPCExtensionSubnets1 : {} ".format(exception)) 

            try:
                if data['VPCExtension2']:
                    for key,value in data['VPCExtension2'].items(): 
                        for key1,value1 in value.items():
                            try:
                                update_vpc_file("vpc_main.tf","aws_vpc_ipv4_cidr_block_association", key, key1, value1,region)
                            except Exception as exception:
                                print(exception) 
            except Exception as exception:
                print("No VPCExtension2 : {} ".format(exception))

            try:
                if data['VPCExtensionSubnets2']:
                    for key,value in data['VPCExtensionSubnets2'].items(): 
                        for key1,value1 in value.items():
                            try:
                                update_vpc_file("vpc_main.tf","aws_subnet", key, key1, value1,region)
                            except Exception as exception:
                                print(exception) 
            except Exception as exception:
                print("No VPCExtensionSubnets2 : {} ".format(exception)) 

            try:
                if data['VPCExtension3']:
                    for key,value in data['VPCExtension3'].items(): 
                        for key1,value1 in value.items():
                            try:
                                update_vpc_file("vpc_main.tf","aws_vpc_ipv4_cidr_block_association", key, key1, value1,region)
                            except Exception as exception:
                                print(exception) 
            except Exception as exception:
                print("No VPCExtension3 : {} ".format(exception))

            try:
                if data['VPCExtensionSubnets3']:
                    for key,value in data['VPCExtensionSubnets3'].items(): 
                        for key1,value1 in value.items():
                            try:
                                update_vpc_file("vpc_main.tf","aws_subnet", key, key1, value1,region)
                            except Exception as exception:
                                print(exception) 
            except Exception as exception:
                print("No VPCExtensionSubnets3 : {} ".format(exception)) 

        if parameters_data['Non_routable_requested_SG'] == "Yes":

            try:
                if data['NonRoutableVPCExtension']:
                    for key,value in data['NonRoutableVPCExtension'].items(): 
                        for key1,value1 in value.items():
                            try:
                                update_vpc_file("vpc_main.tf","aws_vpc_ipv4_cidr_block_association", key, key1, value1,region)
                            except Exception as exception:
                                print(exception) 
            except Exception as exception:
                print("No NonRoutableVPCExtension : {} ".format(exception))

            try:
                if data['NonRoutableVPCExtensionSubnets']:
                    for key,value in data['NonRoutableVPCExtensionSubnets'].items(): 
                        for key1,value1 in value.items():
                            try:
                                update_vpc_file("vpc_main.tf","aws_subnet", key, key1, value1,region)
                            except Exception as exception:
                                print(exception) 
            except Exception as exception:
                print("No NonRoutableVPCExtensionSubnets : {} ".format(exception))  

            try:
                if data['NonRoutableRouteTables']:
                    for key,value in data['NonRoutableRouteTables'].items(): 
                        for key1,value1 in value.items():
                            try:
                                update_vpc_file("vpc_main.tf","aws_route_table", key, key1, value1,region)
                            except Exception as exception:
                                print(exception) 
            except Exception as exception:
                print("No NonRoutableRouteTables : {} ".format(exception))  

            try:
                if data['NonRoutableRouteTableAssociations']:
                    for key,value in data['NonRoutableRouteTableAssociations'].items(): 
                        for key1,value1 in value.items():
                            try:
                                update_vpc_file("vpc_main.tf","aws_route_table_association", key, key1, value1,region)
                            except Exception as exception:
                                print(exception) 
            except Exception as exception:
                print("No NonRoutableRouteTableAssociations : {} ".format(exception)) 

            try:
                if data['NonRoutableRouteTableRoutes']:
                    for key,value in data['NonRoutableRouteTableRoutes'].items(): 
                        for key1,value1 in value.items():
                            try:
                                update_vpc_file("vpc_main.tf","aws_route", key, key1, value1,region)
                            except Exception as exception:
                                print(exception) 
            except Exception as exception:
                print("No NonRoutableRouteTableRoutes : {} ".format(exception))  

            try:
                if data['NATGateway']:
                    for key,value in data['NATGateway'].items(): 
                        for key1,value1 in value.items():
                            try:
                                update_vpc_file("vpc_main.tf","aws_nat_gateway", key, key1, value1,region)
                            except Exception as exception:
                                print(exception) 
            except Exception as exception:
                print("No NATGateway : {} ".format(exception)) 

for file in ["accessanalyzer_main.tf", "ebsencryption_main.tf","config_main.tf", "backup_main.tf","budget_main.tf", "emrblockpublicaccess_main.tf", "iam_main.tf","s3blockpublicaccess_main.tf","sso_main.tf","securityhub_main.tf","vpc_main.tf", "ssm_main.tf"]:
    with open(file,'r') as new_file:
        print("###############################################\n")
        print("Verifiying file after adding import blocks -", file)
        print("\n\n")
        print(new_file.read())