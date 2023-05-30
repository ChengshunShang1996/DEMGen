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
from sys import exit

class ParticlePackingGenerator(DEMAnalysisStage):

    def __init__(self, model, parameters):
        super().__init__(model, parameters)
        self.parameters = parameters

    def Initialize(self):
        super().Initialize()
        self.InitializePackingGenerator() 

    def InitializePackingGenerator(self):

        #define the aim porosity
        self.aim_final_packing_porosity = 0.5
        self.max_porosity_tolerance = 0.03
        self.periodic_boundary_move_inwards_velocity = 0.05
        
        self.container_filling_ratio = 0.0
        self.initial_sphere_volume = 0.0
        self.final_packing_porosity = 0.0
        self.final_check_counter = 0

        self.dt = self.spheres_model_part.ProcessInfo[DELTA_TIME]
        self.final_check_frequency  = int(self.parameters["GraphExportFreq"].GetDouble()/self.parameters["MaxTimeStep"].GetDouble())

        self.final_packing_shape = "box"  #input: "cylinder" or "box" 

        if self.final_packing_shape == "box":
            self.final_packing_lenth  = 0.003   #modify according to your case
            self.final_packing_width  = 0.003   #modify according to your case
            self.final_packing_height = 0.003   #modify according to your case
            self.final_packing_volume = self.final_packing_lenth * self.final_packing_width * self.final_packing_height
            self.final_packing_direction = KratosMultiphysics.Array3()
            self.final_packing_direction[0] = 0.0
            self.final_packing_direction[1] = 1.0
            self.final_packing_direction[2] = 0.0

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

            self.MeasureTotalPorosityOfFinalPacking()
            if self.final_packing_porosity > (1 - self.max_porosity_tolerance) * self.aim_final_packing_porosity and self.final_packing_porosity < (1 + self.max_porosity_tolerance) * self.aim_final_packing_porosity:
                self.WriteOutMdpaFileOfParticles('G-TriaxialDEM_after_compressing.mdpa')
                self.PrintResultsForGid(self.time)
                exit(0)

        self.final_check_counter += 1

        self.UpdatePeriodicBoundaryPositionAndFinalPackingVolume()

    def MeasureTotalPorosityOfFinalPacking(self):
        
        selected_element_volume = 0.0
        for node in self.spheres_model_part.Nodes:
            r = node.GetSolutionStepValue(RADIUS)
            element_volume = 4/3 * math.pi * r * r * r
            selected_element_volume += element_volume

        self.final_packing_porosity = 1 - (selected_element_volume / self.final_packing_volume)

        print("Aim porosity is {} and currently porosity is {}".format(self.aim_final_packing_porosity, self.final_packing_porosity))

        return self.final_packing_porosity


    def UpdatePeriodicBoundaryPositionAndFinalPackingVolume(self):

        BoundingBoxMinX_updated = self.parameters["BoundingBoxMinX"].GetDouble() + self.periodic_boundary_move_inwards_velocity * self.time
        BoundingBoxMinY_updated = self.parameters["BoundingBoxMinY"].GetDouble() + self.periodic_boundary_move_inwards_velocity * self.time
        BoundingBoxMinZ_updated = self.parameters["BoundingBoxMinZ"].GetDouble() + self.periodic_boundary_move_inwards_velocity * self.time
        BoundingBoxMaxX_updated = self.parameters["BoundingBoxMaxX"].GetDouble() - self.periodic_boundary_move_inwards_velocity * self.time
        BoundingBoxMaxY_updated = self.parameters["BoundingBoxMaxY"].GetDouble() - self.periodic_boundary_move_inwards_velocity * self.time
        BoundingBoxMaxZ_updated = self.parameters["BoundingBoxMaxZ"].GetDouble() - self.periodic_boundary_move_inwards_velocity * self.time

        if "PeriodicDomainOption" in self.parameters.keys():
            if self.parameters["PeriodicDomainOption"].GetBool():
                self.search_strategy = OMP_DEMSearch(BoundingBoxMinX_updated,
                                                     BoundingBoxMinY_updated,
                                                     BoundingBoxMinZ_updated,
                                                     BoundingBoxMaxX_updated,
                                                     BoundingBoxMaxY_updated,
                                                     BoundingBoxMaxZ_updated)
                
        self.final_packing_lenth  -= 2 * self.periodic_boundary_move_inwards_velocity * self.time
        self.final_packing_width  -= 2 * self.periodic_boundary_move_inwards_velocity * self.time
        self.final_packing_height -= 2 * self.periodic_boundary_move_inwards_velocity * self.time
        self.final_packing_volume = self.final_packing_lenth * self.final_packing_width * self.final_packing_height

    def WriteOutMdpaFileOfParticles(self, output_file_name):

        aim_path_and_name = os.path.join(os.getcwd(), output_file_name)

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

            f.write("Begin Elements SphericContinuumParticle3D// GUI group identifier: Body \n")
            for element in self.spheres_model_part.Elements:
                f.write(str(element.Id) + ' ' + ' 0 ' + str(element.GetNode(0).Id) + '\n')
            f.write("End Elements \n \n")

            f.write("Begin NodalData RADIUS // GUI group identifier: Body \n")
            for node in self.spheres_model_part.Nodes:
                f.write(str(node.Id) + ' ' + ' 0 ' + str(node.GetSolutionStepValue(RADIUS)) + '\n')
            f.write("End NodalData \n \n")

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

if __name__ == "__main__":

    with open("ProjectParametersDEM.json", 'r') as parameter_file:
        parameters = KratosMultiphysics.Parameters(parameter_file.read())

    model = KratosMultiphysics.Model()
    ParticlePackingGenerator(model, parameters).Run()
