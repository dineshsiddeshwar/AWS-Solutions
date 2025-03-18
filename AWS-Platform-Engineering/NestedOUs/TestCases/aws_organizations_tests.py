def aws_organizations_check_if_ou_exist(organizations, ou_id):
    try:
        response = organizations.describe_organizational_unit(
            OrganizationalUnitId=ou_id
        )
        print(response['OrganizationalUnit']['Name'])
    except Exception as e:
        print("error occured while aws_iam_check_if_role_exist and error is {}".format(e))
        return False
    else:
         return True

