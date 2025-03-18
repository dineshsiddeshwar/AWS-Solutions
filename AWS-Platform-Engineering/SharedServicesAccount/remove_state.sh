

elements=("module.iam-module-ap-southeast-1.aws_iam_instance_profile.platform_ServiceNow_ITOM_Discovery_Child_InstanceProfile" "module.iam-module-ap-southeast-1.aws_iam_policy.policy_platform_ITOM_Discovery_Child_Policy" "module.iam-module-ap-southeast-1.aws_iam_policy.policy_platform_cloud_health_policy" "module.iam-module-ap-southeast-1.aws_iam_role.platform_ServiceNow_ITOM_Discovery_Child_Role" "module.iam-module-ap-southeast-1.aws_iam_role.platform_service_cloudhealth_role" "module.iam-module-eu-west-1.aws_iam_instance_profile.platform_ServiceNow_ITOM_Discovery_Child_InstanceProfile" "module.iam-module-eu-west-1.aws_iam_policy.policy_platform_ITOM_Discovery_Child_Policy" "module.iam-module-eu-west-1.aws_iam_policy.policy_platform_cloud_health_policy" "module.iam-module-eu-west-1.aws_iam_role.platform_ServiceNow_ITOM_Discovery_Child_Role" "module.iam-module-eu-west-1.aws_iam_role.platform_service_cloudhealth_role" "module.iam-module-us-east-1.aws_iam_instance_profile.platform_ServiceNow_ITOM_Discovery_Child_InstanceProfile" "module.iam-module-us-east-1.aws_iam_policy.policy_platform_ITOM_Discovery_Child_Policy" "module.iam-module-us-east-1.aws_iam_policy.policy_platform_cloud_health_policy" "module.iam-module-us-east-1.aws_iam_role.platform_ServiceNow_ITOM_Discovery_Child_Role" "module.iam-module-us-east-1.aws_iam_role.platform_service_cloudhealth_role")

# Loop through each element and execute a statement
for element in "${elements[@]}"
do
    echo "Processing element: $element"
    terraform state rm "$element"
    # Replace the following line with the statement you want to execute for each element
    # For example: 
    #   aws ec2 describe-instances --instance-ids "$element"
done
