#/////////////////////////////////////////////////
__author__      = "Chengshun Shang (CIMNE)"
__copyright__   = "Copyright (C) 2023-present by Chengshun Shang"
__version__     = "0.0.1"
__maintainer__  = "Chengshun Shang"
__email__       = "cshang@cimne.upc.edu"
__status__      = "development"
__date__        = "August 2, 2023"
__license__     = "BSD 2-Clause License"
#/////////////////////////////////////////////////

import os
import random
import shutil
import math
from KratosMultiphysics import *
from KratosMultiphysics.DEMApplication import *

class CreateParticlesInsideOfADomain():

    def __init__(self) -> None:  

        self.clear_old_cases_folder()

    def Initialize(self, RVE_size, domain_scale_multiplier, packing_cnt, ini_path, try_packing_density = 0.0):

        self.particle_list = []
        self.particle_list_left = []
        self.particle_list_right = []
        self.particle_list_top = []
        self.particle_list_bottom = []
        self.particle_list_front = []
        self.particle_list_behind = []
        self.particle_list_side = []

        RVE_length_x = RVE_size[0]
        RVE_length_y = RVE_size[1]
        RVE_length_z = RVE_size[2]

        #two times the RVE size

        self.x_min = -0.5 * domain_scale_multiplier * RVE_length_x
        self.x_max = 0.5 * domain_scale_multiplier * RVE_length_x
        self.y_min = -0.5 * domain_scale_multiplier * RVE_length_y
        self.y_max = 0.5 * domain_scale_multiplier * RVE_length_y
        self.z_min = -0.5 * domain_scale_multiplier * RVE_length_z
        self.z_max = 0.5 * domain_scale_multiplier * RVE_length_z

        parameters_file = open("ParametersDEMGen.json", 'r')
        self.parameters_all = Parameters(parameters_file.read())
        self.parameters = self.parameters_all["random_particle_generation_parameters"]
        self.initial_target_packing_density = self.parameters["target_packing_density"].GetDouble()
        if try_packing_density != 0.0:
            self.parameters["target_packing_density"].SetDouble(try_packing_density)
        print("try_packing_density = {}".format(try_packing_density))
        print("target_packing_density = {}".format(self.parameters["target_packing_density"].GetDouble()))
        original_psd = self.parameters["random_variable_settings"]["possible_values"].GetVector()
        #scaled_pad = [x * self.parameters["random_variable_settings"]["radius_scale_multiplier"].GetDouble() for x in original_psd]
        radius_scale_multiplier = self.parameters["random_variable_settings"]["radius_scale_multiplier"].GetDouble()
        scaled_psd = []
        for i in range(len(original_psd)):
            scaled_psd.append(original_psd[i] * radius_scale_multiplier)
        self.parameters["random_variable_settings"]["possible_values"].SetVector(scaled_psd)

        self.packing_cnt = packing_cnt
        self.ini_path = ini_path

        print("Before creating folder")
        self.create_new_cases_folder()
        self.copy_seed_files_to_aim_folders()
        print("After creating folder")

    def clear_old_cases_folder(self):

        cases_folder_name = 'generated_cases'
        
        if os.path.exists(cases_folder_name):
            shutil.rmtree(cases_folder_name, ignore_errors=True)
            os.makedirs(cases_folder_name)
        else:
            os.makedirs(cases_folder_name)

    def create_new_cases_folder(self):

        new_folder_name = "case_" + str(self.packing_cnt)
        aim_path = os.path.join(os.getcwd(),'generated_cases', new_folder_name)
        os.makedirs(aim_path)
    
    def copy_seed_files_to_aim_folders(self):
        
        aim_folder_name = "case_" + str(self.packing_cnt)
        aim_path = os.path.join(os.getcwd(), "generated_cases", aim_folder_name)

        seed_file_name_list = ['MaterialsDEM.json', 'ProjectParametersDEM.json']
        for seed_file_name in seed_file_name_list:
            seed_file_path_and_name = os.path.join(os.getcwd(), seed_file_name)
            aim_file_path_and_name = os.path.join(aim_path, seed_file_name)
            shutil.copyfile(seed_file_path_and_name, aim_file_path_and_name)

        if self.parameters_all["generator_name"].GetString() == "isotropic_compression_method":
            seed_file_path_and_name = os.path.join(self.ini_path, 'src', 'utilities', 'isotropic_compression_method_run.py')
            aim_file_path_and_name = os.path.join(aim_path, 'isotropic_compression_method_run.py')
            with open(seed_file_path_and_name, "r") as f_material:
                    with open(aim_file_path_and_name, "w") as f_material_w:
                        for line in f_material.readlines():
                            if "domain_scale_multiplier_input" in line:
                                line = line.replace("1.5", str(self.parameters["domain_scale_multiplier"].GetDouble()))
                            f_material_w.write(line)

            seed_file_name_list = ['inletPGDEM_FEM_boundary.mdpa']
            for seed_file_name in seed_file_name_list:
                seed_file_path_and_name = os.path.join(self.ini_path, 'src', 'utilities','rem_seed_files', seed_file_name)
                aim_file_path_and_name = os.path.join(aim_path, seed_file_name)
                shutil.copyfile(seed_file_path_and_name, aim_file_path_and_name)

        elif self.parameters_all["generator_name"].GetString() == "radius_expansion_method":
            seed_file_path_and_name = os.path.join(self.ini_path, 'src', 'utilities', 'radius_expansion_method_run_v1.4.py')
            aim_file_path_and_name = os.path.join(aim_path, 'radius_expansion_method_run_v1.4.py')
            shutil.copyfile(seed_file_path_and_name, aim_file_path_and_name)

        elif self.parameters_all["generator_name"].GetString() == "radius_expansion_method_with_servo_control":
            seed_file_name_list = ['radius_expansion_method_with_servo_control_run.py', 'radius_expansion_method_with_servo_control_run_final.py', 'plot_stress.py']
            for seed_file_name in seed_file_name_list:
                seed_file_path_and_name = os.path.join(self.ini_path, 'src', 'utilities', seed_file_name)
                aim_file_path_and_name = os.path.join(aim_path, seed_file_name)
                with open(seed_file_path_and_name, "r") as f_material:
                    with open(aim_file_path_and_name, "w") as f_material_w:
                        for line in f_material.readlines():
                            if "self.target_packing_density =" in line:
                                line = line.replace("0.64", str(self.initial_target_packing_density))
                            if "ax2.axhline(y=" in line:
                                line = line.replace("0.635", str(self.initial_target_packing_density))
                            f_material_w.write(line)

        seed_file_path_and_name = os.path.join(self.ini_path, 'src', 'utilities', 'show_packing.py')
        aim_file_path_and_name = os.path.join(aim_path, 'show_packing.py')
        shutil.copyfile(seed_file_path_and_name, aim_file_path_and_name)
    
    def CreateParticles(self, RVE_size):

        is_first_particle = True
        particle_cnt = 1
        particle_volume = 0
        #aim_particle_number = self.parameters["aim_particle_number"].GetInt()
        target_packing_density = self.parameters["target_packing_density"].GetDouble()
        target_packing_density_tolerance = self.parameters["target_packing_density_tolerance"].GetDouble()
        print("target_packing_density = {}".format(target_packing_density))
        radius_scale_multiplier = self.parameters["random_variable_settings"]["radius_scale_multiplier"].GetDouble()
        aim_volume = RVE_size[0] * RVE_size[1] * RVE_size[2] * (target_packing_density + target_packing_density_tolerance) * (radius_scale_multiplier ** 3)

        while particle_volume < aim_volume:

            p_parameters_dict = {
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
 
            seed = self.parameters["SEED"].GetInt()
            creator_destructor = ParticleCreatorDestructor()
            self.Fast_Filling_Creator = Fast_Filling_Creator(self.parameters, seed)
            r = self.Fast_Filling_Creator.GetRandomParticleRadius(creator_destructor)

            if is_first_particle:
                radius_max = self.parameters["MAXIMUM_RADIUS"].GetDouble() * self.parameters["random_variable_settings"]["radius_scale_multiplier"].GetDouble()
                if self.parameters_all["periodic_boundary_option"].GetBool():
                    x = random.uniform(self.x_min , self.x_max)
                    y = random.uniform(self.y_min , self.y_max)
                    z = random.uniform(self.z_min , self.z_max)
                else:
                    x = random.uniform(self.x_min + radius_max, self.x_max - radius_max)
                    y = random.uniform(self.y_min + radius_max, self.y_max - radius_max)
                    z = random.uniform(self.z_min + radius_max, self.z_max - radius_max)
                p_parameters_dict["id"] = particle_cnt
                p_parameters_dict["p_x"] = x
                p_parameters_dict["p_y"] = y
                p_parameters_dict["p_z"] = z
                p_parameters_dict["radius"] = r
                p_parameters_dict["p_ele_id"] = particle_cnt
                self.particle_list.append(p_parameters_dict)
                print("Added particle number = {}".format(particle_cnt))
                particle_cnt += 1
                particle_volume += 4/3 * math.pi * (r**3)
                is_first_particle = False
            else:
                IsOverlaped = True
                loop_cnt = 0
                while IsOverlaped:
                    radius_max = self.parameters["MAXIMUM_RADIUS"].GetDouble() * self.parameters["random_variable_settings"]["radius_scale_multiplier"].GetDouble()
                    if self.parameters_all["periodic_boundary_option"].GetBool():
                        self.x = random.uniform(self.x_min, self.x_max)
                        self.y = random.uniform(self.y_min, self.y_max)
                        self.z = random.uniform(self.z_min, self.z_max)
                        for particle in self.particle_list:
                            IsOverlaped = self.Fast_Filling_Creator.CheckHasIndentationOrNot(self.x, self.y, self.z, r, particle["p_x"], particle["p_y"], particle["p_z"], particle["radius"])
                            if IsOverlaped:
                                break

                        real_RVE_x_length = self.x_max - self.x_min
                        real_RVE_y_length = self.y_max - self.y_min
                        real_RVE_z_length = self.z_max - self.z_min

                        x_plus = self.x + real_RVE_x_length
                        x_minus = self.x - real_RVE_x_length
                        y_plus = self.y + real_RVE_y_length
                        y_minus = self.y - real_RVE_y_length
                        z_plus = self.z + real_RVE_z_length
                        z_minus = self.z - real_RVE_z_length

                        if not IsOverlaped:
                            for particle in self.particle_list_side:
                                p_x, p_y, p_z, p_r = particle["p_x"], particle["p_y"], particle["p_z"], particle["radius"]
                                IsOverlaped = self.Fast_Filling_Creator.CheckHasIndentationOrNot(x_plus, self.y, self.z, r, p_x, p_y, p_z, p_r)
                                if IsOverlaped:
                                    break
                                IsOverlaped = self.Fast_Filling_Creator.CheckHasIndentationOrNot(x_plus, y_plus, self.z, r, p_x, p_y, p_z, p_r)
                                if IsOverlaped:
                                    break
                                IsOverlaped = self.Fast_Filling_Creator.CheckHasIndentationOrNot(x_plus, y_minus, self.z, r, p_x, p_y, p_z, p_r)
                                if IsOverlaped:
                                    break
                                IsOverlaped = self.Fast_Filling_Creator.CheckHasIndentationOrNot(x_plus, self.y, z_plus, r, p_x, p_y, p_z, p_r)
                                if IsOverlaped:
                                    break
                                IsOverlaped = self.Fast_Filling_Creator.CheckHasIndentationOrNot(x_plus, self.y, z_minus, r, p_x, p_y, p_z, p_r)
                                if IsOverlaped:
                                    break
                        if not IsOverlaped:
                            for particle in self.particle_list_side:
                                p_x, p_y, p_z, p_r = particle["p_x"], particle["p_y"], particle["p_z"], particle["radius"]
                                IsOverlaped = self.Fast_Filling_Creator.CheckHasIndentationOrNot(x_minus, self.y, self.z, r, p_x, p_y, p_z, p_r)
                                if IsOverlaped:
                                    break
                                IsOverlaped = self.Fast_Filling_Creator.CheckHasIndentationOrNot(x_minus, y_plus, self.z, r, p_x, p_y, p_z, p_r)
                                if IsOverlaped:
                                    break
                                IsOverlaped = self.Fast_Filling_Creator.CheckHasIndentationOrNot(x_minus, y_minus, self.z, r, p_x, p_y, p_z, p_r)
                                if IsOverlaped:
                                    break
                                IsOverlaped = self.Fast_Filling_Creator.CheckHasIndentationOrNot(x_minus, self.y, z_plus, r, p_x, p_y, p_z, p_r)
                                if IsOverlaped:
                                    break
                                IsOverlaped = self.Fast_Filling_Creator.CheckHasIndentationOrNot(x_minus, self.y, z_minus, r, p_x, p_y, p_z, p_r)
                                if IsOverlaped:
                                    break
                        
                        if not IsOverlaped:
                            for particle in self.particle_list_side:
                                p_x, p_y, p_z, p_r = particle["p_x"], particle["p_y"], particle["p_z"], particle["radius"]
                                IsOverlaped = self.Fast_Filling_Creator.CheckHasIndentationOrNot(self.x, y_minus, self.z, r, p_x, p_y, p_z, p_r)
                                if IsOverlaped:
                                    break
                                IsOverlaped = self.Fast_Filling_Creator.CheckHasIndentationOrNot(x_minus, y_minus, self.z, r, p_x, p_y, p_z, p_r)
                                if IsOverlaped:
                                    break
                                IsOverlaped = self.Fast_Filling_Creator.CheckHasIndentationOrNot(x_plus, y_minus, self.z, r, p_x, p_y, p_z, p_r)
                                if IsOverlaped:
                                    break
                                IsOverlaped = self.Fast_Filling_Creator.CheckHasIndentationOrNot(self.x, y_minus, z_minus, r, p_x, p_y, p_z, p_r)
                                if IsOverlaped:
                                    break
                                IsOverlaped = self.Fast_Filling_Creator.CheckHasIndentationOrNot(self.x, y_minus, z_plus, r, p_x, p_y, p_z, p_r)
                                if IsOverlaped:
                                    break
                        if not IsOverlaped:
                            for particle in self.particle_list_side:
                                p_x, p_y, p_z, p_r = particle["p_x"], particle["p_y"], particle["p_z"], particle["radius"]
                                IsOverlaped = self.Fast_Filling_Creator.CheckHasIndentationOrNot(self.x, y_plus, self.z, r, p_x, p_y, p_z, p_r)
                                if IsOverlaped:
                                    break
                                IsOverlaped = self.Fast_Filling_Creator.CheckHasIndentationOrNot(x_minus, y_plus, self.z, r, p_x, p_y, p_z, p_r)
                                if IsOverlaped:
                                    break
                                IsOverlaped = self.Fast_Filling_Creator.CheckHasIndentationOrNot(x_plus, y_plus, self.z, r, p_x, p_y, p_z, p_r)
                                if IsOverlaped:
                                    break
                                IsOverlaped = self.Fast_Filling_Creator.CheckHasIndentationOrNot(self.x, y_plus, z_minus, r, p_x, p_y, p_z, p_r)
                                if IsOverlaped:
                                    break
                                IsOverlaped = self.Fast_Filling_Creator.CheckHasIndentationOrNot(self.x, y_plus, z_plus, r, p_x, p_y, p_z, p_r)
                                if IsOverlaped:
                                    break

                        if not IsOverlaped:
                            for particle in self.particle_list_side:
                                p_x, p_y, p_z, p_r = particle["p_x"], particle["p_y"], particle["p_z"], particle["radius"]
                                IsOverlaped = self.Fast_Filling_Creator.CheckHasIndentationOrNot(self.x, self.y, z_plus, r, p_x, p_y, p_z, p_r)
                                if IsOverlaped:
                                    break
                                IsOverlaped = self.Fast_Filling_Creator.CheckHasIndentationOrNot(x_minus, self.y, z_plus, r, p_x, p_y, p_z, p_r)
                                if IsOverlaped:
                                    break
                                IsOverlaped = self.Fast_Filling_Creator.CheckHasIndentationOrNot(x_plus, self.y, z_plus, r, p_x, p_y, p_z, p_r)
                                if IsOverlaped:
                                    break
                                IsOverlaped = self.Fast_Filling_Creator.CheckHasIndentationOrNot(self.x, y_plus, z_plus, r, p_x, p_y, p_z, p_r)
                                if IsOverlaped:
                                    break
                                IsOverlaped = self.Fast_Filling_Creator.CheckHasIndentationOrNot(self.x, y_minus, z_plus, r, p_x, p_y, p_z, p_r)
                                if IsOverlaped:
                                    break
                        if not IsOverlaped:
                            for particle in self.particle_list_side:
                                p_x, p_y, p_z, p_r = particle["p_x"], particle["p_y"], particle["p_z"], particle["radius"]
                                IsOverlaped = self.Fast_Filling_Creator.CheckHasIndentationOrNot(self.x, self.y, z_minus, r, p_x, p_y, p_z, p_r)
                                if IsOverlaped:
                                    break
                                IsOverlaped = self.Fast_Filling_Creator.CheckHasIndentationOrNot(x_minus, self.y, z_minus, r, p_x, p_y, p_z, p_r)
                                if IsOverlaped:
                                    break
                                IsOverlaped = self.Fast_Filling_Creator.CheckHasIndentationOrNot(x_plus, self.y, z_minus, r, p_x, p_y, p_z, p_r)
                                if IsOverlaped:
                                    break
                                IsOverlaped = self.Fast_Filling_Creator.CheckHasIndentationOrNot(self.x, y_plus, z_minus, r, p_x, p_y, p_z, p_r)
                                if IsOverlaped:
                                    break
                                IsOverlaped = self.Fast_Filling_Creator.CheckHasIndentationOrNot(self.x, y_minus, z_minus, r, p_x, p_y, p_z, p_r)
                                if IsOverlaped:
                                    break
                    else:
                        self.x = random.uniform(self.x_min + radius_max, self.x_max - radius_max)
                        self.y = random.uniform(self.y_min + radius_max, self.y_max - radius_max)
                        self.z = random.uniform(self.z_min + radius_max, self.z_max - radius_max)
                        for particle in self.particle_list:
                            IsOverlaped = self.Fast_Filling_Creator.CheckHasIndentationOrNot(self.x, self.y, self.z, r, particle["p_x"], particle["p_y"], particle["p_z"], particle["radius"])
                            if IsOverlaped:
                                break
                    loop_cnt += 1
                    if loop_cnt > 10000:
                        print("Too much loop for one particle!")
                        exit(0)
                    
                p_parameters_dict["id"] = particle_cnt
                p_parameters_dict["p_x"] = self.x
                p_parameters_dict["p_y"] = self.y
                p_parameters_dict["p_z"] = self.z
                p_parameters_dict["radius"] = r
                p_parameters_dict["p_ele_id"] = particle_cnt
                self.particle_list.append(p_parameters_dict)
                if self.parameters_all["periodic_boundary_option"].GetBool():
                    if self.x <= self.x_min + radius_max * 2:
                        self.particle_list_side.append(p_parameters_dict)
                    elif self.x >= self.x_max - radius_max * 2:
                        self.particle_list_side.append(p_parameters_dict)
                    elif self.y <= self.y_min + radius_max * 2:
                        self.particle_list_side.append(p_parameters_dict)
                    elif self.y >= self.y_max - radius_max * 2:
                        self.particle_list_side.append(p_parameters_dict)
                    elif self.z <= self.z_min + radius_max * 2:
                        self.particle_list_side.append(p_parameters_dict)
                    elif self.z >= self.z_max - radius_max * 2:
                        self.particle_list_side.append(p_parameters_dict)
                print("Added particle number = {}".format(particle_cnt))
                particle_cnt += 1
                particle_volume += 4/3 * math.pi * (r**3)
        
    def WriteOutGIDData(self, aim_folder_name, aim_file_name):

        aim_path_and_name = os.path.join(os.getcwd(), "generated_cases", aim_folder_name, aim_file_name)

        # clean the exsisted file first
        if os.path.isfile(aim_path_and_name):
            os.remove(aim_path_and_name)
        
        with open(aim_path_and_name,'a') as f:
            # write the particle information
            f.write("Begin ModelPartData \n //  VARIABLE_NAME value \n End ModelPartData \n \n Begin Properties 0 \n End Properties \n \n")
            f.write("Begin Nodes\n")
            for p_pram_dict in self.particle_list:
                f.write(str(p_pram_dict["id"]) + ' ' + str(p_pram_dict["p_x"]) + ' ' + str(p_pram_dict["p_y"]) + ' ' + str(p_pram_dict["p_z"]) + '\n')
            f.write("End Nodes \n \n")

            f.write("Begin Elements SphericParticle3D// GUI group identifier: Body \n")
            for p_pram_dict in self.particle_list:
                f.write(str(p_pram_dict["p_ele_id"]) + ' ' + ' 0 ' + str(p_pram_dict["id"]) + '\n')
            f.write("End Elements \n \n")

            f.write("Begin NodalData RADIUS // GUI group identifier: Body \n")
            for p_pram_dict in self.particle_list:
                f.write(str(p_pram_dict["id"]) + ' ' + ' 0 ' + str(p_pram_dict["radius"]) + '\n')
            f.write("End NodalData \n \n")

            ''' only works for continuum DEM calculation
            f.write("Begin NodalData COHESIVE_GROUP // GUI group identifier: Body \n")
            for p_pram_dict in self.p_pram_list:
                f.write(str(p_pram_dict["id"]) + ' ' + ' 0 ' + " 1 " + '\n')
            f.write("End NodalData \n \n")

            f.write("Begin NodalData SKIN_SPHERE \n End NodalData \n \n")
            '''

            f.write("Begin SubModelPart DEMParts_Body // Group Body // Subtree DEMParts \n Begin SubModelPartNodes \n")
            for p_pram_dict in self.particle_list:
                if p_pram_dict["p_group_id"] == 0:
                    f.write(str(p_pram_dict["id"]) + '\n')
            f.write("End SubModelPartNodes \n Begin SubModelPartElements \n ")
            for p_pram_dict in self.particle_list:
                if p_pram_dict["p_group_id"] == 0:
                    f.write(str(p_pram_dict["p_ele_id"]) + '\n')
            f.write("End SubModelPartElements \n")
            f.write("Begin SubModelPartConditions \n End SubModelPartConditions \n End SubModelPart \n \n")

            #write out joint group
            joint_exist = False
            for p_pram_dict in self.particle_list:
                if p_pram_dict["p_group_id"] == 1:
                    joint_exist = True

            if joint_exist:
                f.write("Begin SubModelPart DEMParts_Joint // Group Joint // Subtree DEMParts \n Begin SubModelPartNodes \n")
                for p_pram_dict in self.particle_list:
                    if p_pram_dict["p_group_id"] == 1:
                        f.write(str(p_pram_dict["id"]) + '\n')
                f.write("End SubModelPartNodes \n Begin SubModelPartElements \n ")
                for p_pram_dict in self.particle_list:
                    if p_pram_dict["p_group_id"] == 1:
                        f.write(str(p_pram_dict["p_ele_id"]) + '\n')
                f.write("End SubModelPartElements \n")
                f.write("Begin SubModelPartConditions \n End SubModelPartConditions \n End SubModelPart \n")

            f.close()

        print("Successfully write out file {}-{}!".format(aim_folder_name, aim_file_name))