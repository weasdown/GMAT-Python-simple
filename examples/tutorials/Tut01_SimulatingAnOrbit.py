import gmat_py_simple.utils
from load_gmat import gmat

import gmat_py_simple as gpy
from gmat_py_simple import orbit as o
from gmat_py_simple.orbit import PropSetup
from gmat_py_simple.commands import Propagate

# TODO complete modelling the tutorial mission rather than the default one

sat_params = {
    'Name': 'DefaultSat',
    'Orbit': {
        'Epoch': '22 Jul 2014 11:29:10.811',
        'DateFormat': 'UTCGregorian',
        'CoordSys': 'EarthMJ2000Eq',
        'StateType': 'Keplerian',
        'SMA': 83474.31800000001,
        'ECC': 0.89652,
        'INC': 12.4606,
        'RAAN': 292.8362,
        'AOP': 218.9805,
        'TA': 180,
    },
}

# sat = gpy.Spacecraft.from_dict(sat_params)

# sat.Help()

# lep_fm = o.ForceModel(name='LowEarthProp_ForceModel',
#                       gravity_field=o.ForceModel.GravityField(
#                           degree=10,
#                           order=10,
#                       ),
#                       point_masses=['Luna', 'Sun'],
#                       drag=True,
#                       srp=True
#                       )

# lep_fm.Help()

# start_state = sat.GetKeplerianState()
# print(f'Start state: {start_state}')
#
# prop = PropSetup('Propagator', fm=lep_fm)
#
# gmat.Initialize()
#
# Propagate(prop, sat, ('ElapsedSecs', 60))
#
# end_state = sat.GetKeplerianState()
# print(f'End state: {end_state}')

# sat.Help()
# gator = prop.GetPropagator()
# print(f'gator: {gator}')
# print('gator Help:')
# gator.Help()

sat = gmat.Construct('Spacecraft', 'Sat')
sat.SetField('Epoch', '21545')
sat_name = sat.GetName()

fm = gmat.Construct("ForceModel", "FM")
epm = gmat.Construct("PointMassForce", "EPM")
fm.AddForce(epm)

prop = gmat.Construct("Propagator", "Prop")
gator = gmat.Construct("PrinceDormand78", "Gator")
prop.SetReference(gator)
prop.SetReference(fm)

gmat.Initialize()
prop.AddPropObject(sat)
prop.PrepareInternals()

gator = prop.GetPropagator()

state = gator.GetState()


def CustomHelp(obj):
    print(f'CustomHelp for {obj.GetName()}:')
    if 'gmat_py_simple' in str(type(obj)):
        param_count = obj.gmat_obj.GetParameterCount()
    else:
        param_count = obj.GetParameterCount()

    for i in range(param_count):
        try:
            param_name = obj.GetParameterText(i)
            param_type = obj.GetParameterTypeString(i)
            print(f'Parameter: {param_name}')
            print(f'- Type: {param_type}')
            if param_type == 'String':
                val = obj.GetStringParameter(i)
            elif param_type == 'Object':
                val = obj.GetName()
            elif (param_type == 'Real') or (param_type == 'UnsignedInt') or (param_name == 'InitialEpoch'):
                val = obj.GetRealParameter(i)
            elif param_type == 'Rmatrix':
                val = obj.GetRmatrixParameter(i)
            else:
                try:
                    val = obj.GetField(param_name)
                except Exception:
                    raise TypeError(f'Getting value of {param_type} failed')

            print(f'- Value: {val}\n')

        except Exception as exc:
            print(exc, '\n')
            # raise


pgate = gmat.Construct('Propagate')
pgate.SetSolarSystem(gmat.GetSolarSystem())
pgate.SetGlobalObjectMap(gmat.Sandbox.GetGlobalObjectMap(gmat.Sandbox()))
pgate.SetObjectMap(gmat.Sandbox.GetObjectMap(gmat.Sandbox()))

stop_cond = gmat.Construct('StopCondition', 'StopForSatDays')
print(stop_cond)
stop_param_str = f'{sat.GetName()}.ElapsedSecs'
stop_cond.SetLhsString(stop_param_str)
goal_param_str = '8640.0'
stop_cond.SetRhsString(goal_param_str)
stop_cond.SetSpacecrafts([sat], [sat])

# craft_param = gmat.Construct('Variable', 'SatParam')
# craft_param.SetField('InitialValue', stop_param_str)
# ela = gmat.Construct('ElapsedSecs', 'Sat.ElapsedSecs')
# ela.SetField('Object', sat_name)
# ela.SetRefObject(sat, gmat.SPACECRAFT, sat.GetName())
# ela.Initialize()
# ela_param = gmat.ConfigManager.Instance().GetParameter(ela.GetName())

# stop_param_default = stop_cond.GetStopParameter()
# stop_cond.SetStopParameter(ela_param)
# craft_param = gmat.ConfigManager.Instance().GetParameter(ela.GetName())

# mod = gmat.Moderator.Instance()
# craft_param = mod.CreateParameter('String', stop_param_str)

# stop_param = sat.GetGmatTimeParameter(f'{sat.GetName()}.ElapsedSecs')
stop_param = gmat.Construct('ElapsedSecs', f'{sat.GetName()}.ElapsedSecs')
stop_param.SetField('Object', sat.GetName())
stop_param.SetRefObject(sat, gmat.SPACECRAFT, sat.GetName())
stop_param.SetField('InitialValue', stop_param_str)
stop_param.SetField('Expression', stop_param_str)
stop_param.SetField('Description', stop_param_str)
stop_param.SetField('InitialEpoch', sat.GetState().GetEpoch())
# gmat.Initialize()
# stop_param.SetReference(sat)
stop_param.Initialize()
# stop_param = gmat.Moderator.Instance().GetInternalObject('Sat.ElapsedSecs')
stop_param = gmat.ConfigManager.Instance().GetParameter('Sat.ElapsedSecs')
stop_cond.SetStopParameter(stop_param)
stop_cond.GetStopParameter()
stop_cond.Validate()
stop_cond.Initialize()

pgate.SetObject(stop_cond, gmat.STOP_CONDITION)

goal_val = 8640.0

pgate.SetObject(prop.GetName(), gmat.PROP_SETUP)
pgate.SetObject(sat.GetName(), gmat.SPACECRAFT)
pgate.SetField('StopCondition', [stop_cond.GetName()])
pgate.SetObject(stop_cond.GetName(), gmat.STOP_CONDITION)

print(pgate.GetObjectList())

print(f'pgate Validate: {pgate.Validate()}')
# pgate.Initialize()
# CustomHelp(pgate)

bms = gmat.BeginMissionSequence()

print('\n', pgate.GetGeneratingString())

# print(pgate.TakeAction('CheckStopConditions'))
# print(pgate.TakeAction('PrepareToPropagate'))
print(f'\npgate fields: {gpy.gmat_obj_field_list(pgate)}')
print(f'\nstop_cond fields: {gpy.gmat_obj_field_list(stop_cond)}')

# CustomHelp(pgate)
