def aws_check_if_ram_resource_share_exists(ram_client):
    try:
        response = ram_client.get_resource_shares(resourceOwner='SELF')

        resource_shares = response['resourceShares']
        if len(resource_shares) > 0:
            for a in resource_shares:
                if a['name'] == "platform_Shell_Domain_Resolver_Rule_Share":
                    print("Ram Resource Share found, id is {}".format(a['resourceShareArn']))
                    return True
            print("Ram Resource Share not found for platform_Shell_Domain_Resolver_Rule_Share")
            return False
    except Exception as e:
        print("Error occurred while aws_check_if_ram_resource_share_exists and error is {}".format(e))
        return False

def aws_check_if_ram_resource_share_principals_exists(ram_client,id):
    try:
        response = ram_client.list_principals(resourceOwner='SELF')
        associations = response['principals']
        if len(associations) > 0:
            for a in associations:
                if a['id'] == id:
                    print("Ram Resource Share Principal found")
                    return True
            print("Ram Resource Share Principal not found")
            return False
    except Exception as e:
        print("Error occurred while aws_check_if_ram_resource_share_principals_exists and error is {}".format(e))
        return False
    
def aws_check_if_ram_resource_association_exists(ram_client):
    try:
        response = ram_client.get_resource_share_associations(associationType='RESOURCE')

        resource_association = response['resourceShareAssociations']
        if len(resource_association) > 0:
            for a in resource_association:
                if 'Domain_Resolver_Rule_Share' in a['resourceShareName']:
                    print("Ram Resource Share Association found, name of accociated resource is {}".format(a['resourceShareName']))
                    return True
            print("Ram Resource Share Association not found for any resource share")
            return False
    except Exception as e:
        print("Error occurred while aws_check_if_ram_resource_association_exists and error is {}".format(e))
        return False