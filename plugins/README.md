# Installing plugins

To communicate with Python, GMAT uses plugins that correspond to a Python version. For example, if you use Python 3.12, 
GMAT will use plugins in a folder called `_py312`. Out of the box, different versions of GMAT support different Python 
versions. GMAT R2022a supports Python 3.6-3.9, while GMAT R2025a supports Python 3.6-3.12.

You can add support for extra Python versions by adding the relevant files in this directory to your GMAT installation. 
These have been compiled and tested with GMAT R2025a. You can also compile the plugins yourself by following the [GMAT 
compilation tutorial](https://gmat.atlassian.net/wiki/spaces/GW/pages/380273355/Compiling+GMAT+CMake+Build+System).

Throughout these instructions, `[GMAT]` refers to the root directory of your GMAT installation, e.g. 
`.../gmat-win-2025a`.

## Installation steps

1) Download a fresh copy of GMAT from https://sourceforge.net/projects/gmat/files/latest/download and extract it. For 
GMAT R2025a (recommended), this will give you a folder named `gmat-win-2025a`.
 
2) Open `gmat-win-2025a`. Inside will be a folder called GMAT - this is your GMAT root folder. Inside this will be a set
of folders and files (`api`, `bin`, and so on).

3) From the `plugins` folder that you're reading these instructions from, copy the contents of the `gmatpy` folder. 
Paste the files into `GMAT/bin/gmatpy`. Back in the `plugins` folder, copy the contents of the `plugins`  folder (that 
contains six `.dll` files). Paste the files into `[GMAT]/plugins`.
   
4) You should now have folders or files with names ending `py36` to `py312` in `[GMAT]/bin/gmatpy` and `[GMAT]/plugins`.

5) To get GMAT to use a non-default version of Python, you need to modify two files in `[GMAT]/bin`: 
`api_startup_file.txt` and `gmat_startup_file.txt`. In each of these, within the `Plugins` section, replace the endings 
for library files `libPythonInterface_py3xx` and `libExternalForceModel_py3xx` with the Python version you want to use. 
For example, if GMAT is currently setup for Python 3.9, but you want to use Python 3.12, `libPythonInterface_py39` would
become `libPythonInterface_py312`. Four lines will need modifying in total, one for each of the library files, in each 
of the `.txt` files.

6) To set up the Python API for the first time, follow the instructions in [`API_setup.txt`](API_setup.txt). If you've 
already done that, you're good to go!
