Written by weasdown, 7/12/2023.

Out of the box, GMAT 2022a supports Python 3.6-3.9. These plugins give GMAT the ability to also work with Python 3.10-3.12.

Installation steps:

1) Download a fresh install of GMAT 2022a from https://sourceforge.net/projects/gmat/files/latest/download and extract it. This will give you a folder named gmat-win-2022a.
 
2) Open gmat-win-2022a. Inside will be a folder called GMAT - this is your GMAT root folder. Inside this will be a set of folders and files (api, bin, and so on).

3) From the plugins folder that you're reading these instructions from, copy the gmatpy folder. Paste it into GMAT/bin. Back in the plugins folder, copy the folder named plugins (that contains six .dll files). Paste this into the GMAT root folder.

4) You should now have folders or files with names ending py36 to py312 in GMAT/bin/gmatpy and GMAT/plugins.

5) To get GMAT to use a version of Python later than 3.9 by default, you need to modify two files.

6) To setup the Python API for the first time, follow the instructions in API_setup.txt. If you've already done that, you're good to go!