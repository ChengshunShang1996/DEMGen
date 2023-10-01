#/////////////////////////////////////////////////
#// Main author: Chengshun Shang (CIMNE)
#// Email: chengshun.shang1996@gmail.com
#// Date: March 2023
#/////////////////////////////////////////////////

import KratosMultiphysics
from KratosMultiphysics import *
from KratosMultiphysics.DEMApplication import *
from KratosMultiphysics.DEMApplication.DEM_analysis_stage import DEMAnalysisStage
from KratosMultiphysics.DEMApplication import DEM_procedures as DEM_procedures
import math
from sys import exit

class FindTheBestBondSearchRadius(DEMAnalysisStage):

    def __init__(self, model, parameters):
        super().__init__(model, parameters)
        self.parameters = parameters

    def Initialize(self):
        super().Initialize()
        self.dt = self.spheres_model_part.ProcessInfo[DELTA_TIME]
        self.final_check_frequency  = int(self.parameters["GraphExportFreq"].GetDouble()/self.parameters["MaxTimeStep"].GetDouble())

    def RunSolutionLoop(self):

        while self.KeepAdvancingSolutionLoop():
            self.time = self._GetSolver().AdvanceInTime(self.time)
            self.InitializeSolutionStep()
            self._GetSolver().Predict()
            self._GetSolver().SolveSolutionStep()
            self.FinalizeSolutionStep()
            self.OutputSolutionStep()
        
        return self.measured_bond_volume

    def KeepAdvancingSolutionLoop(self):
        
        return self.time < self.end_time
    
    def FinalizeSolutionStep(self):
        self.MeasureBondVolume()
        super().FinalizeSolutionStep()

    def Finalize(self):
        self.PrintResultsForGid(self.time)
        super().Finalize()

    def MeasureBondVolume(self):
        self.measured_bond_volume = 0.0


if __name__ == "__main__":

    with open("ProjectParametersDEM.json", 'r') as parameter_file:
        parameters = KratosMultiphysics.Parameters(parameter_file.read())

    model = KratosMultiphysics.Model()
    MyCase = FindTheBestBondSearchRadius(model, parameters)

    aim_bond_volume = 10
    particle_radius_max = 0.0001
    current_bond_volume_difference = 1e5
    bond_volume_difference_tolerance = 0.1

    #Binary Search Algorithm
    low = 0.0
    high = 10 * particle_radius_max
    loop_cnt = 0
    is_success = True

    while current_bond_volume_difference > bond_volume_difference_tolerance:

        mid = (low + high) / 2
        parameters["SearchToleranceForBondsCreation"].SetDouble(mid)

        MyCase.Initialize()
        measured_bond_volume = MyCase.RunSolutionLoop()
        current_bond_volume_difference = abs(measured_bond_volume - aim_bond_volume)

        if measured_bond_volume == aim_bond_volume:
            print("SearchToleranceForBondsCreation shouled be {}".format(mid))
            break
        elif measured_bond_volume < aim_bond_volume:
            low = mid
        elif measured_bond_volume > aim_bond_volume:
            high = mid

        MyCase.Finalize()

        loop_cnt += 1

        if loop_cnt > 1000:
            print("Too much loop, please check your parameters.")
            is_success = False
            break
        
    if is_success:
        print("SearchToleranceForBondsCreation shouled be {}".format(mid))
