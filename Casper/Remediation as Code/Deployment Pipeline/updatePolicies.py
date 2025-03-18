from logging import warning
import os
import generalFunc
import gqlVariables
from gql import gql
import warnings
import sys
import json

# Path to python file
py_path = os.path.dirname(os.path.realpath(__file__))
home_path=os.path.normpath(os.path.join(py_path,".."))


sections_list=['Detective-Pipeline', 'Implentation-json']

# Path to wiz framework
framework_relative_path="Technical-controls-framework/wizFramework.json"
framework_path=os.path.join(home_path,framework_relative_path)

# The GraphQL query that defines which data you wish to fetch.
wiz_query=gqlVariables.createCloudConfigurationPolicy

def warning_on_one_line(message, category, filename, lineno, file=None, line=None):
    return '%s:%s: %s: %s\n' % (filename, lineno, category.__name__, message)

warnings.formatwarning = warning_on_one_line

def regular_policy_update(file_relative_path, TOKEN):
    split=file_relative_path.split('/')
    cloud=split[1]
    component_type=split[2] 
    file=split[3] 
    policy_id=os.path.splitext(file)[0]
    if 'Implentation-json' in split[0]:
        implementation_file_path=os.path.join(home_path,file_relative_path)
        requirements_file_path=os.path.join(home_path,'Requirement',cloud,"{}.json".format(component_type))
    else:
        policy_file_realtive_path=file_relative_path
        implementation_file_path=os.path.join(home_path,'Implementation-json',cloud,component_type,"{}.json".format(policy_id))
        requirements_file_path=os.path.join(home_path,'Requirement',cloud,"{}.json".format(component_type))
        '''Check if policy mentioned matches value in implementation
        If not deliver warning and discard'''
        try:
            if policy_file_realtive_path not in open(implementation_file_path, "r").read():
                warnings.warn("Requisite policy file {} not mention in implementation file: {}".format(policy_file_realtive_path, implementation_file_path))
                return
        except FileNotFoundError as e:
            warnings.warn("Implementation File Missing: {}".format(e))
            return
    try:
        if policy_id not in open(requirements_file_path, "r").read():
            warnings.warn("Requisite policy {} not mention in requirement file: {}".format(policy_id, requirements_file_path))
            return
    except FileNotFoundError as e:
        warnings.warn("Implementation File Missing: {}".format(e))
        return
    print(implementation_file_path,' ',requirements_file_path)

    
    


def requirements_based_update(requirements_file_relative_path, TOKEN):
    requirements_file_path=os.path.join(home_path,requirements_file_relative_path)
    try:
        requirements_file=json.loads(open(requirements_file_path, "r").read())
    except FileNotFoundError as e:
        warnings.warn("Requirements File Missing: {}".format(e))
        return
    except Exception as e: 
        warnings.warn("Requirements File: {} | {}".format(os.path.basename(requirements_file_path), e))
        return
            
    '''temp section begin'''
    # Ignore if required data format absent
    if "mappings" not in requirements_file:
        return
    '''temp section ends'''
    '''Iterate through all requirement json files to get policies'''
    for requirements_json in requirements_file['mappings']:
        '''Get requirement severity'''
        wiz_query.variables['input']['severity']=(requirements_json['severityCvssRating']).upper()
        '''Iterate through policy implementations'''
        for implementation_relative_path in [f for f in requirements_json['implementations'] if f.endswith(".json")]:
            update_wiz_policy(wiz_query, implementation_relative_path, TOKEN)

def check_changed_files(changed_file_realtive_path, TOKEN):
    changed_file_path=os.path.join(home_path,changed_file_realtive_path)
    # changed_files=open(changed_file_path, "r").read()
    with open(changed_file_path) as changed_files:
        for changed_file in changed_files:
            changed_file=changed_file.strip()
            if any(section in changed_file for section in sections_list) and ( changed_file.endswith(".json") or changed_file.endswith(".rego")):
                if 'Requirement' in changed_file:
                    requirements_based_update(changed_file, TOKEN)
                else:
                    regular_policy_update(changed_file, TOKEN)


            
            
               
    return

def main():
    print("Getting token.")
    try:
        TOKEN=generalFunc.request_wiz_api_token()
    except Exception as e:
        sys.exit("ERROR: {}".format(e))
    changed_file_realtive_path='Deployment-Pipeline/files'
    check_changed_files(changed_file_realtive_path, TOKEN)
    

if __name__ == '__main__':
    main()
