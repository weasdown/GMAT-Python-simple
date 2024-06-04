from load_gmat import gmat

gmat.LoadScript('C:/Users/weasd/Downloads/default.script')
gmat.ShowObjects()
sc = gmat.GetObject('DefaultSC')
dscela = gmat.GetObject('DefaultSC.ElapsedSecs')
dscela.Help()
print(dscela.GetRefObjectName(gmat.SPACECRAFT))
# print(dscela.GetRefObjectName(gmat.STOP_CONDITION))
gmat.RunScript()
gmat.ShowObjects()
