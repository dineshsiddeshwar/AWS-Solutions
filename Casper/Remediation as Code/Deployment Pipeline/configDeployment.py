from logging import warning
import os
import generalFunc
import gqlVariables
from gql import gql
import json
import warnings
import sys

# Path to python file
py_path = os.path.dirname(os.path.realpath(__file__))
home_path=os.path.normpath(os.path.join(py_path,".."))

# Path to policy source
requirements_relative_path="Requirement"
requirements_path=os.path.join(home_path,requirements_relative_path)

# Path to wiz framework
framework_relative_path="Technical-controls-framework/wizFramework.json"
framework_path=os.path.join(home_path,framework_relative_path)

# The GraphQL query that defines which data you wish to fetch.
wiz_query=gqlVariables.createCloudConfigurationPolicy

def warning_on_one_line(message, category, filename, lineno, file=None, line=None):
    return '%s:%s: %s: %s\n' % (filename, lineno, category.__name__, message)

warnings.formatwarning = warning_on_one_line

def create_security_framework(TOKEN):
    framework=gqlVariables.createWizSeurityFramework
    try:
        framework_json=json.loads(open(framework_path, "r").read())
        framework.variables=framework_json
        result=generalFunc.query_wiz_api(TOKEN,gqlVariables.createWizSeurityFramework)
        framework_id = result['createSecurityFramework']['framework']['id']
    except FileNotFoundError as e:
        sys.exit("ERROR: Framework File Error: {}".format(e))
    except KeyError as e:
        sys.exit("ERROR: Framework Response Key Error: {}".format(e))
    except Exception as e:
        sys.exit("ERROR: Framework Deployment Error: {}".format(e))
    return framework_id

def push_all_policies(wiz_query:gqlVariables.gqlQueryAndVariable, TOKEN):   
    '''Get all requirements jsons'''
    for dirpath, dirnames, filenames in os.walk(requirements_path):
        for filename in [f for f in filenames if f.endswith(".json")]:
            requirements_file_path=os.path.join(dirpath, filename)
            try:
                requirements_file=json.loads(open(requirements_file_path, "r").read())
            except FileNotFoundError as e:
                warnings.warn("Requirements File Missing: {}".format(e))
                continue
            except Exception as e: 
                warnings.warn("Requirements File: {} | {}".format(os.path.basename(requirements_file_path), e))
                continue
            '''temp section begin'''
            # Ignore if required data format absent
            if "mappings" not in requirements_file:
                continue
            '''temp section ends'''
            '''Iterate through all requirement json files to get policies'''
            for requirements_json in requirements_file['mappings']:
                if not requirements_json['implementations']:
                    continue
                '''Get requirement severity'''
                if requirements_json['severityCvssRating'] != "":
                    wiz_query.variables['input']['severity']=(requirements_json['severityCvssRating']).upper()
                else:
                    warnings.warn("Using default severity for requirement {}".format(requirements_json['id']))
                '''Iterate through policy implementations'''
                for implementation_relative_path in [f for f in requirements_json['implementations'] if f.endswith(".json")]:
                    design_wiz_policy(wiz_query, implementation_relative_path, TOKEN)
    return
    
def design_wiz_policy(wiz_query:gqlVariables.gqlQueryAndVariable, implementation_relative_path, TOKEN):
    implementation_file_path=os.path.join(home_path, implementation_relative_path)
    try:
        implementation_json=json.loads(open(implementation_file_path, "r").read())
    except FileNotFoundError as e:
        warnings.warn("Implementation File Missing: {}".format(e))
        return
    except Exception as e: 
        warnings.warn("Implementation Json Load Failed:", e)
        return

    if implementation_json['implementationProvider'] != 'wiz':
        return
    wiz_query.variables['input']['name']=implementation_json['id']+' '+implementation_json['label']
    wiz_query.variables['input']['description']=implementation_json['description']
    if implementation_json['wizNativeType'] == "":
        warnings.warn("WizNativeType Missing: {}".format(implementation_json['id']))
        return
    wiz_query.variables['input']['targetNativeTypes']=implementation_json['wizNativeType']
    rego_path=os.path.join(home_path,implementation_json['link'])
    try:
        policy_rego=open(rego_path, "r").read()
    except FileNotFoundError as e:
        warnings.warn("Policy Rego File Missing: {}".format(e))
        return
    wiz_query.variables['input']['opaPolicy']=policy_rego

    '''Call query'''
    try:
        result=generalFunc.query_wiz_api(TOKEN, wiz_query)
    except Exception as e:
        warnings.warn("Policy Deployment Failed: Policy Name: {} | {}".format(wiz_query.variables['input']['name'], e))
        return
    print("Policy Deployed: ", result)
    return

def main():
    print("Getting token.")
    try:
        TOKEN=generalFunc.request_wiz_api_token()
    except Exception as e:
        sys.exit("ERROR: {}".format(e))
    framework_id=create_security_framework(TOKEN)
    wiz_query.variables['input']['securitySubCategories']=[framework_id]
    push_all_policies(wiz_query, TOKEN)

if __name__ == '__main__':
    main()
