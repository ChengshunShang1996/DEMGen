import numpy as np
import matplotlib.pyplot as plt
import os

fig, axs = plt.subplots(1, 3)

folder_name_list = ['mesher_case_gravity_1_cut_measure', 'mesher_case_gravity_2_cut_measure', 'mesher_case_gravity_3_cut_measure',
                    'fast_mesher_case_1_measure', 'fast_mesher_case_2_measure', 'fast_mesher_case_3_measure', 
                    'radius_expansion_v2_case_1_measure', 'radius_expansion_v2_case_2_measure', 'radius_expansion_v2_case_3_measure']

label_list = ['G-1', 'G-2', 'G-3', 'I-1', 'I-2', 'I-3', 'R-1', 'R-2', 'R-3']

i = 0
for aim_folder_name in folder_name_list:
    aim_file_name   = "PSD_absolute_error_1.txt"
    aim_path_for_file = os.path.join(os.getcwd(), aim_folder_name, aim_file_name)

    lambda_list = []
    abs_error_list = []
    with open(os.path.join(aim_path_for_file), 'r') as psd_error_data:
        for line in psd_error_data:
            values = [float(s) for s in line.split()]
            lambda_list.append(values[0])
            abs_error_list.append(values[1])

    i_label = label_list[i]
    if i < 3:
        axs[0].plot(lambda_list, abs_error_list, 'o--', linewidth=1.5, label = i_label)
    elif i < 6:
        axs[1].plot(lambda_list, abs_error_list, 'o--',  linewidth=1.5, label = i_label)
    elif i < 9:
        axs[2].plot(lambda_list, abs_error_list, 'o--',  linewidth=1.5, label = i_label)
    i += 1

for ax in axs.flat:
    ax.set_xlabel("$\lambda$")
    ax.set_ylabel("Sum of the PSD error / %")
    ax.set_xlim(0, 25)
    ax.set_ylim(0, 80)
    ax.legend(fontsize=8, loc=1)
    ax.grid(True, which='both')
    ax.label_outer()

plt.show()

fig = plt.figure(2)
ax = fig.add_subplot(111)

lambda_list = [4, 8, 12, 16, 20, 24]
measured_error_mean = []
measured_error_top = []
measured_error_bot = []
measured_error_max = []
measured_error_min = []
for ii in range(1,7):
    error_list = []
    for i in range(1,7):
        aim_folder_name = "mesher_case_" + str(i) + "_measure"
        aim_file_name   = "PSD_absolute_error_" + str(i) + ".txt"
        aim_path_for_file = os.path.join(os.getcwd(), aim_folder_name, aim_file_name)

        with open(os.path.join(aim_path_for_file), 'r') as psd_error_data:
            line_cnt = 0
            for line in psd_error_data:
                line_cnt += 1
                j = 0
                values = []
                for s in line.split():
                    if j < 3:
                        values.append(float(s))
                        j += 1
                if line_cnt == ii:
                    error_list.append(values[1])


    sum_error = 0.0
    for error in error_list:
        sum_error += error
    mean_error = sum_error / 6.0
    measured_error_mean.append(mean_error)
    measured_error_top.append(max(error_list) - mean_error)
    measured_error_bot.append(mean_error - min(error_list))
    measured_error_max.append(max(error_list))
    measured_error_min.append(min(error_list))

lns1 = ax.errorbar(lambda_list, measured_error_mean, yerr=(measured_error_bot, measured_error_top),\
                    lw = 2, capsize = 4, capthick = 4, ecolor = "green", color = "blue", label = "PSD error")

ax.set_xlabel("$\lambda$")
ax.set_ylabel("Averaged PSD error")

abs_error = []
for i in range(len(measured_error_max)):
    abs_error.append(measured_error_max[i] - measured_error_min[i])

#ax2 = ax.twinx()
#lns2 = ax2.plot(lambda_list, abs_error, 'bo--', color = "gray", linewidth=2, label="AE width")
#ax2.set_ylabel("Absolute error (AE) width ")
#ax2.set_ylim(0, 0.05)
#ax.set_ylim(0.15, 0.6)
#plt.title(my_title)
#h1, l1 = ax.get_legend_handles_labels()
#h2, l2 = ax2.get_legend_handles_labels()
#ax.legend(h1+h2, l1+l2, loc=1)
#ax2.set_ylim(0, 10)
#ax.set_ylim(-0.9e8, 4e8)
#plt.title(my_title)
ax.grid(True, which='both')
ax.legend()
#ax2.legend()
plt.show()
