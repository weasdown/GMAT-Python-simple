from __future__ import annotations

from load_gmat import gmat
import gmat_py_simple as gpy


class DifferentialCorrector:
    def __init__(self, name: str, algorithm: str = 'NewtonRaphson', max_iter: int = 25,
                 derivative_method: str = 'ForwardDifference', show_progress: bool = True, report_style: str = 'Normal',
                 report_file: str = 'DifferentialCorrectorDC1.data'):
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

    def Help(self):
        return self.gmat_obj.Help()

    def SetField(self, field: str, value: str | int | float | bool) -> bool:
        return self.gmat_obj.SetField(field, value)
