import numpy as np
import matplotlib.pyplot as plt
import os

# Particle size data and corresponding frequencies (example data)
particle_sizes = [0.15, 0.18, 0.2, 0.22, 0.25, 0.275, 0.3, 0.35]
frequencies = [0.20754, 0.20754+0.15525, 0.20754+0.15525+0.13346, 0.20754+0.15525+0.13346+0.13821, 0.20754+0.15525+0.13346+0.13821+0.1751, 0.20754+0.15525+0.13346+0.13821+0.1751+0.09922, 
               0.20754+0.15525+0.13346+0.13821+0.1751+0.09922+0.05418, 0.20754+0.15525+0.13346+0.13821+0.1751+0.09922+0.05418+0.03704]

#particle_sizes = [0.0001, 0.00013, 0.00016]
#frequencies = [0.25, 0.75, 1.0]


frequencies100 = []
for i in range(len(frequencies)):
    frequencies100.append(frequencies[i] * 100)

fig, axs = plt.subplots(3, 3)

folder_name_list = ['mesher_case_gravity_1_cut_measure', 'mesher_case_gravity_2_cut_measure', 'mesher_case_gravity_3_cut_measure',
                    'fast_mesher_case_1_measure', 'fast_mesher_case_2_measure', 'fast_mesher_case_3_measure', 
                    'radius_expansion_v2_case_1_measure', 'radius_expansion_v2_case_2_measure', 'radius_expansion_v2_case_3_measure']

label_list = ['G-1', 'G-2', 'G-3', 'I-1', 'I-2', 'I-3', 'R-1', 'R-2', 'R-3']

i = 0
for aim_folder_name in folder_name_list:

    if i < 3:
        axs[0,i].semilogx(particle_sizes, frequencies100, 'bo-', linewidth=2,label="Input")
        abs_error_list = []
        lambda_list = []
        for int_i in range(8, 50, 8):
            frequencies100_sim = []
            i_name = int_i / 10000
            file_name = "PSD_" + str(i_name) + '.txt'
            with open(os.path.join(os.getcwd(), aim_folder_name, 'inletPG3_Graphs', file_name), 'r') as psd_data:
                for line in psd_data:
                    values = [float(s) for s in line.split()]
                    frequencies100_sim.append(values[1])

            # Plot the PSD curve with log scale on x-axis
            i_lambda = int_i * 4 / 8
            lambda_list.append(i_lambda)
            i_label = 'Sim $\lambda$ =' + str(i_lambda)
            axs[0,i].semilogx(particle_sizes, frequencies100_sim, 'o--', linewidth=2, label=i_label)
    elif i < 6:
        lns1 = axs[1,i-3].semilogx(particle_sizes, frequencies100, 'bo-', linewidth=2,label="Input")
        abs_error_list = []
        lambda_list = []
        for int_i in range(8, 50, 8):
            frequencies100_sim = []
            i_name = int_i / 10000
            file_name = "PSD_" + str(i_name) + '.txt'
            with open(os.path.join(os.getcwd(), aim_folder_name, 'inletPG3_Graphs', file_name), 'r') as psd_data:
                for line in psd_data:
                    values = [float(s) for s in line.split()]
                    frequencies100_sim.append(values[1])

            # Plot the PSD curve with log scale on x-axis
            i_lambda = int_i * 4 / 8
            lambda_list.append(i_lambda)
            i_label = 'Sim $\lambda$ =' + str(i_lambda)
            lns2 = axs[1,i-3].semilogx(particle_sizes, frequencies100_sim, 'o--', linewidth=2, label=i_label)
    elif i < 9:
        lns1 = axs[2, i-6].semilogx(particle_sizes, frequencies100, 'bo-', linewidth=2,label="Input")
        abs_error_list = []
        lambda_list = []
        for int_i in range(8, 50, 8):
            frequencies100_sim = []
            i_name = int_i / 10000
            file_name = "PSD_" + str(i_name) + '.txt'
            with open(os.path.join(os.getcwd(), aim_folder_name, 'inletPG3_Graphs', file_name), 'r') as psd_data:
                for line in psd_data:
                    values = [float(s) for s in line.split()]
                    frequencies100_sim.append(values[1])

            # Plot the PSD curve with log scale on x-axis
            i_lambda = int_i * 4 / 8
            lambda_list.append(i_lambda)
            i_label = 'Sim $\lambda$ =' + str(i_lambda)
            lns2 = axs[2,i-6].semilogx(particle_sizes, frequencies100_sim, 'o--', linewidth=2, label=i_label)
    i += 1

'''
        pdf_list = []
        for i in range(len(frequencies)):
            if i == 0:
                pdf_list.append(frequencies100[i])
            else:
                pdf_list.append(frequencies100[i] - frequencies100[i-1])
        
        pdf_sim_list = []
        for i in range(len(frequencies)):
            if i == 0:
                pdf_sim_list.append(frequencies100_sim[i])
            else:
                pdf_sim_list.append(frequencies100_sim[i] - frequencies100_sim[i-1])

        abs_error = 0.0
        for i in range(len(frequencies)):
            abs_error += abs(pdf_sim_list[i] - pdf_list[i])
        abs_error_list.append(abs_error)
        '''
for ax in axs.flat:
    ax.set_xlabel("Particle diameter / mm")
    ax.set_ylabel("Cumulative size distribution / %")
    ax.set_ylim(10, 110)
    ax.legend(fontsize=8, loc=4)
    ax.grid(True, which='both')
    ax.label_outer()
#ax.legend()
#ax2.legend()
plt.show()

fig = plt.figure(2)
ax = fig.add_subplot(111)
#lns3 = ax2.bar(particle_sizes, abs_error, color = "lightgray", width = 0.7, label='AE')
lns3 = ax.plot(lambda_list, abs_error_list, 'bo--', linewidth=2, label="AE")
ax.set_ylabel("Absolute error (AE) / %")
#ax2.set_ylim(0, 10)
#ax.set_ylim(-0.9e8, 4e8)
#plt.title(my_title)
ax.legend()
ax.grid(True, which='both')
#ax.legend()
#ax2.legend()
plt.show()

file_name = "PSD_absolute_error_" + str(1) + '.txt'
with open(file_name, "w") as f_w:
    for i in range(len(lambda_list)):
        f_w.write(str(lambda_list[i]) + ' '+ str(abs_error_list[i]) + '\n')
