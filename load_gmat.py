# GMAT Application Programmer's Interface Example
#
# Coded by D. Conway. Thinking Systems, Inc.
#
# This file is a template for files used run the GMAT API from a folder outside
# the GMAT application folder.

import sys
from os import path

api_startup = 'api_startup_file.txt'

# Absolute path to your root GMAT folder (below is just an example).
# On Windows, be sure to use either double backslashes or single forward slashes.
gmat_install = 'C:/Users/[USERNAME]/dev/GMAT/gmat-win-R2022a/GMAT'

gmat_bin_path = gmat_install + '/bin'
startup_file = f'{gmat_bin_path}/{api_startup}'

if path.exists(startup_file):

    sys.path.insert(1, gmat_bin_path)

    import gmatpy as gmat

    gmat.Setup(startup_file)

else:
    print(f'Cannot find {startup_file}\n'
          f'\n'
          f'Please set up a GMAT startup file named {api_startup} in the {gmat_bin_path} folder.')
