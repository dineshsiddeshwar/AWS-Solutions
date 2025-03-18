import sys
import os
import boto3
import zipfile

env_type = sys.argv[1]
workspacepath = sys.argv[2]
release_number = sys.argv[3]
is_pythonfile = sys.argv[4]

s3_client = boto3.client('s3')
region_list = ["us-east-1","eu-west-1","us-east-2","us-west-1","us-west-2","ap-south-1","ap-southeast-2","ap-southeast-1","eu-central-1","eu-west-2","eu-north-1","ap-northeast-2","ap-northeast-1","ca-central-1"]
bucket_list = []
try:
      for region in region_list:
            bucket_list.append('azure-devops-da2.0-stackset-'+env_type+'-'+region)
except Exception as ex:
      print("error in generating bucket list")
print("bucket list : ", bucket_list)

print("Env type is : {}".format(env_type))
print("filepath is : {}".format(workspacepath))
print("Release number is : {}".format(release_number))

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
            print("There is an error in function create_zip_for_each_py_file {}".format(ex))

# uploading stack set resources to s3 bucket
def upload_stackset_resources_to_s3(r,i): 
      key = release_number+"/"+i           
      try:
            for bucket in bucket_list:
                  s3_client.upload_file(r, bucket, key)
                  print("s3 upload succeeded to bucket  ",bucket)
      except Exception as ex:
            print("There is an error in function upload_stackset_resources_to_s3 {}".format(ex))

# uploading Stack set file to s3
def upload_stackset_file_to_s3(r,i): 
      key = release_number+"/CloudFormation/"+i      
      filename = r+"/"+i      
      try:
            buckettoupload = "azure-devops-da2.0-release-"+env_type+"-us-east-1"
            s3_client.upload_file(filename, buckettoupload, key)
            print("s3 upload succeeded to bucket  ",buckettoupload)
      except Exception as ex:
            print("There is an error in upload_stackset_file_to_s3 {}".format(ex))

try:
      if os.path.isdir(workspacepath):
            print("Did find the path to upload the Stackset yml file..!!")
            for r,d,f in os.walk(workspacepath+"/StackSetFile"):
                  print(r, d, f)
                  for i in f:                                           
                        upload_stackset_file_to_s3(r,i)
            print("Stackset yml file upload completed..!!")
      else:
            print("Did not find the base path for Stackset yml file upload..!!") 
      
      if is_pythonfile == 'yes':
            if os.path.isdir(workspacepath):
                  print("Did find the path to upload the Python zip file..!!")
                  create_zip_for_each_py_file(workspacepath+"/PythonFunctionFiles")
                  print("Python zip file upload completed..!!")
            else:
                  print("Did not find the base path for Python zip file upload..!!")
      else:
            print("No Python zip files to upload..!!")
      
except Exception as ex:
    print("There is an error %s", str(ex))