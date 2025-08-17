from __future__ import annotations

# from load_gmat import gmat
from gmat_py_simple.load_gmat import gmat
import gmat_py_simple as gpy


class Solver(gpy.GmatObject):
    def __init__(self, obj_type: str, name: str):
        super().__init__(obj_type, name)

    def GetParameterID(self, param_name: str) -> int:
        return gpy.extract_gmat_obj(self).GetParameterID(param_name)

    def GetStringArrayParameter(self, param_id: int) -> tuple:
        return gpy.extract_gmat_obj(self).GetStringArrayParameter(param_id)

    def SetBooleanParameter(self, param: str | int, value: bool) -> bool:
        return gpy.GmatCommand.SetBooleanParameter(gpy.extract_gmat_obj(self), param, value)

    def SetIntegerParameter(self, param: str | int, value: int) -> bool:
        return gpy.GmatCommand.SetIntegerParameter(gpy.extract_gmat_obj(self), param, value)

    def SetStringParameter(self, param: str | int, value: str) -> bool:
        if isinstance(param, str):
            param = self.GetParameterID(param)
        return gpy.extract_gmat_obj(self).SetStringParameter(param, value)


class DifferentialCorrector(Solver):
    def __init__(self, name: str, algorithm: str = 'NewtonRaphson', max_iter: int = 25,
                 derivative_method: str = 'ForwardDifference', show_progress: bool = True, report_style: str = 'Normal',
                 report_file: str = 'DifferentialCorrectorDC1.data'):
        """
        Create a DifferentialCorrector object used to iterate a variable.
        :param name:
        :param algorithm:
        :param max_iter:
        :param derivative_method:
        :param show_progress:
        :param report_style:
        :param report_file:
        """

        super().__init__('DifferentialCorrector', name)

        self.algorithm = algorithm
        self.SetStringParameter('Algorithm', self.algorithm)

        self.max_iter = max_iter
        self.SetIntegerParameter('MaximumIterations', self.max_iter)

        self.derivative_method = derivative_method
        self.SetStringParameter('DerivativeMethod', self.derivative_method)

        self.show_progress = show_progress
        self.SetBooleanParameter('ShowProgress', self.show_progress)

        self.report_style = report_style
        self.SetStringParameter('ReportStyle', self.report_style)  # Enum type

        self.report_file = report_file
        self.SetStringParameter('ReportFile', self.report_file)  # Filename type

        # Variables are set later by Vary and Achieve commands

    def GetStringParameter(self, param: str | int) -> str:
        return gpy.GmatCommand.GetStringParameter(gpy.extract_gmat_obj(self), param)

    def GetStringArrayParameter(self, param: str | int) -> tuple:
        return gpy.GmatCommand.GetStringArrayParameter(gpy.extract_gmat_obj(self), param)

    def Help(self):
        return self.gmat_obj.Help()

    def Initialize(self):
        return self.gmat_obj.Initialize()

    def SetField(self, field: str, value: str | int | float | bool) -> bool:
        return self.gmat_obj.SetField(field, value)

    def SetSolverVariables(self, var_data: list[float | int], var_name: str) -> bool:
        return gpy.extract_gmat_obj(self).SetSolverVariables(var_data, var_name)

    def UpdateSolverGoal(self, goal_id: int, value: int | float) -> bool:
        return gpy.extract_gmat_obj(self).UpdateSolverGoal(goal_id, value)
