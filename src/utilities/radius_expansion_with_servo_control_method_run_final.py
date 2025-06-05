#/////////////////////////////////////////////////
__author__      = "Chengshun Shang (CIMNE)"
__copyright__   = "Copyright (C) 2023-present by Chengshun Shang"
__version__     = "0.0.1"
__maintainer__  = "Chengshun Shang"
__email__       = "cshang@cimne.upc.edu"
__status__      = "development"
__date__        = "Dec 02, 2024"
__license__     = "BSD 2-Clause License"
#/////////////////////////////////////////////////

import time
import sys
import shutil
import math
import numpy as np
import pathlib

import KratosMultiphysics
from KratosMultiphysics import *
from KratosMultiphysics.DEMApplication import *
from KratosMultiphysics.DEMApplication.DEM_analysis_stage import DEMAnalysisStage
from KratosMultiphysics import Logger

if os.path.exists("normalized_kinematic_energy.txt"):
    os.remove("normalized_kinematic_energy.txt")
if os.path.exists("stress_tensor_0.txt"):
    os.remove("stress_tensor_0.txt")
if os.path.exists("granular_temperature_0.txt"):
    os.remove("granular_temperature_0.txt")
if os.path.exists("inletPGDEM.mdpa"):
    os.remove("inletPGDEM.mdpa")

def GetParticleDataFromMdpa(aim_mdpa_file_name):

    p_id = 1
    p_record_nodes = False
    p_record_elements = False
    p_record_radius = False
    p_pram_list = []

    if os.path.isfile(aim_mdpa_file_name):

        with open(aim_mdpa_file_name, 'r') as mdpa_data:

            for line in mdpa_data:

                p_pram_dict = {
                "id" : 0,
                "p_x" : 0.0,
                "p_y" : 0.0,
                "p_z" : 0.0,
                "radius" : 0.0,
                "p_v_x" : 0.0,
                "p_v_y" : 0.0,
                "p_v_z" : 0.0,
                "p_ele_id": 0,
                "p_group_id": 0
                }

                values = [str(s) for s in line.split()]

                if len(values) > 1:
                    if values[0] == 'Begin' and values[1] == 'Nodes':
                        p_record_nodes = True
                        continue
                    elif values[0] == 'End' and values[1] == 'Nodes':
                        p_record_nodes = False

                    if values[0] == 'Begin' and values[1] == 'Elements':
                        p_record_elements = True
                        continue
                    elif values[0] == 'End' and values[1] == 'Elements':
                        p_record_elements = False

                if len(values) > 2:
                    if values[0] == 'Begin' and values[2] == 'RADIUS':
                        p_record_radius = True
                        continue
                if len(values) > 1:
                    if values[0] == 'End' and values[1] == 'NodalData' and p_record_radius == True:
                        p_record_radius = False

                if p_record_nodes:
                    p_pram_dict["id"] = int(values[0])
                    p_pram_dict["p_x"] = float(values[1])
                    p_pram_dict["p_y"] = float(values[2])
                    p_pram_dict["p_z"] = float(values[3])

                if p_record_elements:
                    #only modify the values, not add new one
                    temp_p_pram_dict = next(old_p_pram_dict for old_p_pram_dict in p_pram_list if old_p_pram_dict['id'] == int(values[2]))
                    temp_p_pram_dict["p_ele_id"] = int(values[0])

                if p_record_radius:
                    #only modify the values, not add new one
                    temp_p_pram_dict = next(old_p_pram_dict for old_p_pram_dict in p_pram_list if old_p_pram_dict['id'] == int(values[0]))
                    temp_p_pram_dict["radius"] = float(values[2])

                if not (p_record_elements and p_record_radius):
                    if p_record_nodes:
                        p_pram_list.append(p_pram_dict)
                        p_id = p_id + 1

    p_pram_list = sorted(p_pram_list, key=lambda d: d['id'])

    return p_pram_list

