import sys
import os
from tempfile import mkstemp
from shutil import move
from os import fdopen, remove

EMAIL_SOURCE= str(sys.argv[1])
print("Email Source is: ", EMAIL_SOURCE)
IDC_LOGIN_URL= str(sys.argv[2])
print("Login URL: ", IDC_LOGIN_URL)
REGION= str(sys.argv[3])
print("Region is: ", REGION)
TEAM_ACCOUNT= str(sys.argv[4])
print("TEAM Account is: ", TEAM_ACCOUNT)
ORG_MASTER_PROFILE= str(sys.argv[5])
print("ORG master profile is: ", ORG_MASTER_PROFILE)
TEAM_ACCOUNT_PROFILE= str(sys.argv[6])
print("TEAM Account Profile is: ", TEAM_ACCOUNT_PROFILE)
TEAM_ADMIN_GROUP= str(sys.argv[7])
print("Team Admin group is: ", TEAM_ADMIN_GROUP)
TEAM_AUDITOR_GROUP= str(sys.argv[8])
print("Team Auditor Group is: ", TEAM_AUDITOR_GROUP)
TAGS= str(sys.argv[9])
print("Tags: ", TAGS)
CLOUDTRAIL_AUDIT_LOGS= str(sys.argv[10])
print("CLOUDTRAIL AUDIT LOGS: ", TAGS)
TEAMFolder = str(sys.argv[11])
print("TEAMFolder Path is:", TEAMFolder)


##  Replace values of parameters.sh file
def replace(file_path, pattern, subst):
    fh, abs_path = mkstemp()
    with fdopen(fh,'w') as new_file:
        with open(file_path) as old_file:
            for line in old_file:
                new_file.write(line.replace(pattern, subst))
    remove(file_path)
    move(abs_path, file_path)

try:
    print("Changing values of parameters.sh now...")
    if os.path.isdir(TEAMFolder):
        print("Did find TEAM folder path..!!")
        x = [os.path.join(r,file) for r,d,f in os.walk(TEAMFolder) for file in f]
        print("Got complete list of paths of file that needs to be updated...")
        print("starting the replacements...!!")
        for y in x:
            print(y)
            replace(y, 'EMAIL_SOURCE_VALUE', EMAIL_SOURCE)
            replace(y, 'IDC_LOGIN_URL_VALUE', IDC_LOGIN_URL)
            replace(y, 'REGION_VALUE', REGION)
            replace(y, 'ORG_MASTER_PROFILE_VALUE', ORG_MASTER_PROFILE)
            replace(y, 'TEAM_ADMIN_GROUP_VALUE', TEAM_ADMIN_GROUP)
            replace(y, 'TEAM_AUDITOR_GROUP_VALUE', TEAM_AUDITOR_GROUP)
            replace(y, 'TAGS_VALUE', TAGS)
            replace(y, 'CLOUDTRAIL_AUDIT_LOGS_VALUE', CLOUDTRAIL_AUDIT_LOGS)
        print("replacing values in parameters.sh is complete now...!!")
    else:
        print("Did not find the TEAM folder path..!!")
except Exception as ex:
    print("There is an error %s", str(ex))