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
import scienceplots
import numpy as np
import pandas as pd
import ast
import os
from pathlib import Path


plt.style.use(['science'])

class ParticlePackingCharacterizationRun(DEMAnalysisStage):

    def __init__(self, model, parameters):
        super().__init__(model, parameters)
        self.parameters = parameters
        with open('ParametersDEMGen.json', 'r') as file:
            self.parameters_DEMGen = KratosMultiphysics.Parameters(file.read())

    def CreateMDPA(self): # Now we ensure that we are analyzing the last packing generated from the simulation (folder inletPG_Post_Files)
        # Set the directory to search in
        script_dir = Path(__file__).resolve().parent

        meshes_dir = script_dir.parent / "inletPG_Post_Files"
        # Find all .post.msh files in inletPG_Post_Files/
        post_files = list(meshes_dir.glob("*.post.msh"))

        # Check if any .post files were found
        if not post_files:
            print("No .post files found in the folder.")
        else:
            # Find the most recently modified .post file
            latest_post_file = max(post_files, key=lambda f: f.stat().st_mtime)

            # Print the file name
            print(f"Latest .post file: {latest_post_file.name}")

        SpheresMesh = open(str(meshes_dir) + '/' + latest_post_file.name, 'r')
        SpheresMdpa = open("inletPGDEM.mdpa", 'w')

        node_section_started = False
        node_section_finished = False
        element_section_started = False
        boundary_analysis = False
        node_list = []
        coord_x_list = []
        coord_y_list = []
        coord_z_list = []
        element_list = []
        radius_list = []
        props_list = []
        zeros_list = []
        boundary_coordinates_list = []

        for Line in SpheresMesh:

            if Line.startswith('Coordinates'):
                node_section_started = True
                continue
            if node_section_started and not node_section_finished:
                if Line.startswith('End Coordinates'):
                    node_section_finished = True
                    continue
                data = Line.split(" ")
                node_list.append(data[0])
                coord_x_list.append(data[1])
                coord_y_list.append(data[2])
                coord_z_list.append(data[3])
                zeros_list.append('0')

            if Line.startswith('Elements'):
                element_section_started = True
                continue

            if element_section_started: # and not element_section_finished:
                if Line.startswith('End Elements'):
                    element_section_started = False
                    continue
                data = Line.split(" ")
                element_list.append(data[0])
                radius_list.append(data[2])
                props_list.append(data[3])

            if Line.startswith('MESH "Kratos_Line3D2_Mesh_10000" dimension 3 ElemType Linear Nnode 2'): # SubModelPart of the bounding box
                boundary_analysis = True
                continue

            if boundary_analysis:
                if not (Line.startswith('Coordinates') or Line.startswith('End Coordinates')):
                    data = Line.split(" ")
                    boundary_coordinates_list.append(float(data[1]))
                    boundary_coordinates_list.append(float(data[2]))
                    boundary_coordinates_list.append(float(data[3]))
                if Line.startswith('End Coordinates'):
                    break

        SpheresMesh.close()

        node_list = [int(i) for i in node_list]
        coord_x_list = [float(i) for i in coord_x_list]
        coord_y_list = [float(i) for i in coord_y_list]
        coord_z_list = [float(i) for i in coord_z_list]
        element_list = [int(i) for i in element_list]
        radius_list = [float(i) for i in radius_list]
        props_list = [int(i) for i in props_list]
        zeros_list = [int(i) for i in zeros_list]

        SpheresMdpa.write('''Begin ModelPartData
        //  VARIABLE_NAME value
        End ModelPartData

        Begin Properties 0
        End Properties

        Begin Nodes\n''')

        for i in range(len(node_list)):
            SpheresMdpa.write("%i %12.8f %12.8f %12.8f\n" % (node_list[i], coord_x_list[i], coord_y_list[i], coord_z_list[i]))

        SpheresMdpa.write('''End Nodes

        Begin Elements SphericParticle3D\n''')

        for i in range(len(node_list)):
            SpheresMdpa.write("%i %i %i\n" % (element_list[i], props_list[i], node_list[i]))

        SpheresMdpa.write('''End Elements

        Begin NodalData RADIUS\n''')

        for i in range(len(node_list)):
            SpheresMdpa.write("%i %i %12.8f\n" % (node_list[i], zeros_list[i], radius_list[i]))

        SpheresMdpa.write('''End NodalData

        Begin SubModelPart DEMParts_Body // Group dem // Subtree PartsCont
            Begin SubModelPartNodes\n''')

        for i in range(len(node_list)):
            SpheresMdpa.write("%i\n" % (node_list[i]))

        SpheresMdpa.write('''End SubModelPartNodes
            Begin SubModelPartElements\n''')

        for i in range(len(node_list)):
            SpheresMdpa.write("%i\n" % (element_list[i]))

        SpheresMdpa.write('''End SubModelPartElements
            Begin SubModelPartConditions
            End SubModelPartConditions
        End SubModelPart\n''')

        SpheresMdpa.close()
        print('WARNING: The assignment of the boundaries assumes the domain as a cube centered at (0,0,0)')
        length_domain = max(boundary_coordinates_list) - min(boundary_coordinates_list)
        self.parameters_DEMGen["domain_length_x"].SetDouble(length_domain)
        self.parameters_DEMGen["domain_length_y"].SetDouble(length_domain)
        self.parameters_DEMGen["domain_length_z"].SetDouble(length_domain)
        self.parameters["BoundingBoxMinX"].SetDouble(min(boundary_coordinates_list))
        self.parameters["BoundingBoxMaxX"].SetDouble(max(boundary_coordinates_list))
        self.parameters["BoundingBoxMinY"].SetDouble(min(boundary_coordinates_list))
        self.parameters["BoundingBoxMaxY"].SetDouble(max(boundary_coordinates_list))
        self.parameters["BoundingBoxMinZ"].SetDouble(min(boundary_coordinates_list))
        self.parameters["BoundingBoxMaxZ"].SetDouble(max(boundary_coordinates_list))

    def Initialize(self):
        super().Initialize()
        self.InitializePackingCharacterization()

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
        max_diameter = self.parameters_DEMGen["particle_radius_max"].GetDouble() * 2.0
        RVE_lambda = self.parameters_DEMGen["packing_charcterization_setting"]["RVE_lambda_initial"].GetInt()
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
        measured_fabric_tensor = []
        diagram_xy = []
        diagram_xz = []
        diagram_yz = []
        fabric_tensor_list = []
        conductivity_tensor_list = []
        n_particles_list = []

        while side_length <= side_length_max:

            RVE_lambda_list.append(RVE_lambda)
            if self.parameters_DEMGen["packing_charcterization_setting"]["measure_density_option"].GetBool():
                measured_packing_density.append(1 - self.MeasureSphereForGettingPackingProperties((side_length/2), center_x, center_y, center_z, 'porosity'))

            if self.parameters_DEMGen["packing_charcterization_setting"]["measure_mean_coordination_number_option"].GetBool():
                measured_mean_coordination_number.append(self.MeasureSphereForGettingPackingProperties((side_length/2), center_x, center_y, center_z, 'averaged_coordination_number'))

            if self.parameters_DEMGen["packing_charcterization_setting"]["measure_anisotropy_option"].GetBool():
                eigenvalues, second_invariant_of_deviatoric_tensor, fabric_tensor = self.MeasureSphereForGettingPackingProperties((side_length/2), center_x, center_y, center_z, 'fabric_tensor')
                measured_eigenvalues.append(eigenvalues)
                measured_second_invariant_of_deviatoric_tensor.append(second_invariant_of_deviatoric_tensor)
                measured_fabric_tensor.append(fabric_tensor[0][0])
                measured_fabric_tensor.append(fabric_tensor[1][1])
                measured_fabric_tensor.append(fabric_tensor[2][2])
                fabric_tensor_list.append(fabric_tensor)

            if self.parameters_DEMGen["packing_charcterization_setting"]["measure_conductivity_tensor_option"].GetBool():
                n_particles, conductivity_tensor, measured_non_homogenized_conductivity_tensor_trace, angles_xy, angles_xz, angles_yz = self.MeasureSphereForGettingPackingProperties((side_length/2), center_x, center_y, center_z, 'conductivity_tensor')
                measured_conductivity.append(measured_non_homogenized_conductivity_tensor_trace)
                diagram_xy.append(angles_xy)
                diagram_xz.append(angles_xz)
                diagram_yz.append(angles_yz)
                conductivity_tensor_list.append(conductivity_tensor)
                n_particles_list.append(n_particles)


            '''
            if self.parameters_DEMGen["packing_charcterization_setting"]["measure_radia_distribution_function_option"]:
                self.MeasureSphereForGettingRadialDistributionFunction(side_length/2, center_x, center_y, center_z, max_diameter/15, max_diameter)

            if self.parameters_DEMGen["packing_charcterization_setting"]["measure_voronoi_input_option"]:
                self.MeasureCubicForGettingPackingProperties(side_length, center_x, center_y, center_z, 'voronoi_input_data')
            '''

            RVE_lambda += self.parameters_DEMGen["packing_charcterization_setting"]["RVE_lambda_increment"].GetInt()
            side_length = max_diameter * RVE_lambda
            #side_length = round(side_length, 4)

        if self.parameters_DEMGen["packing_charcterization_setting"]["measure_density_option"].GetBool():
            with open("packing_properties_density.txt", "w") as f_w:
                for i in range(len(RVE_lambda_list)):
                    f_w.write(str(RVE_lambda_list[i]) + ' '+ str(measured_packing_density[i]) + '\n')

        if self.parameters_DEMGen["packing_charcterization_setting"]["measure_mean_coordination_number_option"].GetBool():
            with open("packing_properties_mean_coordination_number.txt", "w") as f_w:
                for i in range(len(RVE_lambda_list)):
                    f_w.write(str(RVE_lambda_list[i]) + ' ' + str(measured_mean_coordination_number[i]) + '\n')

        if self.parameters_DEMGen["packing_charcterization_setting"]["measure_anisotropy_option"].GetBool():
            with open("packing_properties_anisotropy.txt", "w") as f_w:
                for i in range(len(RVE_lambda_list)):
                    f_w.write(str(RVE_lambda_list[i]) + ' ' + str(measured_eigenvalues[i][0]) + ' '+ str(measured_eigenvalues[i][1]) + ' '+\
                               str(measured_eigenvalues[i][2]) + ' ' + str(measured_second_invariant_of_deviatoric_tensor[i]) + ' ' + str(measured_fabric_tensor[i]) + '\n')
            df_F = pd.DataFrame(data={"F": fabric_tensor_list})
            df_F.to_csv("fabric_tensor_diagonal.csv", sep=";")

        if self.parameters_DEMGen["packing_charcterization_setting"]["measure_conductivity_tensor_option"].GetBool():
            with open("packing_properties_conductivity.txt", "w") as f_w:
                for i in range(len(n_particles_list)):
                    f_w.write(str(n_particles_list[i]) + ' ' + str(measured_conductivity[i]) + '\n')
            df = pd.DataFrame(data={"rose_xy": diagram_xy, "rose_xz": diagram_xz, "rose_yz": diagram_yz})
            df.to_csv("rose_diagrams_direction.csv", sep=";")
            df_K = pd.DataFrame(data={"K": conductivity_tensor_list})
            df_K.to_csv("conductivity_tensor_diagonal.csv", sep=";")


        print("Measurement finish")

    def PlotAndSaveResultsInPDF(self):
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_pdf import PdfPages
        from datetime import datetime

        file_names = []
        if self.parameters_DEMGen["packing_charcterization_setting"]["measure_density_option"].GetBool():
            file_names.append("packing_properties_density.txt")
        if self.parameters_DEMGen["packing_charcterization_setting"]["measure_mean_coordination_number_option"].GetBool():
            file_names.append("packing_properties_mean_coordination_number.txt")
        if self.parameters_DEMGen["packing_charcterization_setting"]["measure_anisotropy_option"]:
            file_names.append("packing_properties_anisotropy.txt")
        if self.parameters_DEMGen["packing_charcterization_setting"]["measure_conductivity_tensor_option"].GetBool():
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
                    plt.plot(lambda_list[1:], density_list[1:], marker='o')

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
                    plt.plot(lambda_list[1:], mcn_list[1:], marker='o')

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
                    fabric_tensor_trace_list = []
                    fabric_tensor_XX_list = []
                    fabric_tensor_YY_list = []
                    fabric_tensor_ZZ_list = []
                    anisotropy_intensity_list = []

                    df = pd.read_csv("fabric_tensor_diagonal.csv",sep=";")
                        # Parse the NumPy-like string using np.fromstring
                    def parse_fabric_tensor(s):
                        # Remove outer brackets and parse numbers
                        numbers = np.fromstring(s.replace('[', '').replace(']', ''), sep=' ')
                        return numbers.reshape(3, 3)  # Assumes a 3x3 tensor
                    # Apply parser to column
                    data_base = df["F"].apply(parse_fabric_tensor)

                    for i in range(0,len(data_base)):
                        fabric_tensor_XX_list.append(data_base[i][0][0])
                        fabric_tensor_YY_list.append(data_base[i][1][1])
                        fabric_tensor_ZZ_list.append(data_base[i][2][2])

                    with open(file_name, 'r') as file:
                        for line in file:
                            my_lambda, eigenvalue_1, eigenvalue_2, eigenvalue_3, anisotropy_intensity, fabric_tensor_trace = map(float, line.split())
                            self.lambda_list.append(my_lambda)
                            eigenvalue_1_list.append(eigenvalue_1)
                            eigenvalue_2_list.append(eigenvalue_2)
                            eigenvalue_3_list.append(eigenvalue_3)
                            anisotropy_intensity_list.append(anisotropy_intensity)
                            fabric_tensor_trace_list.append(fabric_tensor_trace)

                    plt.figure(figsize=(8, 6))
                    plt.plot(lambda_list[1:], eigenvalue_1_list[1:], label = '$F$1', marker='o')
                    plt.plot(lambda_list[1:], eigenvalue_2_list[1:], label = '$F$2', marker='o')
                    plt.plot(lambda_list[1:], eigenvalue_3_list[1:], label = '$F$3', marker='o')


                    plt.axhline(y=1/3, color='blue', linestyle='--')


                    plt.xlabel('$\lambda$')

                    plt.ylabel('Eigenvalue')
                    plt.title(f'Measured eigenvalues')
                    plt.legend()
                    plt.grid('both')

                    pdf.savefig()
                    plt.close()

                    plt.figure(figsize=(8, 6))
                    plt.plot(lambda_list[1:], anisotropy_intensity_list[1:], marker='o')

                    plt.xlabel('$\lambda$')
                    plt.ylabel('Anisotropy intensity')
                    plt.title(f'Measured anisotropy intensity')


                    plt.grid('both')

                    pdf.savefig()
                    plt.close()

                    plt.figure(figsize=(8, 6))
                    plt.plot(lambda_list[1:], fabric_tensor_trace_list[1:], marker='o', label = r'Tr($\pmb{F}$)')
                    plt.plot(lambda_list[1:], fabric_tensor_XX_list[1:], marker = 'o', label = r'$F_{xx}$')
                    plt.plot(lambda_list[1:], fabric_tensor_YY_list[1:], marker = 'o', label = r'$F_{yy}$')
                    plt.plot(lambda_list[1:], fabric_tensor_ZZ_list[1:], marker = 'o', label = r'$F_{zz}$')

                    plt.xlabel('$\lambda$')
                    plt.ylabel('F')
                    plt.title(f'Measured fabric tensor trace')
                    plt.legend()

                    plt.grid('both')

                    pdf.savefig()
                    plt.close()

                elif file_name == "packing_properties_conductivity.txt":
                    conductivity_tensor_list = []
                    conductivity_tensor_XX_list = []
                    conductivity_tensor_YY_list = []
                    conductivity_tensor_ZZ_list = []
                    n_particles_list = []

                    df = pd.read_csv("conductivity_tensor_diagonal.csv",sep=";")
                    data_base = df["K"].apply(ast.literal_eval)
                    for i in range(0,len(data_base)):
                        conductivity_tensor_XX_list.append(data_base[i][0])
                        conductivity_tensor_YY_list.append(data_base[i][1])
                        conductivity_tensor_ZZ_list.append(data_base[i][2])

                    with open(file_name, 'r') as file:
                        for line in file:
                            n_particles = int(float(line.split()[0]))
                            conductivity_tensor = float(line.split()[1])
                            conductivity_tensor_list.append(conductivity_tensor)
                            n_particles_list.append(n_particles)

                    plt.figure(figsize=(8, 6))

                    fig, ax1 = plt.subplots()
                    fig.set_figheight(6)
                    fig.set_figwidth(8)

                    ax1.set_xlabel('$\lambda$')
                    ax1.set_ylabel("Mean Value K", color="blue")
                    line1, = ax1.plot(self.lambda_list[1:], conductivity_tensor_list[1:], marker='o', label=r'Tr($\pmb{K}$)',zorder=10)
                    line2, = ax1.plot(self.lambda_list[1:], conductivity_tensor_XX_list[1:],  marker='o', label=r'$K_{xx}$',zorder=10)
                    line3, = ax1.plot(self.lambda_list[1:], conductivity_tensor_YY_list[1:], marker='o', label=r'$K_{yy}$',zorder=10)
                    line4, = ax1.plot(self.lambda_list[1:], conductivity_tensor_ZZ_list[1:], marker='o', label=r'$K_{zz}$',zorder=10)
                    ax1.tick_params(axis="y", labelcolor="blue")

                    plt.grid(zorder=0)

                    # Add legends
                    lines = [line1, line2, line3, line4]
                    labels = [line.get_label() for line in lines]
                    ax1.legend(lines, labels)

                    pdf.savefig()
                    plt.close()

                    ### ROSES CREATION ###

                    fig, axes = plt.subplots(4, 6, figsize=(30, 20), subplot_kw={'projection': 'polar'})
                    fig.suptitle(f'Rose diagram in XY direction', fontsize=25)
                    axes = axes.flatten()

                    df = pd.read_csv("rose_diagrams_direction.csv",sep=";")

                    for i, (ax, angles) in enumerate(zip(axes, df['rose_xy'].apply(ast.literal_eval))):
                        # Bin the angles into 10-degree intervals
                        bins = np.arange(0, 370, 10)  # Bins from 0 to 360 degrees in steps of 10
                        hist, bin_edges = np.histogram(angles, bins=bins, density=True)

                        # Normalize the histogram to percentages
                        if hist.sum() > 0:
                            ax.grid(zorder=2)
                            hist_percent = hist / hist.sum()
                            ax.bar(np.deg2rad(bin_edges[:-1]), hist_percent, width=np.deg2rad(10), color='skyblue', edgecolor='black')
                            ax.set_title(f'N $ = $ {n_particles_list[i]}', fontsize=12)
                            ax.grid(color='gray', linewidth=0.5, zorder=0)

                    pdf.savefig(fig)
                    plt.close()

                    fig, axes = plt.subplots(4, 6, figsize=(30, 20), subplot_kw={'projection': 'polar'})
                    fig.suptitle(f'Rose diagram in XZ direction', fontsize=25)
                    axes = axes.flatten()

                    for i, (ax, angles) in enumerate(zip(axes, df['rose_xz'].apply(ast.literal_eval))):
                        # Bin the angles into 10-degree intervals
                        bins = np.arange(0, 370, 10)  # Bins from 0 to 360 degrees in steps of 10
                        hist, bin_edges = np.histogram(angles, bins=bins, density=True)

                        # Normalize the histogram to percentages
                        if hist.sum() > 0:
                            ax.grid(zorder=2)
                            hist_percent = hist / hist.sum()
                            ax.bar(np.deg2rad(bin_edges[:-1]), hist_percent, width=np.deg2rad(10), color='skyblue', edgecolor='black',zorder=1)
                            ax.set_title(f'N $ = $ {n_particles_list[i]}', fontsize=12)

                    pdf.savefig(fig)
                    plt.close()

                    fig, axes = plt.subplots(4, 6, figsize=(30, 20), subplot_kw={'projection': 'polar'})
                    fig.suptitle(f'Rose diagram in YZ direction', fontsize=25)
                    axes = axes.flatten()

                    for i, (ax, angles) in enumerate(zip(axes, df['rose_yz'].apply(ast.literal_eval))):
                        # Bin the angles into 10-degree intervals
                        bins = np.arange(0, 370, 10)  # Bins from 0 to 360 degrees in steps of 10
                        hist, bin_edges = np.histogram(angles, bins=bins, density=True)

                        # Normalize the histogram to percentages
                        if hist.sum() > 0:
                            # Customize the grid and set its zorder (bottom layer)
                            ax.grid(color='gray', linestyle='-', linewidth=0.5, zorder=2)
                            # Bring axis labels and tick labels to the front
                            for label in ax.get_xticklabels() + ax.get_yticklabels():
                                label.set_zorder(0)  # Set zorder for tick labels (front layer)
                            hist_percent = hist / hist.sum()
                            ax.bar(np.deg2rad(bin_edges[:-1]), hist_percent, width=np.deg2rad(10), color='skyblue', edgecolor='black',zorder=1)
                            ax.set_title(f'N $ = $ {n_particles_list[i]}', fontsize=12)

                    pdf.savefig(fig)
                    plt.close()

if __name__ == "__main__":

    with open("ProjectParametersDEM.json", 'r') as parameter_file:
        parameters = KratosMultiphysics.Parameters(parameter_file.read())

    model = KratosMultiphysics.Model()
    packing_characterizer = ParticlePackingCharacterizationRun(model, parameters)
    packing_characterizer.CreateMDPA()
    packing_characterizer.Run()