class DEMAnalysisStageWithFlush(DEMAnalysisStage):

    def __init__(self, model, project_parameters, radius_multiplier, ini_p_pram_list, flush_frequency=10.0):
        super().__init__(model, project_parameters)
        self.flush_frequency = flush_frequency
        self.last_flush = time.time()
        self.parameters = parameters
        self.radius_multiplier = radius_multiplier
        self.normalized_kinematic_energy = 1e10
        self.ini_p_pram_list = ini_p_pram_list
        self.start_reset_velocity = False
        self.second_stage_flag = False
        self.is_in_inaccessibale_region2 = False
        self.is_start_servo_control = False

    def Initialize(self):
        super().Initialize()
        self.dt = self.spheres_model_part.ProcessInfo[DELTA_TIME]
        self.final_check_frequency  = int(self.parameters["GraphExportFreq"].GetDouble()/self.parameters["MaxTimeStep"].GetDouble())
        self.final_check_counter = 0
        self.final_check_counter_2 = 0
        self.final_check_counter_reset = 0
        self.measured_stress_list = []
        self.target_packing_density = 0.64

    def ReadMaterialsFile(self):
        adapted_to_current_os_relative_path = pathlib.Path(self.DEM_parameters["solver_settings"]["material_import_settings"]["materials_filename"].GetString())
        materials_file_abs_path = os.path.join(self.main_path, str(adapted_to_current_os_relative_path))
        with open(materials_file_abs_path, 'r') as materials_file:
            self.DEM_material_parameters = Parameters(materials_file.read())

        self.initial_friction_coefficient = self.DEM_material_parameters["material_relations"][0]["Variables"]["DYNAMIC_FRICTION"].GetDouble()
        self.DEM_material_parameters["material_relations"][0]["Variables"]["STATIC_FRICTION"].SetDouble(0.0)
        self.DEM_material_parameters["material_relations"][0]["Variables"]["DYNAMIC_FRICTION"].SetDouble(0.0)

    def SetResetStart(self):

        self.start_reset_velocity = True

    def SetAllParticleVelocityToZero(self):
        for node in self.spheres_model_part.Nodes:
            node.SetSolutionStepValue(VELOCITY_X, 0.0)
            node.SetSolutionStepValue(VELOCITY_Y, 0.0)
            node.SetSolutionStepValue(VELOCITY_Z, 0.0)

    def GetMaximumVelocity(self):
        max_particle_velocity = 0.0
        for node in self.spheres_model_part.Nodes:
            velocity_x = node.GetSolutionStepValue(VELOCITY_X)
            velocity_y = node.GetSolutionStepValue(VELOCITY_Y)
            velocity_z = node.GetSolutionStepValue(VELOCITY_Z)
            velocity_magnitude = (velocity_x * velocity_x + velocity_y * velocity_y + velocity_z * velocity_z)**0.5
            if velocity_magnitude > max_particle_velocity:
                max_particle_velocity = velocity_magnitude
        return max_particle_velocity

    def GetGranularTemperature(self):
        vel_x = []
        vel_y = []
        vel_z = []
        volume = []
        total_volume = 0.0
        for node in self.spheres_model_part.Nodes:
            vol = 4/3*math.pi*node.GetSolutionStepValue(RADIUS)**3
            volume.append(vol)
            vel_x.append(vol*node.GetSolutionStepValue(VELOCITY_X))
            vel_y.append(vol*node.GetSolutionStepValue(VELOCITY_Y))
            vel_z.append(vol*node.GetSolutionStepValue(VELOCITY_Z))
            total_volume += vol
        mean_vel_x = sum(vel_x)/total_volume
        mean_vel_y = sum(vel_y)/total_volume
        mean_vel_z = sum(vel_z)/total_volume

        T_x = 0.0
        T_y = 0.0
        T_z = 0.0
        max_gran_temp = 0.0
        for V,u,v,w in zip(volume,vel_x,vel_y,vel_z):
            T_x += (u/V-mean_vel_x)**2
            T_y += (v/V-mean_vel_y)**2
            T_z += (w/V-mean_vel_z)**2
            T_p = 1/3*((u/V-mean_vel_x)**2 + (v/V-mean_vel_y)**2 + (w/V-mean_vel_z)**2)
            if T_p > max_gran_temp:
                max_gran_temp = T_p
        T_x /= len(vel_x)
        T_y /= len(vel_y)
        T_z /= len(vel_z)

        return (T_x+T_y+T_z)/3, max_gran_temp

    def OutputSolutionStep(self):

        super().OutputSolutionStep()

        if self.final_check_counter == self.final_check_frequency:

            self.final_check_counter = 0

            self.UpdateFinalPackingVolume()
            self.MeasureTotalPackingDensityOfFinalPacking()

            self.normalized_kinematic_energy = self.DEMEnergyCalculator.CalculateNormalizedKinematicEnergy()
            with open("normalized_kinematic_energy.txt", 'a') as file:
                file.write(str(self.time) + ' ' + str(self.normalized_kinematic_energy) + '\n')

            stress_tensor = self.MeasureSphereForGettingGlobalStressTensor()
            mean_stress = (stress_tensor[0][0] + stress_tensor[1][1] + stress_tensor[2][2])/3
            granular_temperature, max_granular_temperature = self.GetGranularTemperature()

            with open("stress_tensor_0.txt", 'a') as file:
                    file.write(str(self.time) + ' ' + str(mean_stress) + ' ' + str(self.final_packing_density) + ' ' \
                               + str(stress_tensor[0][0]) + ' ' + str(stress_tensor[1][1]) + ' ' + str(stress_tensor[2][2])+'\n')

            with open("granular_temperature_0.txt", 'a') as file:
                    file.write(str(self.time) + ' ' + str(granular_temperature) + ' ' + str(max_granular_temperature) + '\n')

            self.measured_stress_list.append(mean_stress)

            if not self.is_start_servo_control:

                if self.start_reset_velocity:

                    self.PrintResultsForGid(self.time)

                    #max_particle_velocity = self.GetMaximumVelocity()

                    #if ((self.normalized_kinematic_energy < 1e-8) and (mean_stress < 5000)) or ((max_particle_velocity < 1e-3) and (mean_stress < 5000)):
                    target_stress = self.parameters["BoundingBoxServoLoadingSettings"]["BoundingBoxServoLoadingStress"].GetVector()
                    target_mean_stress = (target_stress[0] + target_stress[1] + target_stress[2]) / 3
                    if mean_stress < target_mean_stress * 1.2: # (target stress, packing density) in the accessiable region
                        self.second_stage_flag = True
                        self.WriteOutMdpaFileOfParticles("inletPGDEM.mdpa")
                        self.PrintResultsForGid(self.time)
                        self.is_start_servo_control = True
                        self.parameters["BoundingBoxMoveOption"].SetBool(True)
                        self.parameters["BoundingBoxServoLoadingOption"].SetBool(True)
                        for properties in self.spheres_model_part.Properties:
                            for subproperties in properties.GetSubProperties():
                                subproperties[STATIC_FRICTION] = self.initial_friction_coefficient
                                subproperties[DYNAMIC_FRICTION] = self.initial_friction_coefficient
                        #self.copy_files_and_run_show_results()
                        #exit(0)
                    elif self.normalized_kinematic_energy < 1e-8: # (target stress, packing density) in the inaccessiable region (2)
                        self.second_stage_flag = True
                        self.WriteOutMdpaFileOfParticles("inletPGDEM.mdpa")
                        self.PrintResultsForGid(self.time)
                        if mean_stress > target_mean_stress * 1.2:
                            self.is_in_inaccessibale_region2 = True
                        self.is_start_servo_control = True
                        self.parameters["BoundingBoxMoveOption"].SetBool(True)
                        self.parameters["BoundingBoxServoLoadingOption"].SetBool(True)
                        for properties in self.spheres_model_part.Properties:
                            for subproperties in properties.GetSubProperties():
                                subproperties[STATIC_FRICTION] = self.initial_friction_coefficient
                                subproperties[DYNAMIC_FRICTION] = self.initial_friction_coefficient
                        #self.copy_files_and_run_show_results()
                        #exit(0)
                    else:
                        self.SetAllParticleVelocityToZero()
            else:
                mad = 0.0
                target_stress = self.parameters["BoundingBoxServoLoadingSettings"]["BoundingBoxServoLoadingStress"].GetVector()
                if len(self.measured_stress_list) > 5:
                    mad = np.mean([abs(x - target_stress[0]) for x in self.measured_stress_list[-5:]])

                mad_threshold = 0.02 * target_stress[0]
                if mad < mad_threshold and len(self.measured_stress_list) > 5:
                    self.WriteOutMdpaFileOfParticles("inletPGDEM.mdpa")
                    self.copy_files_and_run_show_results()
                    exit(0)
        self.final_check_counter += 1

    def FinalizeSolutionStep(self):
        super().FinalizeSolutionStep()

        if self.parallel_type == "OpenMP":
            now = time.time()
            if now - self.last_flush > self.flush_frequency:
                sys.stdout.flush()
                self.last_flush = now

    def Finalize(self):
        #self.WriteOutMdpaFileOfParticles("inletPGDEM" + str(self.radius_multiplier) + ".mdpa")
        self.WriteOutMdpaFileOfParticles("inletPGDEM.mdpa")
        self.PrintResultsForGid(self.time)
        super().Finalize()

    def PassNormalizedKineticEnergy(self):

        return self.normalized_kinematic_energy

    def MeasureTotalPackingDensityOfFinalPacking(self):

        selected_element_volume = self.MeasureTotalSpheresVolume()

        self.final_packing_density = selected_element_volume / self.final_packing_volume

        print("Currently packing density is {}".format(self.final_packing_density))

    def UpdateFinalPackingVolume(self):

        self.final_packing_volume = (self.BoundingBoxMaxX_update - self.BoundingBoxMinX_update) * \
                                (self.BoundingBoxMaxY_update - self.BoundingBoxMinY_update) * \
                                (self.BoundingBoxMaxZ_update - self.BoundingBoxMinZ_update)

    def WriteOutMdpaFileOfParticles(self, output_file_name):

        if self.second_stage_flag:
            self.clear_old_and_create_new_show_packing_case_folder()
            aim_path_and_name = os.path.join(os.getcwd(), 'show_packing', output_file_name)
        else:
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
            for p_pram_dict in self.ini_p_pram_list:
                f.write(str(p_pram_dict["id"]) + ' ' + ' 0 ' + str(p_pram_dict["radius"] * self.radius_multiplier) + '\n')
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

    def clear_old_and_create_new_show_packing_case_folder(self):

        aim_path = os.path.join(os.getcwd(),'show_packing')

        if os.path.exists(aim_path):
            shutil.rmtree(aim_path, ignore_errors=True)
            os.makedirs(aim_path)
        else:
            os.makedirs(aim_path)

    def copy_seed_files_to_aim_folders(self):

        aim_path = os.path.join(os.getcwd(), 'show_packing')

        seed_file_name_list = ['MaterialsDEM.json', 'ProjectParametersDEM.json', 'inletPGDEM_FEM_boundary.mdpa', 'show_packing.py']
        for seed_file_name in seed_file_name_list:
            seed_file_path_and_name = os.path.join(os.getcwd(), seed_file_name)
            aim_file_path_and_name = os.path.join(aim_path, seed_file_name)

            if seed_file_name == 'ProjectParametersDEM.json':
                with open(seed_file_path_and_name, "r") as f_material:
                    with open(aim_file_path_and_name, "w") as f_material_w:
                        for line in f_material.readlines():
                            if "FinalTime" in line:
                                line = "    \"FinalTime\"                      : " + str(self.dt * 2) + ', \n'
                            elif "\"GraphExportFreq\"" in line:
                                line = "    \"GraphExportFreq\"                : " + str(self.dt) + ', \n'
                            elif "VelTrapGraphExportFreq" in line:
                                line = "    \"VelTrapGraphExportFreq\"         : " + str(self.dt) + ', \n'
                            elif "OutputTimeStep" in line:
                                line = "    \"OutputTimeStep\"                 : " + str(self.dt) + ', \n'
                            f_material_w.write(line)
            else:
                if os.path.exists(seed_file_path_and_name):
                    shutil.copyfile(seed_file_path_and_name, aim_file_path_and_name)

    def copy_files_and_run_show_results(self):

        self.copy_seed_files_to_aim_folders()

        current_path = os.getcwd()
        aim_path = os.path.join(current_path,'show_packing')
        os.chdir(aim_path)
        if os.name == 'nt': # for windows
            os.system("python show_packing.py")
        else: # for linux
            os.system("python3 show_packing.py")
        os.chdir(current_path)

    def SetSecondStageFlag(self):

        self.second_stage_flag = True

