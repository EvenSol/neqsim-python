
import sys
if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol

import java.io
import java.lang
import java.util
import typing



class SulfurThermodynamics:
    @staticmethod
    def calculateAllotropeMoleFractions(double: float, double2: float) -> java.util.Map[java.lang.String, float]: ...
    @staticmethod
    def calculateDewPointTemperatureK(double: float) -> float: ...
    @staticmethod
    def calculateMeanSulfurAtomsPerMolecule(double: float, double2: float) -> float: ...
    @staticmethod
    def calculateS8IdealGasHeatCapacityJPerMolK(double: float) -> float: ...
    @staticmethod
    def calculateVapourPressureBar(double: float) -> float: ...
    @staticmethod
    def getSpeciesData(int: int) -> 'SulfurThermodynamics.SpeciesData': ...
    class SpeciesData(java.io.Serializable):
        def getEnthalpyJPerMolAt298K(self) -> float: ...
        def getEntropyJPerMolKAt298K(self) -> float: ...
        def getHeatCapacityJPerMolK(self) -> float: ...
        def getName(self) -> java.lang.String: ...
        def getSulfurAtoms(self) -> int: ...


class __module_protocol__(Protocol):
    # A module protocol which reflects the result of ``jp.JPackage("jneqsim.thermo.util.sulfur")``.

    SulfurThermodynamics: typing.Type[SulfurThermodynamics]
