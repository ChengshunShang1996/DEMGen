import time
import sys
import os
import math
import numpy as np

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
        if os.path.exists("stress_tensor_zz.txt"):
            os.remove("stress_tensor_zz.txt")
        if os.path.exists("time_v_a.txt"):
            os.remove("time_v_a.txt")
        if os.path.exists("stress_tensor_0.txt"):
            os.remove("stress_tensor_0.txt")
        if os.path.exists("inletPGDEM_post_1.mdpa"):
            os.remove("inletPGDEM_post_1.mdpa")
        if os.path.exists("inletPGDEM_non-converge.mdpa"):
            os.remove("inletPGDEM_non-converge.mdpa")

    def Initialize(self):
        super().Initialize()
        self.dt = self.spheres_model_part.ProcessInfo[DELTA_TIME]
        self.final_check_frequency  = int(self.parameters["GraphExportFreq"].GetDouble()/self.parameters["MaxTimeStep"].GetDouble())
        self.final_check_counter = 0
        self.final_packing_lenth_ini = self.parameters["BoundingBoxMaxX"].GetDouble() - self.parameters["BoundingBoxMinX"].GetDouble()
        self.final_packing_width_ini = self.parameters["BoundingBoxMaxZ"].GetDouble() - self.parameters["BoundingBoxMinZ"].GetDouble()
        self.final_packing_height_ini = self.parameters["BoundingBoxMaxY"].GetDouble() - self.parameters["BoundingBoxMinY"].GetDouble()
        self.final_packing_volume = self.final_packing_lenth_ini * self.final_packing_width_ini * self.final_packing_height_ini
        self.update_bounding_box_freq = self.parameters["GraphExportFreq"].GetDouble()
        self.measured_stress_list = []
        self.first_step = True
        self.target_porosity = 0.3905
        self.ZeroFrictionPhase = False
        self.initial_friction_coefficient = self.DEM_material_parameters["material_relations"][0]["Variables"]["DYNAMIC_FRICTION"].GetDouble()
        print("The initial friction coefficient is {}".format(self.initial_friction_coefficient))
    
    def OutputSolutionStep(self):
        super().OutputSolutionStep()

        if self.final_check_counter == self.final_check_frequency:

            self.final_check_counter = 0
            
            self.UpdateFinalPackingVolume()
            self.MeasureTotalPorosityOfFinalPacking()

            normalized_kinematic_energy = self.DEMEnergyCalculator.CalculateNormalizedKinematicEnergy()
            with open("normalized_kinematic_energy.txt", 'a') as file:
                file.write(str(self.time) + ' ' + str(normalized_kinematic_energy) + '\n')

            stress_tensor = self.MeasureSphereForGettingGlobalStressTensor()
            mean_stress = (stress_tensor[0][0]+stress_tensor[1][1]+stress_tensor[2][2])/3
            if self.first_step:
                with open("stress_tensor_0.txt", 'a') as file:
                    file.write(str(self.time) + ' ' + str(mean_stress) + ' ' + str(self.final_packing_porosity) + ' ' + str(stress_tensor[0][0]) + ' ' + str(stress_tensor[1][1]) + ' ' + str(stress_tensor[2][2])+'\n')
            else:
                with open("stress_tensor_zz.txt", 'a') as file:
                    file.write(str(self.time) + ' ' + str(mean_stress) + ' ' + str(self.final_packing_porosity) + ' ' + str(stress_tensor[0][0]) + ' ' + str(stress_tensor[1][1]) + ' ' + str(stress_tensor[2][2])+'\n')
            
            self.measured_stress_list.append(mean_stress)
            
            with open("time_v_a.txt", 'a') as file:
                file.write(str(self.time) + ' ' + str(self.bounding_box_move_velocity[0]) + ' ' + str(self.bounding_box_move_velocity[1]) + ' ' + str(self.bounding_box_move_velocity[2]) +'\n')

            if self.first_step:
                mad = 0.0
                mean = 0.0
                mean_bias = 0.0
                target_stress = self.parameters["BoundingBoxServoLoadingSettings"]["BoundingBoxServoLoadingStress"].GetVector()
                if len(self.measured_stress_list) > 5:
                    mad = np.mean([abs(x - target_stress[0]) for x in self.measured_stress_list[-5:]])
                    if len(self.measured_stress_list) > 10:
                        mean = np.mean(self.measured_stress_list[-10:])
                        mean_bias = np.mean([abs(x - mean) for x in self.measured_stress_list[-10:]])
                
                if self.ZeroFrictionPhase:
                    for properties in self.spheres_model_part.Properties:
                        for subproperties in properties.GetSubProperties():
                            subproperties[STATIC_FRICTION] = self.initial_friction_coefficient
                            subproperties[DYNAMIC_FRICTION] = self.initial_friction_coefficient

                mad_threshold = 0.02 * target_stress[0]
                mean_bias_threshold = 0.01 * mean
                if mad < mad_threshold and len(self.measured_stress_list) > 5:
                    print("The stress is stable, and the simulation reaches to the 2nd phase.")
                    if abs(self.final_packing_porosity - self.target_porosity) < 0.0001:
                        self.WriteOutMdpaFileOfParticles("inletPGDEM_post_1.mdpa")
                        self.parameters["BoundingBoxServoLoadingSettings"]["BoundingBoxServoLoadingStress"].SetVector([0.0, 1e10, 0.0])
                        self.parameters["BoundingBoxMoveOptionDetail"].SetVector([0, 0, 0, 0, 1, 0])
                        self.first_step = False
                    else:
                        for properties in self.spheres_model_part.Properties:
                            for subproperties in properties.GetSubProperties():
                                subproperties[STATIC_FRICTION] = 0.0
                                subproperties[DYNAMIC_FRICTION] = 0.0
                        self.ZeroFrictionPhase = True       
                #elif abs(mean_bias) < mean_bias_threshold and len(self.measured_stress_list) > 10:
                #    print("The stress is stable, but it can not reach the target value.")
                #    self.WriteOutMdpaFileOfParticles("inletPGDEM_non-converge.mdpa")
                #    exit(0)

            else:
                if stress_tensor[1][1] > 1e8:
                    print("The simulation end.")
                    exit(0)

        self.final_check_counter += 1
    
    def FinalizeSolutionStep(self):
        super().FinalizeSolutionStep()

        if self.parallel_type == "OpenMP":
            now = time.time()
            if now - self.last_flush > self.flush_frequency:
                sys.stdout.flush()
                self.last_flush = now

    def MeasureTotalPorosityOfFinalPacking(self):
        
        selected_element_volume = 0.0
        for node in self.spheres_model_part.Nodes:
            r = node.GetSolutionStepValue(RADIUS)
            element_volume = 4/3 * math.pi * r * r * r
            selected_element_volume += element_volume

        self.final_packing_porosity = 1 - (selected_element_volume / self.final_packing_volume)

        print("Currently porosity is {}".format(self.final_packing_porosity))

        #return self.final_packing_porosity
    
    def UpdateFinalPackingVolume(self):
         
        #self.final_packing_lenth_ini -= 2 * self.periodic_boundary_move_inwards_velocity * self.update_bounding_box_freq
        #self.final_packing_width_ini -= 2 * self.periodic_boundary_move_inwards_velocity * self.update_bounding_box_freq
        #self.final_packing_height_ini -= self.periodic_boundary_move_inwards_velocity * self.update_bounding_box_freq / 50.0
        self.final_packing_volume = (self.BoundingBoxMaxX_update - self.BoundingBoxMinX_update) * \
                                (self.BoundingBoxMaxY_update - self.BoundingBoxMinY_update) * \
                                (self.BoundingBoxMaxZ_update - self.BoundingBoxMinZ_update)

    def WriteOutMdpaFileOfParticles(self, output_file_name):

        aim_path_and_name = os.path.join(os.getcwd(), output_file_name)
        
        with open(aim_path_and_name,'w') as f:
            # write the particle information
            f.write("Begin ModelPartData \n //  VARIABLE_NAME value \n End ModelPartData \n \n Begin Properties 0 \n End Properties \n \n")
            f.write("Begin Nodes\n")
            for node in self.spheres_model_part.Nodes:
                f.write(str(node.Id) + ' ' + str(node.X) + ' ' + str(node.Y) + ' ' + str(node.Z) + '\n')
            f.write("End Nodes \n \n")

            f.write("Begin Elements SphericParticle3D// GUI group identifier: Body \n")
            for element in self.spheres_model_part.Elements:
                f.write(str(element.Id) + ' ' + ' 0 ' + str(element.GetNode(0).Id) + '\n')
            f.write("End Elements \n \n")

            f.write("Begin NodalData RADIUS // GUI group identifier: Body \n")
            for node in self.spheres_model_part.Nodes:
                f.write(str(node.Id) + ' ' + ' 0 ' + str(node.GetSolutionStepValue(RADIUS)) + '\n')
            f.write("End NodalData \n \n")

            ''' only works for continuum DEM calculation
            f.write("Begin NodalData COHESIVE_GROUP // GUI group identifier: Body \n")
            for p_pram_dict in p_pram_list:
                f.write(str(p_pram_dict["id"]) + ' ' + ' 0 ' + " 1 " + '\n')
            f.write("End NodalData \n \n")

            f.write("Begin NodalData SKIN_SPHERE \n End NodalData \n \n")
            '''

            f.write("Begin SubModelPart DEMParts_Body // Group Body // Subtree DEMParts \n Begin SubModelPartNodes \n")
            for node in self.spheres_model_part.Nodes:
                f.write(str(node.Id) + '\n')
            f.write("End SubModelPartNodes \n Begin SubModelPartElements \n ")
            for element in self.spheres_model_part.Elements:
                f.write(str(element.Id) + '\n')
            f.write("End SubModelPartElements \n")
            f.write("Begin SubModelPartConditions \n End SubModelPartConditions \n End SubModelPart \n \n")

            f.close()

        print("Successfully write out GID DEM.mdpa file!")

if __name__ == "__main__":
    Logger.GetDefaultOutput().SetSeverity(Logger.Severity.INFO)
    with open("ProjectParametersDEM.json", 'r') as parameter_file:
        parameters = KratosMultiphysics.Parameters(parameter_file.read())

    global_model = KratosMultiphysics.Model()
    DEMAnalysisStageWithFlush(global_model, parameters).Run()
