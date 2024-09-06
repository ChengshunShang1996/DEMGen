#/////////////////////////////////////////////////
#// Main author: Chengshun Shang (CIMNE)
#// Email: chengshun.shang1996@gmail.com
#// Date: August 2023
#/////////////////////////////////////////////////

import os
import random
import math
from KratosMultiphysics import *
from KratosMultiphysics.DEMApplication import *

class CreatParticlesInsideOfADomain():

    def __init__(self) -> None:  

        pass

    def initialize(self, RVE_size, domain_scale_multiplier):

        self.particle_list = []
        '''
        self.particle_list_left = []
        self.particle_list_right = []
        self.particle_list_top = []
        self.particle_list_bottom = []
        self.particle_list_front = []
        self.particle_list_behind = []'''
        self.particle_list_side = []

        RVE_length_x = RVE_size[0]
        RVE_length_y = RVE_size[1]
        RVE_length_z = RVE_size[2]

        #two times of the RVE size

        self.x_min = -0.5 * domain_scale_multiplier * RVE_length_x
        self.x_max = 0.5 * domain_scale_multiplier * RVE_length_x
        self.y_min = -0.5 * domain_scale_multiplier * RVE_length_y
        self.y_max = 0.5 * domain_scale_multiplier * RVE_length_y
        self.z_min = -0.5 * domain_scale_multiplier * RVE_length_z
        self.z_max = 0.5 * domain_scale_multiplier * RVE_length_z

        parameters_file = open("creat_particles_input_parameters.json", 'r')
        self.parameters = Parameters(parameters_file.read())
        original_psd = self.parameters["random_variable_settings"]["possible_values"].GetVector()
        scaled_pad = [x * self.parameters["random_variable_settings"]["radius_scale_multiplier"].GetDouble() for x in original_psd]
        self.parameters["random_variable_settings"]["possible_values"].SetVector(scaled_pad)

    def CreateParticles(self, RVE_size):

        is_first_particle = True
        particle_cnt = 1
        particle_volume = 0
        #aim_particle_number = self.parameters["aim_particle_number"].GetInt()
        aim_porosity = self.parameters["aim_porosity"].GetDouble()
        aim_porosity_tolerance = self.parameters["aim_porosity_tolerance"].GetDouble()
        radius_scale_multiplier = self.parameters["random_variable_settings"]["radius_scale_multiplier"].GetDouble()
        aim_volume = RVE_size[0] * RVE_size[1] * RVE_size[2] * (1 - aim_porosity - aim_porosity_tolerance) * (radius_scale_multiplier ** 3)
        
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
                if self.parameters["UsingPeriodicBoundary"].GetBool():
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
                #print("Added particle number = {}".format(particle_cnt))
                particle_cnt += 1
                particle_volume += 4/3 * math.pi * (r**3)
                is_first_particle = False
            else:
                IsOverlaped = True
                loop_cnt = 0
                radius_max = self.parameters["MAXIMUM_RADIUS"].GetDouble() * self.parameters["random_variable_settings"]["radius_scale_multiplier"].GetDouble()
                while IsOverlaped:
                    if self.parameters["UsingPeriodicBoundary"].GetBool():
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
                if self.parameters["UsingPeriodicBoundary"].GetBool():
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
        
    def WriteOutGIDData(self, outName = 'inletPGDEM_ini.mdpa'):

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

    TestDEM = CreatParticlesInsideOfADomain()
    RVE_length_x = 0.005
    RVE_length_y = 0.005
    RVE_length_z = 0.005
    RVE_size = [RVE_length_x, RVE_length_y, RVE_length_z]
    domain_scale_multiplier = 1.0
    TestDEM.initialize(RVE_size, domain_scale_multiplier)
    TestDEM.CreateParticles(RVE_size)
    TestDEM.WriteOutGIDData()

