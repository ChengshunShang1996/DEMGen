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
        self.parameters = parameters

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
        self.final_packing_porosity = 0.0
        self.generator_process_marker_phase_1 = True  # Phase 1: Generate initial particle packing
        self.generator_process_marker_phase_2 = False # Phase 2: Operate on initial particle packing for getting a desired porosity
        self.generator_process_marker_phase_3 = False # Phase 3: Get the final particle packing
        self.is_operations_running = False
        
        self.container_shape = "cylinder"  #input: "cylinder" or "box"  

        if self.container_shape == "cylinder":
            self.container_radius = 0.0   #modify according to your case
            self.container_height = 0.0   #modify according to your case
            self.container_volume = math.pi * self.container_radius * self.container_radius * self.container_height

        if self.container_shape == "box":
            self.container_lenth  = 0.0   #modify according to your case
            self.container_width  = 0.0   #modify according to your case
            self.container_height = 0.0   #modify according to your casºe
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

        print("********************Stage 1*************************")

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
        
        if self.generator_process_marker_phase_1:
            self.CalculateFillingRatioAndSetInletStop()

        if self.generator_process_marker_phase_2:
            self.MeasureLocalPorosityOfFinalPacking()
            self.MeasureTotalPorosityOfFinalPacking()
            if self.final_packing_porosity > (1 - 0.03) * self.aim_final_packing_porosity and self.final_packing_porosity < (1 + 0.03) * self.aim_final_packing_porosity:
                self.generator_process_marker_phase_2 = False
                self.generator_process_marker_phase_3 = True
                print("********************Stage 3*************************")
            else:
                if not self.is_operations_running:
                    self.OperationsOnParticlePacking()

        if self.generator_process_marker_phase_3:
            pass

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

            self.generator_process_marker_phase_1 = False
            self.generator_process_marker_phase_2 = True
            print("********************Stage 2*************************")

    def MeasureLocalPorosityOfFinalPacking(self):
        pass

    def MeasureTotalPorosityOfFinalPacking(self):
        
        selected_element_volume = 0.0
        for element in self.spheres_model_part.Elements:
            node = element.GetNode(0)
            r = node.GetSolutionStepValue(RADIUS)
            x = node.X
            y = node.Y
            z = node.Z
            is_inside_the_final_packing = self.CheckInsideFinalPackingOrNot(x,y,z)
            if is_inside_the_final_packing:
                element_volume = 4/3 * math.pi * r * r * r
                selected_element_volume += element_volume

        self.final_packing_porosity = 1 - (selected_element_volume / self.container_volume)

        return self.final_packing_porosity

    def CheckInsideFinalPackingOrNot(self, x,y,z):

        #TODO: final_packing_direction should be included
        
        if self.final_packing_shape == "cylinder":

            if y >= self.final_packing_bottom_center_point[1] and y <= self.final_packing_bottom_center_point[1] + self.final_packing_height:
                if (self.final_packing_bottom_center_point[0] - x)**2 + (self.final_packing_bottom_center_point[2] - z)**2 < self.final_packing_radius * self.final_packing_radius:
                    return True
            else:
                return False

        if self.final_packing_shape == "box":

            if x > self.final_packing_bottom_center_point[0] - 0.5 * self.final_packing_lenth and x < self.final_packing_bottom_center_point[0] + 0.5 * self.final_packing_lenth:
                if y >= self.final_packing_bottom_center_point[1] and y <= self.final_packing_bottom_center_point[1] + self.final_packing_height:
                    if z > self.final_packing_bottom_center_point[2] - 0.5 * self.final_packing_width and z < self.final_packing_bottom_center_point[2] + 0.5 * self.final_packing_width:
                        return True
            else:
                return False
    
    def OperationsOnParticlePacking(self):
        
        print("*******Packing Operations*********")
        
        if self.final_packing_porosity > (1 + 0.03) * self.aim_final_packing_porosity:

            print("You can input a number to achieve:")
            print("1. inverte")
            print("2. compressing")

            selected_operation = input("Please input the number of the operation: ")

            #inverte operation
            if selected_operation == "1":
                
                number_of_operation = input("Please input the amount of operations (the number should be an even):")
                
                operation_counter = 0
                while operation_counter < number_of_operation:
                    self.spheres_model_part.ProcessInfo[GRAVITY] *= -1
                    self.is_operations_running = True


            #compressing operation
            if selected_operation == "2":
                pass

        if self.final_packing_porosity < (1 - 0.03) * self.aim_final_packing_porosity:
            
            print("Porosity is lower than aim value.")
            print("Some particles will be deleted!")
                
            delete_particle_count = 0
            while self.final_packing_porosity < (1 - 0.03) * self.aim_final_packing_porosity:

                self.RandomDeleteAParticle()
                delete_particle_count += 1
                self.MeasureTotalPorosityOfFinalPacking(self)
            print("{} particles have been deleted.".format(delete_particle_count))
            self.generator_process_marker_phase_2 = False
            self.generator_process_marker_phase_3 = True
            print("********************Stage 3*************************")

    def RandomDeleteAParticle(self):
        pass

if __name__ == "__main__":

    with open("ProjectParametersDEM.json", 'r') as parameter_file:
        parameters = KratosMultiphysics.Parameters(parameter_file.read())

    model = KratosMultiphysics.Model()
    ParticlePackingGenerator(model, parameters).Run()
