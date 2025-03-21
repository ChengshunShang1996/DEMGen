#/////////////////////////////////////////////////
#// Main author: Chengshun Shang (CIMNE)
#// Email: chengshun.shang1996@gmail.com
#// Date: August 2023
#/////////////////////////////////////////////////

import os
import shutil
import random
from KratosMultiphysics import *
from KratosMultiphysics.DEMApplication import *

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

class CreateParticlesInsideOfADomain():

    def __init__(self) -> None:  
        
        self.particle_list = []

    def initialize(self, RVE_size, domain_scale_multiplier):

        RVE_length_x = RVE_size[0]
        RVE_length_y = RVE_size[1]
        RVE_length_z = RVE_size[2]

        #two times of the RVE size

        self.x_min = -0.5 * domain_scale_multiplier * RVE_length_x
        self.x_max = 0.5 * domain_scale_multiplier * RVE_length_x
        self.y_min = 0.0
        self.y_max = RVE_length_y
        self.z_min = -0.5 * domain_scale_multiplier * RVE_length_z
        self.z_max = 0.5 * domain_scale_multiplier * RVE_length_z

        parameters_file = open("create_particles_input_parameters.json", 'r')
        self.parameters = Parameters(parameters_file.read())
        original_psd = self.parameters["random_variable_settings"]["possible_values"].GetVector()
        scaled_pad = [x * self.parameters["random_variable_settings"]["radius_scale_multiplier"].GetDouble() for x in original_psd]
        self.parameters["random_variable_settings"]["possible_values"].SetVector(scaled_pad)

    def CreateParticles(self):

        is_first_particle = True
        particle_cnt = 1
        aim_particle_number = self.parameters["aim_particle_number"].GetInt()
        while particle_cnt <= aim_particle_number:

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
                radius_max = self.parameters["MAXIMUM_RADIUS"].GetDouble()
                x = random.uniform(self.x_min + radius_max, self.x_max - radius_max)
                y = random.uniform(self.y_min + radius_max, self.y_max - radius_max)
                z = random.uniform(self.z_min + radius_max, self.z_max - radius_max)
                if (x**2 + z **2) <= (0.025 - radius_max)**2:
                    p_parameters_dict["id"] = particle_cnt
                    p_parameters_dict["p_x"] = x
                    p_parameters_dict["p_y"] = y
                    p_parameters_dict["p_z"] = z
                    p_parameters_dict["radius"] = r
                    p_parameters_dict["p_ele_id"] = particle_cnt
                    self.particle_list.append(p_parameters_dict)
                    print("Added particle number = {}".format(particle_cnt))
                    particle_cnt += 1
                    is_first_particle = False
            else:
                IsOverlaped = True
                loop_cnt = 0
                while IsOverlaped:
                    radius_max = self.parameters["MAXIMUM_RADIUS"].GetDouble()
                    self.x = random.uniform(self.x_min + radius_max, self.x_max - radius_max)
                    self.y = random.uniform(self.y_min + radius_max, self.y_max - radius_max)
                    self.z = random.uniform(self.z_min + radius_max, self.z_max - radius_max)
                    if (self.x**2 + self.z **2) <= (0.025 - radius_max)**2:
                        for particle in self.particle_list:
                            IsOverlaped = self.Fast_Filling_Creator.CheckHasIndentationOrNot(self.x, self.y, self.z, r, particle["p_x"], particle["p_y"], particle["p_z"], particle["radius"])
                            if IsOverlaped:
                                break
                    loop_cnt += 1
                    if loop_cnt > 1000:
                        print("Too much loop for one particle!")
                        exit(0)
                    
                p_parameters_dict["id"] = particle_cnt
                p_parameters_dict["p_x"] = self.x
                p_parameters_dict["p_y"] = self.y
                p_parameters_dict["p_z"] = self.z
                p_parameters_dict["radius"] = r
                p_parameters_dict["p_ele_id"] = particle_cnt
                self.particle_list.append(p_parameters_dict)
                print("Added particle number = {}".format(particle_cnt))
                particle_cnt += 1
        
    def WriteOutGIDData(self):
    
        outName = 'inletPG3DEM.mdpa'

        # clean the exsisted file first
        if os.path.isfile(outName):
            os.remove(outName)
        
        with open(outName,'a') as f:
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

        print("Successfully write out GID DEM.mdpa file!")



if __name__ == "__main__":

    TestDEM = CreateParticlesInsideOfADomain()
    RVE_length_x = 0.05
    RVE_length_y = 0.1
    RVE_length_z = 0.05
    RVE_size = [RVE_length_x, RVE_length_y, RVE_length_z]
    domain_scale_multiplier = 1
    TestDEM.initialize(RVE_size, domain_scale_multiplier)
    TestDEM.CreateParticles()
    TestDEM.WriteOutGIDData()

