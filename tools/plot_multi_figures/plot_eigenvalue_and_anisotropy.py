import numpy as np
import matplotlib.pyplot as plt
import os

fig, axs = plt.subplots(3, 3)

folder_name_list = ['mesher_case_gravity_1_cut_measure', 'mesher_case_gravity_2_cut_measure', 'mesher_case_gravity_3_cut_measure',
                    'fast_mesher_case_1_measure', 'fast_mesher_case_2_measure', 'fast_mesher_case_3_measure', 
                    'radius_expansion_v2_case_1_measure', 'radius_expansion_v2_case_2_measure', 'radius_expansion_v2_case_3_measure']

label_list = ['G-1', 'G-2', 'G-3', 'I-1', 'I-2', 'I-3', 'R-1', 'R-2', 'R-3']

i = 0
for aim_folder_name in folder_name_list:
    aim_file_name   = "packing_properties_" + str(1.1) + ".txt"
    aim_path_for_file = os.path.join(os.getcwd(), aim_folder_name, aim_file_name)

    lambda_list = []
    eigenvalue_1_list = []
    eigenvalue_2_list = []
    eigenvalue_3_list = []
    with open(os.path.join(aim_path_for_file), 'r') as psd_error_data:
        for line in psd_error_data:
            values = [float(s) for s in line.split()]
            lambda_list.append(values[0])
            eigenvalue_1_list.append(values[3])
            eigenvalue_2_list.append(values[4])
            eigenvalue_3_list.append(values[5])

    #i_label = label_list[i]
    if i < 3:
        axs[0,i].plot(lambda_list, eigenvalue_1_list, 'o-', linewidth=1.5, label="$F_1$")
        axs[0,i].plot(lambda_list, eigenvalue_2_list, 'o-', linewidth=1.5, label="$F_2$")
        axs[0,i].plot(lambda_list, eigenvalue_3_list, 'o-', linewidth=1.5, label="$F_3$")
    elif i < 6:
        axs[1,i-3].plot(lambda_list, eigenvalue_1_list, 'o-', linewidth=1.5, label="$F_1$")
        axs[1,i-3].plot(lambda_list, eigenvalue_2_list, 'o-', linewidth=1.5, label="$F_2$")
        axs[1,i-3].plot(lambda_list, eigenvalue_3_list, 'o-', linewidth=1.5, label="$F_3$")
    elif i < 9:
        axs[2,i-6].plot(lambda_list, eigenvalue_1_list, 'o-', linewidth=1.5, label="$F_1$")
        axs[2,i-6].plot(lambda_list, eigenvalue_2_list, 'o-', linewidth=1.5, label="$F_2$")
        axs[2,i-6].plot(lambda_list, eigenvalue_3_list, 'o-', linewidth=1.5, label="$F_3$")

    i += 1

for ax in axs.flat:
    ax.axhline(y=1/3, color='b', linestyle='--', label='1/3')
    ax.set(xlabel='$\lambda$', ylabel='Eigenvalues')

for ax in axs.flat:
    ax.set_xlim(0.0, 25)
    ax.set_ylim(0.26, 0.45)
#plt.title(my_title)
    ax.legend(fontsize=7, loc=1)
    ax.grid(True, which='both')
    ax.label_outer()

ii = 0
for ax in axs.flat:
    ax.set_title(label_list[ii])
    ii += 1
plt.show()


fig, axs = plt.subplots(1, 3)

folder_name_list = ['mesher_case_gravity_1_cut_measure', 'mesher_case_gravity_2_cut_measure', 'mesher_case_gravity_3_cut_measure',
                    'fast_mesher_case_1_measure', 'fast_mesher_case_2_measure', 'fast_mesher_case_3_measure', 
                    'radius_expansion_v2_case_1_measure', 'radius_expansion_v2_case_2_measure', 'radius_expansion_v2_case_3_measure']

label_list = ['G-1', 'G-2', 'G-3', 'I-1', 'I-2', 'I-3', 'R-1', 'R-2', 'R-3']

