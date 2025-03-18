def aws_check_if_ssm_associations_created(ssm, association_name):
    try:
        response = ssm.list_associations(
                AssociationFilterList=[
                    {
                        'key': 'AssociationName',
                        'value': association_name
                    },
                ]
            )
        if (response['Associations'].__len__() > 0):
            return True
        else:
            return False
    except Exception as e:
        print("error occured while aws_check_if_ssm_associations_created and error is {}".format(e))
        return False
    
def aws_check_if_ssm_parameters_exists(ssm,parameter_name):
    try:
        response  = ssm.get_parameter(Name=parameter_name)
        if len(response['Parameter'])>0:
            return True
        else:
            return False
    except Exception as e:
        print("error occured while aws_check_if_ssm_parameters_exists and error is {}".format(e))
        return False