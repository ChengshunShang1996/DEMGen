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

import time
import sys
import shutil

import KratosMultiphysics
from KratosMultiphysics import *
from KratosMultiphysics.DEMApplication.DEM_analysis_stage import DEMAnalysisStage
from KratosMultiphysics import Logger

if os.path.exists("normalized_kinematic_energy.txt"):
    os.remove("normalized_kinematic_energy.txt")
if os.path.exists("stress_tensor_averaged.txt"):
    os.remove("stress_tensor_averaged.txt")
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
        self.check_status = False
        self.second_stage_flag = False

    def Initialize(self):
        super().Initialize()
        self.dt = self.spheres_model_part.ProcessInfo[DELTA_TIME]
        self.final_check_frequency  = int(self.parameters["GraphExportFreq"].GetDouble()/self.parameters["MaxTimeStep"].GetDouble())
        self.final_check_counter = 0
        self.final_check_counter_2 = 0
        self.final_check_counter_reset = 0
    
    def SetResetStart(self):

        self.start_reset_velocity = True

    def SetAllParticleVelocityToZero(self):
        for node in self.spheres_model_part.Nodes:
            node.SetSolutionStepValue(VELOCITY_X, 0.0)
            node.SetSolutionStepValue(VELOCITY_Y, 0.0)
            node.SetSolutionStepValue(VELOCITY_Z, 0.0)
    
    def OutputSolutionStep(self):
        
        if not self.start_reset_velocity:
            super().OutputSolutionStep()
        else:
            self.post_utils.ComputeMeanVelocitiesInTrap("Average_Velocity.txt", self.time, self.graphs_path)
            self.DEMFEMProcedures.PrintGraph(self.time)
            self.DEMFEMProcedures.PrintBallsGraph(self.time)
            self.DEMFEMProcedures.PrintAdditionalGraphs(self.time, self._GetSolver())
            self.DEMEnergyCalculator.CalculateEnergyAndPlot(self.time)

            self._GetSolver().PrepareElementsForPrinting()
            if self.DEM_parameters["ContactMeshOption"].GetBool():
                self._GetSolver().PrepareContactElementsForPrinting()

        if self.start_reset_velocity and (self.final_check_counter_reset == 50) and (not self.check_status):
            self.final_check_counter_reset = 0
            self.SetAllParticleVelocityToZero()

        if self.final_check_counter == self.final_check_frequency:

            self.final_check_counter = 0

            self.check_status = True
            
            self.normalized_kinematic_energy = self.DEMEnergyCalculator.CalculateNormalizedKinematicEnergy()
            with open("normalized_kinematic_energy.txt", 'a') as file:
                file.write(str(self.time) + ' ' + str(self.normalized_kinematic_energy) + '\n')

            side_length = 0.0025
            center_x = 0.0
            center_y = 0.0
            center_z = 0.0
            stress_tensor = self.MeasureSphereForGettingPackingProperties((side_length/2), center_x, center_y, center_z, "stress_tensor")
            with open("stress_tensor_averaged.txt", 'a') as file:
                file.write(str(self.time) + ' ' + str((stress_tensor[0][0] + stress_tensor[1][1] + stress_tensor[2][2])/3) + '\n')

            # n = 5e6;   Rate 100 = 1 / (Delta t * n); t = Delta t * n

            if self.start_reset_velocity and (self.final_check_counter_2 == self.final_check_frequency * 2):
                
                self.final_check_counter_2 = 0
                self.check_status = False
                print(' ')
                print("----------------------------Second loops {} finished!".format(self.time))
                print(' ')
                
                self.PrintResultsForGid(self.time)

                if self.normalized_kinematic_energy < 1e-8:
                    self.WriteOutMdpaFileOfParticles("inletPGDEM.mdpa")
                    self.PrintResultsForGid(self.time)
                    self.copy_files_and_run_show_results()
                    exit(0)
                else:
                    self.SetAllParticleVelocityToZero()

            
            if self.time > 0.05:
                self.DEM_parameters["MaxTimeStep"].SetDouble(1e-5)
                self._GetSolver().dt = self.DEM_parameters["MaxTimeStep"].GetDouble()
                self.spheres_model_part.ProcessInfo[DELTA_TIME] = self.parameters["MaxTimeStep"].GetDouble()
                self.dt = self.spheres_model_part.ProcessInfo[DELTA_TIME]
        
        if self.start_reset_velocity:
            self.final_check_counter_2 += 1
            if not self.check_status:
                self.final_check_counter_reset += 1

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

    def WriteOutMdpaFileOfParticles(self, output_file_name):

        if self.second_stage_flag:
            print("I am here")
            self.clear_old_and_create_new_show_packing_case_folder()
            print("I am here 2")
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
    MyDemCase.SetSecondStageFlag()
    MyDemCase.RunSolutionLoop()
    #NormalizedKineticEnergy = MyDemCase.PassNormalizedKineticEnergy()
    MyDemCase.Finalize()

    