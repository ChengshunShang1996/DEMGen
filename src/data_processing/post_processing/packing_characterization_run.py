#/////////////////////////////////////////////////
__author__      = "Chengshun Shang (CIMNE)"
__copyright__   = "Copyright (C) 2023-present by Chengshun Shang"
__version__     = "0.0.1"
__maintainer__  = "Chengshun Shang"
__email__       = "cshang@cimne.upc.edu"
__status__      = "development"
__date__        = "June 21, 2024"
__license__     = "BSD 2-Clause License"
#/////////////////////////////////////////////////

import KratosMultiphysics
from KratosMultiphysics import *
from KratosMultiphysics.DEMApplication import *
from KratosMultiphysics.DEMApplication.DEM_analysis_stage import DEMAnalysisStage
from KratosMultiphysics.DEMApplication import DEM_procedures as DEM_procedures
import matplotlib.pyplot as plt

class ParticlePackingGenerator(DEMAnalysisStage):

    def __init__(self, model, parameters):
        super().__init__(model, parameters)
        self.parameters = parameters

    def Initialize(self):
        super().Initialize()
        self.InitializePackingGenerator() 
        #self.GetInitialDemSphereVolume()

    def InitializePackingGenerator(self):

        self.max_particle_velocity_in_phase_1_2 = 0.1
        self.final_check_counter = 0

        self.dt = self.spheres_model_part.ProcessInfo[DELTA_TIME]
        self.final_check_frequency  = int(self.parameters["GraphExportFreq"].GetDouble()/self.parameters["MaxTimeStep"].GetDouble())

        self.domain_x_min = self.parameters["BoundingBoxMinX"].GetDouble()
        self.domain_x_max = self.parameters["BoundingBoxMaxX"].GetDouble()
        self.domain_y_min = self.parameters["BoundingBoxMinY"].GetDouble()
        self.domain_y_max = self.parameters["BoundingBoxMaxY"].GetDouble()
        self.domain_z_min = self.parameters["BoundingBoxMinZ"].GetDouble()
        self.domain_z_max = self.parameters["BoundingBoxMaxZ"].GetDouble()

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
        #self.MeasureLocalPorosityOfFinalPacking()
        #self.MeasureLocalPorosityWithDifferentRadius()
        self.MeasureLocalPorosityWithDifferentSideLength()
        exit(0)

    def MeasureLocalPorosityWithDifferentSideLength(self):
        
        print("start measurement")
        max_diameter = 0.0002
        RVE_lambda = 4
        side_length = max_diameter * RVE_lambda
        side_length_max = self.domain_x_max - self.domain_x_min
        #update this center point if necessary
        center_x = 0.0
        center_y = 0.0
        center_z = 0.0

        RVE_lambda_list = []
        measured_packing_density = []
        measured_averaged_coordination_number = []
        measured_eigenvalues = []
        measured_second_invariant_of_deviatoric_tensor = []

        while side_length <= side_length_max:

            RVE_lambda_list.append(RVE_lambda)
            #measured_packing_density.append(1 - self.MeasureCubicForGettingPackingProperties(side_length, center_x, center_y, center_z, 'porosity'))
            measured_packing_density.append(1 - self.MeasureSphereForGettingPackingProperties((side_length/2), center_x, center_y, center_z, 'porosity'))
            measured_averaged_coordination_number.append(self.MeasureCubicForGettingPackingProperties(side_length, center_x, center_y, center_z, 'averaged_coordination_number'))
            eigenvalues, second_invariant_of_deviatoric_tensor = self.MeasureCubicForGettingPackingProperties(side_length, center_x, center_y, center_z, 'fabric_tensor')
            measured_eigenvalues.append(eigenvalues)
            measured_second_invariant_of_deviatoric_tensor.append(second_invariant_of_deviatoric_tensor)
            self.MeasureSphereForGettingRadialDistributionFunction(side_length/2, center_x, center_y, center_z, mean_diameter/15, mean_diameter)
            self.MeasureCubicForGettingPackingProperties(side_length, center_x, center_y, center_z, 'voronoi_input_data')

            RVE_lambda += 2
            side_length = max_diameter * RVE_lambda
            side_length = round(side_length, 4)
        
        with open("packing_properties.txt", "w") as f_w:
            for i in range(len(RVE_lambda_list)):
                f_w.write(str(RVE_lambda_list[i]) + ' '+ str(measured_packing_density[i]) + ' '+ str(measured_averaged_coordination_number[i]) + ' '+\
                           str(measured_eigenvalues[i][0]) + ' '+ str(measured_eigenvalues[i][1]) + ' '+ str(measured_eigenvalues[i][2]) + ' ' +\
                            str(measured_second_invariant_of_deviatoric_tensor[i]) + '\n')

        print("Measurement finish")

if __name__ == "__main__":

    with open("ProjectParametersDEM.json", 'r') as parameter_file:
        parameters = KratosMultiphysics.Parameters(parameter_file.read())

    model = KratosMultiphysics.Model()
    ParticlePackingGenerator(model, parameters).Run()
