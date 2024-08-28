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

import KratosMultiphysics
from KratosMultiphysics import *
from KratosMultiphysics.DEMApplication.DEM_analysis_stage import DEMAnalysisStage
from KratosMultiphysics import Logger

class DEMAnalysisStageWithFlush(DEMAnalysisStage):

    def __init__(self, model, project_parameters, radius_multiplier, old_radius_multiplier, flush_frequency=10.0):
        super().__init__(model, project_parameters)
        self.flush_frequency = flush_frequency
        self.last_flush = time.time()
        self.radius_multiplier = radius_multiplier
        self.old_radius_multiplier = old_radius_multiplier

    def FinalizeSolutionStep(self):
        super().FinalizeSolutionStep()

        if self.parallel_type == "OpenMP":
            now = time.time()
            if now - self.last_flush > self.flush_frequency:
                sys.stdout.flush()
                self.last_flush = now

    def Finalize(self):
        self.WriteOutMdpaFileOfParticles("inletPGDEM" + str(self.radius_multiplier) + ".mdpa")
        self.WriteOutMdpaFileOfParticles("inletPGDEM.mdpa")
        self.PrintResultsForGid(self.time)
        super().Finalize()
    
    '''
    def UpdateYoungsModulus(self):
        
        old_E = self.spheres_model_part.GetProperties()[1][YOUNG_MODULUS]
        update_E = 2.0 * old_E
        
        with open('MaterialsDEM.json', 'r') as file:
            file_content = file.read()

        basic_string = '"YOUNG_MODULUS"       : '
        search_string =  basic_string + str(old_E)

        new_content = file_content.replace(search_string, basic_string + str(update_E))

        with open('MaterialsDEM.json', 'w') as file:
            file.write(new_content)

        self.WriteOutMdpaFileOfParticles("inletPGDEM.mdpa")

        print("--------------------Current E = {} ---------------------------".format(update_E))
    '''

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
                f.write(str(node.Id) + ' ' + ' 0 ' + str(node.GetSolutionStepValue(RADIUS) / self.old_radius_multiplier * self.radius_multiplier) + '\n')
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
    radius_multiplier = 1
    old_radius_multiplier = 1
    while radius_multiplier < 2.1:
        with open("ProjectParametersDEM.json", 'r') as parameter_file:
            parameters = KratosMultiphysics.Parameters(parameter_file.read())

        if radius_multiplier >= 2.0:
            parameters["FinalTime"].SetDouble(10)
        global_model = KratosMultiphysics.Model()
        MyDemCase = DEMAnalysisStageWithFlush(global_model, parameters, radius_multiplier, old_radius_multiplier)
        MyDemCase.Run()
        os.rename("inletPG_Post_Files", "inletPG_Post_Files_" + str(radius_multiplier))
        print("----------------------------Loop {} finished!".format(radius_multiplier))
        old_radius_multiplier = radius_multiplier
        radius_multiplier += 0.1