from __future__ import annotations

from load_gmat import gmat
import gmat_py_simple as gpy


class DifferentialCorrector:
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

        """
        According to DifferentialCorrector.hpp, talk to Vary and Achieve commands via these functions in DC:
            SetSolverResults()
            UpdateSolverGoal()
            UpdateSolverTolerance()
            SetResultValue()
        """

        self.name = name
        self.gmat_obj = gmat.Construct('DifferentialCorrector', name)

        self.algorithm = algorithm
        self.SetField('Algorithm', self.algorithm)

        self.max_iter = max_iter
        self.SetField('MaximumIterations', self.max_iter)

        self.derivative_method = derivative_method
        self.SetField('DerivativeMethod', self.derivative_method)

        self.show_progress = show_progress
        self.SetField('ShowProgress', self.show_progress)

        self.report_style = report_style
        self.SetField('ReportStyle', self.report_style)

        self.report_file = report_file
        self.SetField('ReportFile', self.report_file)

        # TODO: how to set Goals (string array) field in Help?
        # self.Help()

        # gpy.CustomHelp(self)

        # for i in range(19):
        #     print(f'{i}: {self.gmat_obj.GetParameterText(i)}: {self.gmat_obj.GetParameterTypeString(i)}')

        # print(f'Variables: {self.gmat_obj.GetStringArrayParameter(4)}')

        # TODO bugfix: DifferentialCorrector Initialize throwing error: "Solver subsystem exception: Targeter cannot
        #  initialize: No goals or variables are set."
        # self.Initialize()

    def Help(self):
        return self.gmat_obj.Help()

    def Initialize(self):
        return self.gmat_obj.Initialize()

    def SetField(self, field: str, value: str | int | float | bool) -> bool:
        return self.gmat_obj.SetField(field, value)