i = 0
for aim_folder_name in folder_name_list:
    aim_file_name   = "packing_properties_" + str(1.1) + ".txt"
    aim_path_for_file = os.path.join(os.getcwd(), aim_folder_name, aim_file_name)

    lambda_list = []
    packing_density_list = []
    with open(os.path.join(aim_path_for_file), 'r') as psd_error_data:
        for line in psd_error_data:
            values = [float(s) for s in line.split()]
            lambda_list.append(values[0])
            packing_density_list.append(values[6])

    i_label = label_list[i]
    if i < 3:
        lns3 = axs[0].plot(lambda_list, packing_density_list, 'o--', linewidth=1.5, label=i_label)
    elif i < 6:
        lns3 = axs[1].plot(lambda_list, packing_density_list, '^--', linewidth=1.5, label=i_label)
    elif i < 9:
        lns3 = axs[2].plot(lambda_list, packing_density_list, 's--', linewidth=1.5, label=i_label)

    i += 1

for ax in axs.flat:
    ax.set(xlabel='$\lambda$', ylabel='Anisotropic intensity')
    ax.set_xlim(0.0, 25)
    ax.set_ylim(0.0, 0.3)
    ax.legend(fontsize=8, loc=1)
    ax.grid(True, which='both')
    ax.label_outer()

plt.show()

############################################################################################

fig, axs = plt.subplots(1, 3)

lambda_list = [4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24]
measured_mcn_mean = []
measured_mcn_top = []
measured_mcn_bot = []
measured_mcn_max = []
measured_mcn_min = []

folder_name_list = ['mesher_case_gravity_1_cut_measure', 'mesher_case_gravity_2_cut_measure', 'mesher_case_gravity_3_cut_measure']

for ii in range(1,12):
    i = 0
    mcn_list = []
    for aim_folder_name in folder_name_list:
        aim_file_name   = "packing_properties_" + str(1.1) + ".txt"
        aim_path_for_file = os.path.join(os.getcwd(), aim_folder_name, aim_file_name)

        line_cnt = 0
        with open(os.path.join(aim_path_for_file), 'r') as psd_error_data:
            for line in psd_error_data:
                line_cnt += 1
                values = [float(s) for s in line.split()]
                if line_cnt == ii:
                    mcn_list.append(values[6])

    sum_mcn = 0.0
    for mcn in mcn_list:
        sum_mcn += mcn
    mean_mcn = sum_mcn / 3.0
    measured_mcn_mean.append(mean_mcn)
    measured_mcn_top.append(max(mcn_list) - mean_mcn)
    measured_mcn_bot.append(mean_mcn - min(mcn_list))
    measured_mcn_max.append(max(mcn_list))
    measured_mcn_min.append(min(mcn_list))

lns1 = axs[0].errorbar(lambda_list, measured_mcn_mean, yerr=(measured_mcn_bot, measured_mcn_top),\
                    lw = 1.5, capsize = 2, capthick = 2, ecolor = "green", color = "blue", label = "Anisotropic intensity - G")

#ax.set_xlabel("$\lambda$")
#ax.set_ylabel("Averaged packing density")

abs_error = []
for i in range(len(measured_mcn_max)):
    abs_error.append(measured_mcn_max[i] - measured_mcn_min[i])

ax2 = axs[0].twinx()
lns2 = ax2.plot(lambda_list, abs_error, 'o--', color = "gray", linewidth=1.5, label="AE width - G")

measured_mcn_mean = []
measured_mcn_top = []
measured_mcn_bot = []
measured_mcn_max = []
measured_mcn_min = []

folder_name_list = ['fast_mesher_case_1_measure', 'fast_mesher_case_2_measure', 'fast_mesher_case_3_measure']

for ii in range(1,12):
    i = 0
    mcn_list = []
    for aim_folder_name in folder_name_list:
        aim_file_name   = "packing_properties_" + str(1.1) + ".txt"
        aim_path_for_file = os.path.join(os.getcwd(), aim_folder_name, aim_file_name)

        line_cnt = 0
        with open(os.path.join(aim_path_for_file), 'r') as psd_error_data:
            for line in psd_error_data:
                line_cnt += 1
                values = [float(s) for s in line.split()]
                if line_cnt == ii:
                    mcn_list.append(values[6])

    sum_mcn = 0.0
    for mcn in mcn_list:
        sum_mcn += mcn
    mean_mcn = sum_mcn / 3.0
    measured_mcn_mean.append(mean_mcn)
    measured_mcn_top.append(max(mcn_list) - mean_mcn)
    measured_mcn_bot.append(mean_mcn - min(mcn_list))
    measured_mcn_max.append(max(mcn_list))
    measured_mcn_min.append(min(mcn_list))

