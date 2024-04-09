import time
import sys
import os

import KratosMultiphysics
from KratosMultiphysics import *
from KratosMultiphysics.DEMApplication import *
from KratosMultiphysics.DEMApplication.DEM_analysis_stage import DEMAnalysisStage
from KratosMultiphysics import Logger

class DEMAnalysisStageWithFlush(DEMAnalysisStage):

    def __init__(self, model, project_parameters, flush_frequency=10.0):
        super().__init__(model, project_parameters)
        self.flush_frequency = flush_frequency
        self.last_flush = time.time()
        self.parameters = parameters
        if os.path.exists("normalized_kinematic_energy.txt"):
            os.remove("normalized_kinematic_energy.txt")
        if os.path.exists("stress_tensor_modulus.txt"):
            os.remove("stress_tensor_modulus.txt")

    def Initialize(self):
        super().Initialize()
        self.dt = self.spheres_model_part.ProcessInfo[DELTA_TIME]
        self.final_check_frequency  = int(self.parameters["GraphExportFreq"].GetDouble()/self.parameters["MaxTimeStep"].GetDouble())
        self.final_check_counter = 0
    
    def OutputSolutionStep(self):
        super().OutputSolutionStep()

        if self.final_check_counter == self.final_check_frequency:

            self.final_check_counter = 0
            
            normalized_kinematic_energy = self.DEMEnergyCalculator.CalculateNormalizedKinematicEnergy()
            with open("normalized_kinematic_energy.txt", 'a') as file:
                file.write(str(self.time) + ' ' + str(normalized_kinematic_energy) + '\n')

            side_length = 0.005
            center_x = 0.0
            center_y = 0.0
            center_z = 0.0
            stress_tensor_modulus = self.MeasureCubicForGettingPackingProperties(side_length, center_x, center_y, center_z, "stress_tensor_modulus")
            with open("stress_tensor_modulus.txt", 'a') as file:
                file.write(str(self.time) + ' ' + str(stress_tensor_modulus) + '\n')

            # n = 5e6;   Rate 100 = 1 / (Delta t * n); t = Delta t * n
            expansion_stop_time = 0.001454545
            if self.time > expansion_stop_time and normalized_kinematic_energy < 1e-8:
                self.PrintResultsForGid(self.time)
                exit(0)

        self.final_check_counter += 1
    
    def FinalizeSolutionStep(self):
        super().FinalizeSolutionStep()

        if self.parallel_type == "OpenMP":
            now = time.time()
            if now - self.last_flush > self.flush_frequency:
                sys.stdout.flush()
                self.last_flush = now

if __name__ == "__main__":
    Logger.GetDefaultOutput().SetSeverity(Logger.Severity.INFO)
    with open("ProjectParametersDEM.json", 'r') as parameter_file:
        parameters = KratosMultiphysics.Parameters(parameter_file.read())

    global_model = KratosMultiphysics.Model()
    DEMAnalysisStageWithFlush(global_model, parameters).Run()
