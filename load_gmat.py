# GMAT Application Programmer's Interface Example
#
# Coded by D. Conway. Thinking Systems, Inc.
#
# This file is a template for files used run the GMAT API from a folder outside  
# of the GMAT application folder.

import sys
from os import path

apistartup = "api_startup_file.txt"

# Absolute path to your root GMAT folder (below is just an example).
# On Windows, be sure to use either double backslashes or single forward slashes.
GmatInstall = "C:\\Users\\[USERNAME]\\dev\\GMAT\\gmat-win-R2022a\\GMAT"

GmatBinPath = GmatInstall + "/bin"
Startup = GmatBinPath + "/" + apistartup

if path.exists(Startup):


   sys.path.insert(1, GmatBinPath)

   import gmatpy as gmat
   gmat.Setup(Startup)

else:
   print("Cannot find ", Startup)
   print()
   print("Please set up a GMAT startup file named ", apistartup, " in the ", 
      GmatBinPath, " folder.")
