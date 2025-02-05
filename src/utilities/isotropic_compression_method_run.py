#/////////////////////////////////////////////////
__author__      = "Chengshun Shang (CIMNE)"
__copyright__   = "Copyright (C) 2023-present by Chengshun Shang"
__version__     = "0.0.1"
__maintainer__  = "Chengshun Shang"
__email__       = "cshang@cimne.upc.edu"
__status__      = "development"
__date__        = "June 26, 2024"
__license__     = "BSD 2-Clause License"
#/////////////////////////////////////////////////

import KratosMultiphysics
from KratosMultiphysics import *
from KratosMultiphysics.DEMApplication import *
from KratosMultiphysics.DEMApplication.DEM_analysis_stage import DEMAnalysisStage
from KratosMultiphysics.DEMApplication import DEM_procedures as DEM_procedures
import math
from sys import exit
import random
import shutil

class IsotropicCompressionTestRun(DEMAnalysisStage):

    def __init__(self, model, parameters):
        super().__init__(model, parameters)
        self.parameters = parameters

    def Initialize(self):
        super().Initialize()
        self.InitializePackingGenerator() 

    def InitializePackingGenerator(self):

        self.periodic_boundary_move_inwards_velocity = self.parameters["BoundingBoxMoveVelocity"].GetDouble()
        #Note: In Kratos DEM, the BoundingBox move every [NStepSearch] steps, which can help us get a stable results
        self.NStepSearch = self.parameters["NeighbourSearchFrequency"].GetDouble()
        self.update_bounding_box_freq = self.parameters["MaxTimeStep"].GetDouble() / self.NStepSearch
        self.final_check_counter = 0
        self.need_apply_forces = True
        self.end_cnt = 0

        self.dt = self.spheres_model_part.ProcessInfo[DELTA_TIME]
        self.graph_export_freq = self.parameters["GraphExportFreq"].GetDouble()
        self.final_check_frequency  = int(self.graph_export_freq / self.parameters["MaxTimeStep"].GetDouble())
        self.final_packing_lenth_ini  = self.parameters["BoundingBoxMaxX"].GetDouble() - self.parameters["BoundingBoxMinX"].GetDouble()
        self.domain_scale_multiplier_input = 1.5
        self.domain_scale_multiplier = self.domain_scale_multiplier_input
        self.total_compression_distance = self.final_packing_lenth_ini / (self.domain_scale_multiplier * 2.0) 
        self.final_packing_lenth = (self.parameters["BoundingBoxMaxX"].GetDouble() - self.parameters["BoundingBoxMinX"].GetDouble()) / self.domain_scale_multiplier

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

        if self.final_check_counter == self.final_check_frequency:

            self.final_check_counter = 0

            if self.parameters["BoundingBoxMoveOption"].GetBool():
                self.final_packing_lenth_ini -= 2 * self.periodic_boundary_move_inwards_velocity * self.update_bounding_box_freq * self.final_check_frequency
            
            if self.need_apply_forces:
                self.ApplyRandomForcesToParticles()
            else:
                self.EraseAppliedForces()
            #if self.final_packing_porosity > (1 - self.max_porosity_tolerance) * self.aim_final_packing_porosity and self.final_packing_porosity < (1 + self.max_porosity_tolerance) * self.aim_final_packing_porosity:
            if self.final_packing_lenth_ini <= self.final_packing_lenth:
                self.parameters["BoundingBoxMoveOption"].SetBool(False)
                self.need_apply_forces = False
                self.normalized_kinematic_energy = self.DEMEnergyCalculator.CalculateNormalizedKinematicEnergy()
                #print(self.normalized_kinematic_energy)
                with open("normalized_kinematic_energy.txt", 'a') as file:
                    file.write(str(self.time) + ' ' + str(self.normalized_kinematic_energy) + '\n')

                # n = 5e6;   Rate 100 = 1 / (Delta t * n); t = Delta t * n
                expansion_stop_time = self.total_compression_distance / (2 * self.parameters["BoundingBoxMoveVelocity"].GetDouble() / self.NStepSearch)
                if self.time > expansion_stop_time and self.normalized_kinematic_energy < 1e-8:
                    self.PrintResultsForGid(self.time)
                    self.WriteOutMdpaFileOfParticles('inletPGDEM.mdpa')
                    self.copy_files_and_run_show_results()
                    exit(0)
            #elif self.final_packing_lenth_ini <= 0.0051:
            #    self.parameters["BoundingBoxMoveVelocity"].SetDouble(0.005)
            #elif self.final_packing_lenth_ini <= 0.0055:
            #    self.parameters["BoundingBoxMoveVelocity"].SetDouble(0.01)

        self.final_check_counter += 1

    def ApplyRandomForcesToParticles(self):
        
        for node in self.spheres_model_part.Nodes:

            x = random.uniform(-1, 1)
            y = random.uniform(-1, 1)
            z = random.uniform(-1, 1)
            r = node.GetSolutionStepValue(RADIUS)

            values = Array3()
            vect = Array3()

            # normal vector to the center:
            vect_moduli = math.sqrt(x * x + y * y + z * z)

            vect[0] = x / vect_moduli
            vect[1] = y / vect_moduli
            vect[2] = z / vect_moduli

            applied_force = random.uniform(0.99e3, 1.01e3) * (r ** 3)
            values[0] = applied_force * vect[0]
            values[1] = applied_force * vect[1]
            values[2] = applied_force * vect[2]

            node.SetSolutionStepValue(EXTERNAL_APPLIED_FORCE, values)

    def EraseAppliedForces(self):

        for node in self.spheres_model_part.Nodes:
            
            values = Array3()
            values[0] = 0.0
            values[1] = 0.0
            values[2] = 0.0
            node.SetSolutionStepValue(EXTERNAL_APPLIED_FORCE, values)

    def WriteOutMdpaFileOfParticles(self, output_file_name):

        self.clear_old_and_creat_new_show_packing_case_folder()
        aim_path_and_name = os.path.join(os.getcwd(), 'show_packing', output_file_name)

        # clean the exsisted file first
        if os.path.isfile(aim_path_and_name):
            os.remove(aim_path_and_name)
        
        with open(aim_path_and_name,'a') as f:
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

            #uncomment this if it is for continuum simulation
            '''
            f.write("Begin NodalData COHESIVE_GROUP // GUI group identifier: Body \n")
            for node in self.spheres_model_part.Nodes:
                f.write(str(node.Id) + ' ' + ' 0 ' + " 1 " + '\n')
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

    def copy_files_and_run_show_results(self):

        self.copy_seed_files_to_aim_folders()

        aim_path = os.path.join(os.getcwd(),'show_packing')
        os.chdir(aim_path)
        if os.name == 'nt': # for windows
            os.system("python show_packing.py")
        else: # for linux
            os.system("python3 show_packing.py")

    def clear_old_and_creat_new_show_packing_case_folder(self):

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
                            if "dem_inlet_option" in line:
                                line = line.replace("true", 'false')
                            elif "FinalTime" in line:
                                line = "    \"FinalTime\"                      : " + str(self.dt * 2) + ', \n'
                            elif "\"GraphExportFreq\"" in line:
                                line = "    \"GraphExportFreq\"                : " + str(self.dt) + ', \n'
                            elif "VelTrapGraphExportFreq" in line:
                                line = "    \"VelTrapGraphExportFreq\"         : " + str(self.dt) + ', \n'
                            elif "OutputTimeStep" in line:
                                line = "    \"OutputTimeStep\"                 : " + str(self.dt) + ', \n'
                            f_material_w.write(line)
            else:
                shutil.copyfile(seed_file_path_and_name, aim_file_path_and_name)

if __name__ == "__main__":

    with open("ProjectParametersDEM.json", 'r') as parameter_file:
        parameters = KratosMultiphysics.Parameters(parameter_file.read())

        model = KratosMultiphysics.Model()
        run_dem = IsotropicCompressionTestRun(model, parameters)
        run_dem.Run()