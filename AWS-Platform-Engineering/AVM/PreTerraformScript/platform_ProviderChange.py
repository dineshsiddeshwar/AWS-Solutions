import sys
import os
from tempfile import mkstemp
from shutil import move
from os import fdopen, remove

RootAVMfolder = str(sys.argv[5])
print("Root AVM folder is:", RootAVMfolder)


##  Replace provider file with correct key and secrete dynamically.
def replace(file_path, pattern, subst):
    fh, abs_path = mkstemp()
    with fdopen(fh,'w') as new_file:
        with open(file_path) as old_file:
            for line in old_file:
                new_file.write(line.replace(pattern, subst))
    remove(file_path)
    move(abs_path, file_path)

try:
    print("Changing Provider file values now...")
    if os.path.isdir(RootAVMfolder):
        print("Did find the Root AVM folder path..!!")
        x = [os.path.join(r,file) for r,d,f in os.walk(RootAVMfolder) for file in f]
        print("Got complete list of paths of file that needs to be updated...")
        print("starting the replacements...!!")
        for y in x:
            print(y)
            replace(y, 'TFC_SHARED_ACCOUNT_KEY', str(sys.argv[1]))
            replace(y, 'TFC_SHARED_ACCOUNT_SECRET', str(sys.argv[2]))
            replace(y, 'TFC_PAYER_ACCOUNT_KEY', str(sys.argv[3]))
            replace(y, 'TFC_PAYER_ACCOUNT_SECRET', str(sys.argv[4]))
        print("replacing provider file is complete now...!!")
    else:
        print("Did not find the Root AVM folder folder path..!!")
except Exception as ex:
    print("There is an error %s", str(ex))