lns3 = axs[1].errorbar(lambda_list, measured_mcn_mean, yerr=(measured_mcn_bot, measured_mcn_top),\
                    lw = 1.5, capsize = 2, capthick = 2, ecolor = "green", color = "blue", label = "Anisotropic intensity - I")

abs_error = []
for i in range(len(measured_mcn_max)):
    abs_error.append(measured_mcn_max[i] - measured_mcn_min[i])
ax3 = axs[1].twinx()
lns4 = ax3.plot(lambda_list, abs_error, 'o--', color = "gray", linewidth=1.5, label="AE width - I")

measured_mcn_mean = []
measured_mcn_top = []
measured_mcn_bot = []
measured_mcn_max = []
measured_mcn_min = []

folder_name_list = ['radius_expansion_v2_case_1_measure', 'radius_expansion_v2_case_2_measure', 'radius_expansion_v2_case_3_measure']

for ii in range(1,12):
    i = 0
    mcn_list = []
    for aim_folder_name in folder_name_list:
        aim_file_name   = "packing_properties_" + str(1.1) + ".txt"
        aim_path_for_file = os.path.join(os.getcwd(), aim_folder_name, aim_file_name)

        line_cnt = 0
        with open(os.path.join(aim_path_for_file), 'r') as psd_error_data:
            for line in psd_error_data:
                line_cnt += 1
                values = [float(s) for s in line.split()]
                if line_cnt == ii:
                    mcn_list.append(values[6])

    sum_mcn = 0.0
    for mcn in mcn_list:
        sum_mcn += mcn
    mean_mcn = sum_mcn / 3.0
    measured_mcn_mean.append(mean_mcn)
    measured_mcn_top.append(max(mcn_list) - mean_mcn)
    measured_mcn_bot.append(mean_mcn - min(mcn_list))
    measured_mcn_max.append(max(mcn_list))
    measured_mcn_min.append(min(mcn_list))

lns5 = axs[2].errorbar(lambda_list, measured_mcn_mean, yerr=(measured_mcn_bot, measured_mcn_top),\
                    lw = 1.5, capsize = 2, capthick = 2, ecolor = "green", color = "blue", label = "Anisotropic intensity - R")

abs_error = []
for i in range(len(measured_mcn_max)):
    abs_error.append(measured_mcn_max[i] - measured_mcn_min[i])
ax4 = axs[2].twinx()
lns6 = ax4.plot(lambda_list, abs_error, 'o--', color = "gray", linewidth=1.5, label="AE width - R")
ax4.set_ylabel("Absolute error (AE) width ")

for ax in axs.flat:
    ax.set(xlabel='$\lambda$', ylabel='Averaged anisotropic intensity')

h1, l1 = axs[0].get_legend_handles_labels()
h2, l2 = ax2.get_legend_handles_labels()
axs[0].legend(h1+h2, l1+l2, loc=1, fontsize=8)

h1, l1 = axs[1].get_legend_handles_labels()
h2, l2 = ax3.get_legend_handles_labels()
axs[1].legend(h1+h2, l1+l2, loc=1, fontsize=8)

h1, l1 = axs[2].get_legend_handles_labels()
h2, l2 = ax4.get_legend_handles_labels()
axs[2].legend(h1+h2, l1+l2, loc=1, fontsize=8)
ax2.set_ylim(0, 0.3)
ax3.set_ylim(0, 0.3)
ax2.set_yticks([])
ax3.set_yticks([])
ax4.set_ylim(0, 0.3)

for ax in axs.flat:
    ax.set_xlim(0.0, 25)
    ax.set_ylim(0.0, 0.3)
#   ax.legend(fontsize=8)
for ax in axs.flat:
    ax.grid(True, which='both')
    ax.label_outer()
plt.show()