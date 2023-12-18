from __future__ import annotations
from typing import Type

from load_gmat import gmat
from gmat_py_simple import GmatCommand


class Moderator:
    def __init__(self):
        self.gmat_obj = gmat.Moderator.Instance()

    def Initialize(self):
        self.gmat_obj.Initialize()

    def GetRunState(self):
        rs = self.gmat_obj.GetRunState()
        if rs == 10000:
            return 'IDLE', 10000
        elif rs == 10001:
            return 'RUNNING', 10001
        elif rs == 10002:
            return 'PAUSED', 10002
        else:
            raise Exception(f'Run state not recognised: {rs}')

    def GetDetailedRunState(self):
        drs = self.gmat_obj.GetDetailedRunState()
        if drs == 10000:
            return 'IDLE'
        elif drs == 10001:
            return 'RUNNING'
        elif drs == 10002:
            return 'PAUSED'
        # TODO: add options for optimizer state etc
        else:
            raise Exception(f'Detailed run state not recognised: {drs}')

    def GetSandbox(self):
        return self.gmat_obj.GetSandbox()

    def GetConfiguredObjectMap(self):
        return self.gmat_obj.GetConfiguredObjectMap()

    def CreateDefaultCommand(self, command_type: str = 'Propagate', name: str = ''):
        return self.gmat_obj.CreateDefaultCommand(command_type, name)

    def GetFirstCommand(self):
        return self.gmat_obj.GetFirstCommand()

    def InsertCommand(self, command_to_insert: GmatCommand, preceding_command: GmatCommand):
        return self.gmat_obj.InsertCommand(command_to_insert, preceding_command)

    def AppendCommand(self, command_to_append: Type[GmatCommand]):
        return self.gmat_obj.AppendCommand(command_to_append)

    def RunMission(self):
        return self.gmat_obj.RunMission()
