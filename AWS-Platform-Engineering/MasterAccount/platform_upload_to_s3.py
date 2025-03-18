import sys
import os
import boto3
import re
import zipfile

env_type = sys.argv[1]
workspacepath = sys.argv[2]
release_number = sys.argv[3]

s3_client = boto3.client('s3')
bucket_name = 'azure-devops-da2.0-release-'+env_type+'-us-east-1'

print("Env type is : {}".format(env_type))
print("filepath is : {}".format(workspacepath))
print("Release number is : {}".format(release_number))

to_s3_file_path = "/TFC-Master/"+release_number

# uploading files to s3
def upload_to_s3(r,i,key):      
      filename = r+"/"+i      
      try:
            response = s3_client.upload_file(filename, bucket_name, key)
            print("s3 upload succeeded")
      except Exception as ex:
            print("There is an error {}".format(ex))

def upload_stackset_resources_to_s3(r,i): 
      key = release_number+"/Lambda/"+i      
      filename = r     
      try:
            s3_client.upload_file(filename, bucket_name, key)
            print("s3 upload succeeded to bucket  ",bucket_name)
      except Exception as ex:
            print("There is an error {}".format(ex))

def create_zip_for_each_py_file(folder_path):
      try:
            # Get a list of all files in the folder
            files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
            
            # Filter only the .py files
            py_files = [f for f in files if f.endswith('.py')]
            
            # Create a zip file for each .py file
            for py_file in py_files:
                  file_name, file_extension = os.path.splitext(py_file)
                  zip_file_name = f"{file_name}.zip"
                  zip_path = os.path.join(folder_path, zip_file_name)
                  
                  with zipfile.ZipFile(zip_path, 'w') as zip_file:
                        py_file_path = os.path.join(folder_path, py_file)
                        zip_file.write(py_file_path, py_file)                   
                  upload_stackset_resources_to_s3(zip_path, zip_file_name)
      except Exception as ex:
            print("There is an error {}".format(ex))

# updating service catalog tf files with s3 bucket path
def update_sc_tf_files(i):      
      try:
            if i == "avm_template.template" or i == "network.template" or i == "instancescheduler.template":
                  modify_file(workspacepath+"/modules/ServiceCatalog/platform_service_catalog.tf",to_s3_file_path)  
                  print("updated platform_service_catalog.tf")             
            elif i == "patching_window.template":
                  modify_file(workspacepath+"/modules/Patching/platform_patching_solution.tf",to_s3_file_path)
                  print("updated platform_patching_solution.tf")
            else:
                  pass            
      except Exception as ex:
            print("There is an error {}".format(ex))

# updating cft tf files with s3 bucket path
def update_cft_tf_files(i):
      try:
            if i == "CloudIntelligenceDashboards.yaml":
                  modify_file(workspacepath+"/modules/CloudIntelligenceDashboard/platform_cloud_intelligence_dashboard.tf",to_s3_file_path)  
                  print("updated platform_cloud_intelligence_dashboard.tf")
            elif i == "control-tower-iam-role-guardrails.yaml":
                  modify_file(workspacepath+"/modules/ControlTowerIAMRoleGaurdrails/platform_control_tower_iam_role_gaurdrails.tf",to_s3_file_path)
                  modify_file_2(workspacepath+"/modules/ControlTowerIAMRoleGaurdrails/platform_control_tower_iam_role_gaurdrails.tf",to_s3_file_path)    
                  print("updated platform_control_tower_iam_role_gaurdrails.tf")                  
            else:
                  pass            
      except Exception as ex:
            print("There is an error {}".format(ex))

def modify_file(filepath,to_s3_file_path):
      file = open(filepath,"r+")
      text = file.read()
      modified_text = re.sub(r'/TFC-Master\/\d+',to_s3_file_path,text)
      with open(filepath, "w") as file:
            file.write(modified_text)

def modify_file_2(filepath,to_s3_file_path):
      file = open(filepath,"r+")
      text = file.read()
      search_text = "ReleaseNumber"
      modified_text = re.sub(search_text,release_number,text)
      with open(filepath, "w") as file:
            file.write(modified_text)

try:
      if os.path.isdir(workspacepath):
            print("Did find the path..!!")
            for r,d,f in os.walk(workspacepath+"/modules/ServiceCatalog/ServiceCatalogTemplates"):
                  for i in f:
                        #update sc tf files
                        print("inside update service catalog tf files...")    
                        key = "TFC-Master/"+release_number+"/ServiceCatalogTemplates/"+i                     
                        update_sc_tf_files(i)

                        #updload files 
                        print("inside service catalog templates upload to s3 block...")                       
                        upload_to_s3(r,i,key)
            for r,d,f in os.walk(workspacepath+"/modules/CloudIntelligenceDashboard/CloudFormationTemplate"):
                  for i in f:
                        #update cft tf files
                        print("inside update cloudfromation tf files...")    
                        key = "TFC-Master/"+release_number+"/CloudFormationTemplates/"+i                     
                        update_cft_tf_files(i)
                        #updload files 
                        print("inside cloud intelligence cft template upload to s3 block ...") 
                        key = "TFC-Master/"+release_number+"/CloudFormationTemplates/"+i                      
                        upload_to_s3(r,i,key)
            for r,d,f in os.walk(workspacepath+"/modules/ControlTowerIAMRoleGaurdrails/CloudFormationTemplate"):
                  for i in f:
                        #update cft tf files
                        print("inside update cloudfromation tf files...")    
                        key = "TFC-Master/"+release_number+"/CloudFormationTemplates/"+i                     
                        update_cft_tf_files(i)
                        #updload files 
                        print("inside cloud intelligence cft template upload to s3 block ...") 
                        key = "TFC-Master/"+release_number+"/CloudFormationTemplates/"+i                      
                        upload_to_s3(r,i,key)
            for r,d,f in os.walk(workspacepath+"/modules/ControlTowerIAMRoleGaurdrails/PythonFunctionFiles"):
                  for i in f:
                        #update cft tf files
                        print("inside update python lambda files...") 
                        create_zip_for_each_py_file(workspacepath+"/modules/ControlTowerIAMRoleGaurdrails/PythonFunctionFiles")
                        print("Python zip file upload completed..!!")                       

      else:
            print("Did not find the path..!!") 
      
except Exception as ex:
    print("There is an error %s", str(ex))


