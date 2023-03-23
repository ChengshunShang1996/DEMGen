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

class ParticlePackingGenerator(DEMAnalysisStage):

    def __init__(self, model, parameters):
        super().__init__(model, parameters)

    def Initialize(self):
        super().Initialize()
        self.InitializePackingGenerator() 
        self.GetInitialDemSphereVolume()
        self.dt = self.spheres_model_part.ProcessInfo[DELTA_TIME]

    def InitializePackingGenerator(self):

        #define the aim porosity
        self.aim_final_packing_porosity = 0.35
        self.aim_container_filling_ratio = 0.8 #this means the inlet will stop when the generated particel's volume occupies [aim_container_filling_ratio * container_volume]
        self.container_filling_ratio = 0.0
        self.initial_sphere_volume = 0.0
        
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
    
    def FinalizeSolutionStep(self):
        super().FinalizeSolutionStep()
        self.CalculateFillingRatioAndSetInletStop()

    def GetInitialDemSphereVolume(self):

        for element in self.spheres_model_part.Elements:
            r = element.GetNode(0).GetSolutionStepValue(RADIUS)
            element_volume = 4/3 * math.pi * r * r * r
            self.initial_sphere_volume += element_volume

    def CalculateFillingRatioAndSetInletStop(self):
        
        #calculte container filling ratio
        total_element_volume = 0.0
        for element in self.spheres_model_part.Elements:
            r = element.GetNode(0).GetSolutionStepValue(RADIUS)
            element_volume = 4/3 * math.pi * r * r * r
            total_element_volume += element_volume

        generated_element_volume = total_element_volume - self.initial_sphere_volume
        self.container_filling_ratio = generated_element_volume / self.container_volume

        #set Inlet stop time
        if self.container_filling_ratio > self.aim_container_filling_ratio:

            for submp in self.dem_inlet_model_part.SubModelParts:
                if submp.Has(INLET_STOP_TIME):
                    submp[INLET_STOP_TIME] = self.time + self.dt

if __name__ == "__main__":

    with open("ProjectParametersDEM.json", 'r') as parameter_file:
        parameters = KratosMultiphysics.Parameters(parameter_file.read())

    model = KratosMultiphysics.Model()
    ParticlePackingGenerator(model, parameters).Run()
