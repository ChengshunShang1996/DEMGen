
import KratosMultiphysics
from KratosMultiphysics import *
from KratosMultiphysics.DEMApplication import *
import KratosMultiphysics.DEMApplication as DEM
from KratosMultiphysics.DEMApplication.DEM_analysis_stage import DEMAnalysisStage
from KratosMultiphysics.DEMApplication import DEM_procedures as DEM_procedures
import math
import datetime

class ParticlePackingGenerator(DEMAnalysisStage):

    def __init__(self, model, parameters):
        super().__init__(model, parameters)

    def Initialize(self):
        super().Initialize()
        self.InitializePackingGenerator()  

    def InitializePackingGenerator(self):

        #define the aim porosity
        self.aim_final_packing_porosity = 0.35
        self.aim_container_filling_ratio = 0.8 #this means the inlet will stop when the generated particel's volume occupies [aim_container_filling_ratio * container_volume]
        
        self.container_shape = "cylinder"  #input: "cylinder" or "box"  

        if self.container_shape == "cylinder":
            self.container_radius = 0.0   #modify according to your case
            self.container_height = 0.0   #modify according to your case
            self.container_volume = math.pi * self.container_radius * self.container_radius * self.container_height

        if self.container_shape == "box":
            self.container_lenth  = 0.0   #modify according to your case
            self.container_width  = 0.0   #modify according to your case
            self.container_height = 0.0   #modify according to your case
            self.container_volume = self.container_lenth * self.container_width * self.container_height

        self.final_packing_shape = "cylinder"  #input: "cylinder" or "box" 

        if self.final_packing_shape == "cylinder":
            self.final_packing_radius = 0.0   #modify according to your case
            self.final_packing_height = 0.0   #modify according to your case
            self.final_packing_volume = math.pi * self.final_packing_radius * self.final_packing_radius * self.final_packing_height
            self.final_packing_bottom_center_point = [0, 0, 0]
            self.final_packing_direction = [0, 1, 0]

        if self.final_packing_shape == "box":
            self.final_packing_lenth  = 0.0   #modify according to your case
            self.final_packing_width  = 0.0   #modify according to your case
            self.final_packing_height = 0.0   #modify according to your case
            self.final_packing_volume = self.final_packing_lenth * self.final_packing_width * self.final_packing_height
            self.final_packing_bottom_center_point = [0, 0, 0]
            self.final_packing_direction = [0, 1, 0]

    def RunSolutionLoop(self):

        while self.KeepAdvancingSolutionLoop():
            self.time = self._GetSolver().AdvanceInTime(self.time)
            self.InitializeSolutionStep()
            self._GetSolver().Predict()
            self._GetSolver().SolveSolutionStep()
            self.FinalizeSolutionStep()
            self.OutputSolutionStep()

    def KeepAdvancingSolutionLoop(self):
        
        return self.time < self.end_time


if __name__ == "__main__":

    with open("ProjectParametersDEM.json", 'r') as parameter_file:
        parameters = KratosMultiphysics.Parameters(parameter_file.read())

    model = KratosMultiphysics.Model()
    ParticlePackingGenerator(model, parameters).Run()
