import sys
from os import path

apistartup = "gmat_startup_file.txt"
GmatInstall = r"D:\GMAT\gmat-win-R2025a\GMAT_R2025a"
GmatBinPath = GmatInstall + "/bin"
Startup = GmatBinPath + "/" + apistartup

if path.exists(Startup):
print(f'Running GMAT in {GmatInstall}')

sys.path.insert(1, GmatBinPath)

import gmatpy as gmat

gmat.Setup(Startup)
else:
print("Cannot find ", Startup)
print()
print("Please set up a GMAT startup file named ", apistartup, " in the ",
GmatBinPath, " folder.")

sat = gmat.Construct("Spacecraft", "LNSS_Sat1")
sat.SetField("DateFormat", "UTCGregorian")
sat.SetField("Epoch", "01 Jan 2026 00:00:00.000")
sat.SetField("CoordinateSystem", "MoonMJ2000Eq")
sat.SetField("DisplayStateType", "Keplerian")
sat.SetField("SMA", 6541.4)
sat.SetField("ECC", 0.6)
sat.SetField("INC", 56.2)
sat.SetField("AOP", 90.0)
sat.SetField("RAAN", 0.0)
sat.SetField("TA", 0.0)
sat.SetField("DryMass", 80.0)
sat.SetField("Cr", 1.8)
sat.SetField("SRPArea", 1.5)
sat.SetField("Cd", 2.2)
sat.SetField("DragArea", 1.0)

cs = gmat.Construct("CoordinateSystem", "LunaMJ2000Eq")
cs.SetField("Origin", "Luna")
cs.SetField("Axes", "MJ2000Eq")

gds = gmat.Construct("GroundStation", "GroundStation1")