def aws_organizations_check_if_scp_is_created_and_attached(organizations_client, ou_id, ou_scp_details):
    
    try:
        policy_response = organizations_client.list_policies_for_target(TargetId=ou_id, Filter='SERVICE_CONTROL_POLICY')
        Attached_SCPs = [policy["Name"] for policy in policy_response ["Policies"]]
        print("Checking for OU {} and SCP {} .".format(ou_scp_details[0],ou_scp_details[1]))
        print("Attached policies {} for {} OU".format(Attached_SCPs, ou_scp_details[0]))
        if ou_scp_details[1] in Attached_SCPs:
            return True
    except Exception as e:
        print("error occured while aws_organizations_check_if_scp_is_created_and_attached and error is {}".format(e))
        return False
    else:
        return False