from __future__ import annotations

from load_gmat import gmat
import gmat_py_simple as gpy


class Solver(gpy.GmatObject):
    def __init__(self, obj_type: str, name: str):
        super().__init__(obj_type, name)

    # def __init__(self, solver_type: str, name: str):
    #     self.name = name
    #     self.gmat_obj = gpy.Moderator().CreateSolver(solver_type, name)
    #
    #     # self.gmat_obj.Help()
    #     # pass

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

        :param name:
        :param algorithm:
        :param max_iter:
        :param derivative_method:
        :param show_progress:
        :param report_style:
        :param report_file:
        """

        super().__init__('DifferentialCorrector', name)

        """
        According to DifferentialCorrector.hpp, talk to Vary and Achieve commands via these functions in DC:
            SetSolverResults()
            UpdateSolverGoal()
            UpdateSolverTolerance()
            SetResultValue()
        """

        self.algorithm = algorithm
        # self.SetField('Algorithm', self.algorithm)
        self.SetStringParameter('Algorithm', self.algorithm)

        self.max_iter = max_iter
        # self.SetField('MaximumIterations', self.max_iter)
        self.SetIntegerParameter('MaximumIterations', self.max_iter)

        self.derivative_method = derivative_method
        # self.SetField('DerivativeMethod', self.derivative_method)
        self.SetStringParameter('DerivativeMethod', self.derivative_method)

        self.show_progress = show_progress
        # self.SetField('ShowProgress', self.show_progress)
        self.SetBooleanParameter('ShowProgress', self.show_progress)

        self.report_style = report_style
        # self.SetField('ReportStyle', self.report_style)
        self.SetStringParameter('ReportStyle', self.report_style)  # Enum type

        self.report_file = report_file
        # self.SetField('ReportFile', self.report_file)
        self.SetStringParameter('ReportFile', self.report_file)  # Filename type

        # Variables are set later by Vary/Achieve commands (TODO determine which)

        print(f"\nVariables in DiffCor: {self.GetStringArrayParameter('Variables')}")
        print(f"Goals in DiffCor: {self.GetStringArrayParameter('Goals')}\n")
        pass

        # Set initial variable and goal so object can initialize
        # self.SetStringParameter('Variables', 'PlaceholderVarSetInDiffCorrInit')
        # self.SetStringParameter('Goals', str('PlaceholderGoalSetInDiffCorrInit'))
        #
        # self.Initialize()

        # self.SetStringParameter(self.GetParameterID('Variables'), 'TOI.Element1')
        # self.SetStringParameter(self.GetParameterID('Goals'), str(2.240269210751019))

        # TODO: how to set Goals (string array) field in Help?
        # self.Help()

        # gpy.CustomHelp(self)

        # for i in range(19):
        #     print(f'{i}: {self.gmat_obj.GetParameterText(i)}: {self.gmat_obj.GetParameterTypeString(i)}')

        # print(f'Variables: {self.gmat_obj.GetStringArrayParameter(4)}')

        # TODO bugfix: DifferentialCorrector Initialize throwing error: "Solver subsystem exception: Targeter cannot
        #  initialize: No goals or variables are set."
        # self.Initialize()

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
