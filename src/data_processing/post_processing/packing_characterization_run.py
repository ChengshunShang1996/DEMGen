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
import json

class ParticlePackingCharacterizationRun(DEMAnalysisStage):

    def __init__(self, model, parameters):
        super().__init__(model, parameters)
        self.parameters = parameters
        with open('ParametersDEMGen.json', 'r') as file:
            self.parameters_DEMGen = json.load(file)


    def Initialize(self):
        super().Initialize()
        self.InitializePackingCharacterization()
        #self.GetInitialDemSphereVolume()

    def InitializePackingCharacterization(self):

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
        time_step = self.spheres_model_part.ProcessInfo[TIME_STEPS]
        if time_step == 2:
            self.MeasureLocalPropertiesWithDifferentRadius()
            self.PlotAndSaveResultsInPDF()

    def MeasureLocalPropertiesWithDifferentRadius(self):

        print("Start measurement")
        max_diameter = self.parameters_DEMGen["particle_radius_max"] * 2.0
        RVE_lambda = self.parameters_DEMGen["packing_charcterization_setting"]["RVE_lambda_initial"]
        side_length = max_diameter * RVE_lambda
        side_length_max = self.domain_x_max - self.domain_x_min
        #update this center point if necessary. Center point is (0, 0 ,0) by default
        center_x = 0.0
        center_y = 0.0
        center_z = 0.0

        RVE_lambda_list = []
        measured_packing_density = []
        measured_mean_coordination_number = []
        measured_eigenvalues = []
        measured_second_invariant_of_deviatoric_tensor = []
        measured_conductivity = []

        while side_length <= side_length_max:

            RVE_lambda_list.append(RVE_lambda)
            if self.parameters_DEMGen["packing_charcterization_setting"]["measure_density_option"]:
                measured_packing_density.append(1 - self.MeasureSphereForGettingPackingProperties((side_length/2), center_x, center_y, center_z, 'porosity'))

            if self.parameters_DEMGen["packing_charcterization_setting"]["measure_mean_coordination_number_option"]:
                measured_mean_coordination_number.append(self.MeasureSphereForGettingPackingProperties((side_length/2), center_x, center_y, center_z, 'averaged_coordination_number'))

            if self.parameters_DEMGen["packing_charcterization_setting"]["measure_anisotropy_option"]:
                eigenvalues, second_invariant_of_deviatoric_tensor, measured_fabric_tensor = self.MeasureSphereForGettingPackingProperties((side_length/2), center_x, center_y, center_z, 'fabric_tensor')
                measured_eigenvalues.append(eigenvalues)
                measured_second_invariant_of_deviatoric_tensor.append(second_invariant_of_deviatoric_tensor)

            if self.parameters_DEMGen["packing_charcterization_setting"]["measure_conductivity_tensor_option"]:
                particle_number_inside, measured_non_homogenized_conductivity_tensor, conductivity_tensor_trace, angles_xy, angles_xz, angles_yz = self.MeasureSphereForGettingPackingProperties((side_length/2), center_x, center_y, center_z, 'conductivity_tensor')
                measured_conductivity.append(measured_non_homogenized_conductivity_tensor)

            '''
            if self.parameters_DEMGen["packing_charcterization_setting"]["measure_radia_distribution_function_option"]:
                self.MeasureSphereForGettingRadialDistributionFunction(side_length/2, center_x, center_y, center_z, max_diameter/15, max_diameter)

            if self.parameters_DEMGen["packing_charcterization_setting"]["measure_voronoi_input_option"]:
                self.MeasureCubicForGettingPackingProperties(side_length, center_x, center_y, center_z, 'voronoi_input_data')
            '''

            RVE_lambda += self.parameters_DEMGen["packing_charcterization_setting"]["RVE_lambda_increment"]
            side_length = max_diameter * RVE_lambda
            #side_length = round(side_length, 4)

        if self.parameters_DEMGen["packing_charcterization_setting"]["measure_density_option"]:
            with open("packing_properties_density.txt", "w") as f_w:
                for i in range(len(RVE_lambda_list)):
                    f_w.write(str(RVE_lambda_list[i]) + ' '+ str(measured_packing_density[i]) + '\n')

        if self.parameters_DEMGen["packing_charcterization_setting"]["measure_mean_coordination_number_option"]:
            with open("packing_properties_mean_coordination_number.txt", "w") as f_w:
                for i in range(len(RVE_lambda_list)):
                    f_w.write(str(RVE_lambda_list[i]) + ' ' + str(measured_mean_coordination_number[i]) + '\n')

        if self.parameters_DEMGen["packing_charcterization_setting"]["measure_anisotropy_option"]:
            with open("packing_properties_anisotropy.txt", "w") as f_w:
                for i in range(len(RVE_lambda_list)):
                    f_w.write(str(RVE_lambda_list[i]) + ' ' + str(measured_eigenvalues[i][0]) + ' '+ str(measured_eigenvalues[i][1]) + ' '+\
                               str(measured_eigenvalues[i][2]) + ' ' + str(measured_second_invariant_of_deviatoric_tensor[i]) + '\n')

        if self.parameters_DEMGen["packing_charcterization_setting"]["measure_conductivity_tensor_option"]:
            with open("packing_properties_conductivity.txt", "w") as f_w:
                for i in range(len(RVE_lambda_list)):
                    f_w.write(str(RVE_lambda_list[i]) + ' '+ str(measured_conductivity[i]) + '\n')

        print("Measurement finish")

    def PlotAndSaveResultsInPDF(self):
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_pdf import PdfPages
        from datetime import datetime

        file_names = []
        if self.parameters_DEMGen["packing_charcterization_setting"]["measure_density_option"]:
            file_names.append("packing_properties_density.txt")
        if self.parameters_DEMGen["packing_charcterization_setting"]["measure_mean_coordination_number_option"]:
            file_names.append("packing_properties_mean_coordination_number.txt")
        if self.parameters_DEMGen["packing_charcterization_setting"]["measure_anisotropy_option"]:
            file_names.append("packing_properties_anisotropy.txt")
        if self.parameters_DEMGen["packing_charcterization_setting"]["measure_conductivity_tensor_option"]:
            file_names.append("packing_properties_conductivity.txt")

        github_link = "https://github.com/ChengshunShang1996/DEMGen"
        current_time = datetime.now().strftime('%Y-%m-%d')

        with PdfPages('all_measured_results.pdf') as pdf:

            plt.figure(figsize=(8, 6))
            plt.text(0.5, 0.7, "Particle Packing Characterization", fontsize=18, ha='center')
            plt.text(0.5, 0.5, "---- Generated by DEMGen", fontsize=12, ha='center')
            plt.text(0.5, 0.4, f"{current_time}", fontsize=12, ha='center')
            plt.text(0.5, 0.3, github_link, fontsize=8, ha='center', color='blue')

            if len(file_names) == 0:
                plt.text(0.5, 0.1, "NO RESULTS ARE PRESENTED!!!", fontsize=15, ha='center', color='red')

            # Hide axes for the cover page
            plt.axis('off')

            # Save the cover page to the PDF
            pdf.savefig()
            plt.close()

            for file_name in file_names:

                if file_name == "packing_properties_density.txt":
                    lambda_list = []
                    density_list = []

                    with open(file_name, 'r') as file:
                        for line in file:
                            my_lambda, density = map(float, line.split())
                            lambda_list.append(my_lambda)
                            density_list.append(density)

                    plt.figure(figsize=(8, 6))
                    plt.plot(lambda_list, density_list, marker='o')

                    plt.xlabel('$\lambda$')

                    plt.ylabel('Packing density')
                    plt.title(f'Measured packing density')
                    #plt.legend()
                    plt.grid('both')

                    pdf.savefig()
                    plt.close()

                elif file_name == "packing_properties_mean_coordination_number.txt":
                    lambda_list = []
                    mcn_list = []

                    with open(file_name, 'r') as file:
                        for line in file:
                            my_lambda, mcn = map(float, line.split())
                            lambda_list.append(my_lambda)
                            mcn_list.append(mcn)

                    plt.figure(figsize=(8, 6))
                    plt.plot(lambda_list, mcn_list, marker='o')

                    plt.xlabel('$\lambda$')

                    plt.ylabel('MCN')
                    plt.title(f'Measured mean coordination number (MCN)')
                    #plt.legend()
                    plt.grid('both')

                    pdf.savefig()
                    plt.close()

                elif file_name == "packing_properties_anisotropy.txt":
                    self.lambda_list = []
                    eigenvalue_1_list = []
                    eigenvalue_2_list = []
                    eigenvalue_3_list = []
                    anisotrpy_intensity_list = []

                    with open(file_name, 'r') as file:
                        for line in file:
                            my_lambda, eigenvalue_1, eigenvalue_2, eigenvalue_3, anisotrpy_intensity = map(float, line.split())
                            self.lambda_list.append(my_lambda)
                            eigenvalue_1_list.append(eigenvalue_1)
                            eigenvalue_2_list.append(eigenvalue_2)
                            eigenvalue_3_list.append(eigenvalue_3)
                            anisotrpy_intensity_list.append(anisotrpy_intensity)

                    plt.figure(figsize=(8, 6))
                    plt.plot(lambda_list, eigenvalue_1_list, label = '$F$1', marker='o')
                    plt.plot(lambda_list, eigenvalue_2_list, label = '$F$2', marker='o')
                    plt.plot(lambda_list, eigenvalue_3_list, label = '$F$3', marker='o')

                    plt.axhline(y=1/3, color='blue', linestyle='--')


                    plt.xlabel('$\lambda$')

                    plt.ylabel('Eigenvalue')
                    plt.title(f'Measured eigenvalues')
                    plt.legend()
                    plt.grid('both')

                    pdf.savefig()
                    plt.close()

                    plt.figure(figsize=(8, 6))
                    plt.plot(lambda_list, anisotrpy_intensity_list, marker='o')

                    plt.xlabel('$\lambda$')
                    plt.ylabel('Anisotrpy intensity')
                    plt.title(f'Measured anisotrpy intensity')

                    #plt.legend()
                    plt.grid('both')

                    pdf.savefig()
                    plt.close()

                elif file_name == "packing_properties_conductivity.txt":
                    conductivity_tensor_list = []

                    with open(file_name, 'r') as file:
                        for line in file:
                            conductivity_tensor = float(line.split()[1])
                            conductivity_tensor_list.append(conductivity_tensor)

                    plt.figure(figsize=(8, 6))
                    plt.plot(self.lambda_list, conductivity_tensor_list, label = '$F$1', marker='o')

                    plt.xlabel('$\lambda$')

                    plt.ylabel('K')
                    plt.title(f'Measured mean conductivity')
                    #plt.legend()
                    plt.grid('both')

                    pdf.savefig()
                    plt.close()

if __name__ == "__main__":

    with open("ProjectParametersDEM.json", 'r') as parameter_file:
        parameters = KratosMultiphysics.Parameters(parameter_file.read())

    model = KratosMultiphysics.Model()
    ParticlePackingCharacterizationRun(model, parameters).Run()