if __name__ == "__main__":
    Logger.GetDefaultOutput().SetSeverity(Logger.Severity.INFO)
    radius_multiplier = 1.0
    NormalizedKineticEnergy = 1e8

    shutil.copyfile('inletPGDEM_ini.mdpa', 'inletPGDEM.mdpa')

    ini_p_pram_list = GetParticleDataFromMdpa('inletPGDEM_ini.mdpa')

    while radius_multiplier < 2.2:
        if os.path.exists('inletPG_Post_Files'):
            shutil.rmtree('inletPG_Post_Files', ignore_errors=True)
        with open("ProjectParametersDEM.json", 'r') as parameter_file:
            parameters = KratosMultiphysics.Parameters(parameter_file.read())

        #if radius_multiplier >= 2.1:
        #    parameters["FinalTime"].SetDouble(10)
        global_model = KratosMultiphysics.Model()
        MyDemCase = DEMAnalysisStageWithFlush(global_model, parameters, radius_multiplier, ini_p_pram_list)
        #MyDemCase.Run()
        MyDemCase.Initialize()
        MyDemCase.RunSolutionLoop()
        NormalizedKineticEnergy = MyDemCase.PassNormalizedKineticEnergy()
        MyDemCase.Finalize()
        #os.rename("inletPG_Post_Files", "inletPG_Post_Files_" + str(radius_multiplier))
        print(' ')
        print("----------------------------Loop {} finished!".format(radius_multiplier))
        print(' ')
        radius_multiplier += 0.2
        radius_multiplier = round(radius_multiplier, 1)

    radius_multiplier = 2.0

    if os.path.exists('inletPG_Post_Files'):
        shutil.rmtree('inletPG_Post_Files', ignore_errors=True)
    with open("ProjectParametersDEM.json", 'r') as parameter_file:
        parameters = KratosMultiphysics.Parameters(parameter_file.read())

    parameters["FinalTime"].SetDouble(10)
    global_model = KratosMultiphysics.Model()
    MyDemCase = DEMAnalysisStageWithFlush(global_model, parameters, radius_multiplier, ini_p_pram_list)
    MyDemCase.Initialize()
    MyDemCase.SetResetStart()
    MyDemCase.RunSolutionLoop()
    #NormalizedKineticEnergy = MyDemCase.PassNormalizedKineticEnergy()
    MyDemCase.Finalize()

