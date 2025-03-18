import sys
import os
from tempfile import mkstemp
from shutil import move
from os import fdopen, remove

AccountNumber= str(sys.argv[1])
print("AccountNumber is: ", AccountNumber)
Backendfolder = str(sys.argv[2])
print("TFC backend files Path is:", Backendfolder)


##  Replace backend file path with account workspace name
def replace(file_path, pattern, subst):
    fh, abs_path = mkstemp()
    with fdopen(fh,'w') as new_file:
        with open(file_path) as old_file:
            for line in old_file:
                new_file.write(line.replace(pattern, subst))
    remove(file_path)
    move(abs_path, file_path)

try:
    print("Changing the TFC workspace now...")
    if os.path.isdir(Backendfolder):
        print("Did find the Backend folder path..!!")
        x = [os.path.join(r,file) for r,d,f in os.walk(Backendfolder) for file in f]
        print("Got complete list of paths of file that needs to be updated...")
        print("starting the replacements...!!")
        for y in x:
            print(y)
            replace(y, 'TFCWORKSpaceName', AccountNumber)
        print("replacing the TFCWORKSpaceName name is complete now...!!")
    else:
        print("Did not find the Backend folder path..!!")
except Exception as ex:
    print("There is an error %s", str(ex))