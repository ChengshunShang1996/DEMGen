import numpy as np
import matplotlib.pyplot as plt

# Particle size data and corresponding frequencies (example data)
particle_sizes = [0.15, 0.18, 0.2, 0.22, 0.25, 0.275, 0.3, 0.35]
frequencies = [0.20754, 0.20754+0.15525, 0.20754+0.15525+0.13346, 0.20754+0.15525+0.13346+0.13821, 0.20754+0.15525+0.13346+0.13821+0.1751, 0.20754+0.15525+0.13346+0.13821+0.1751+0.09922, 
               0.20754+0.15525+0.13346+0.13821+0.1751+0.09922+0.05418, 0.20754+0.15525+0.13346+0.13821+0.1751+0.09922+0.05418+0.03704]

frequencies100 = []
for i in range(len(frequencies)):
    frequencies100.append(frequencies[i] * 100)

frequencies100_sim = []
with open("PSD.txt", 'r') as psd_data:
    for line in psd_data:
        values = [float(s) for s in line.split()]
        frequencies100_sim.append(values[1])

frequencies100_sim_accu = []
for i in range(len(frequencies100_sim)):
    sim_accu = 0.0
    for j in range(len(frequencies100_sim)):
        if j <= i:
            sim_accu += frequencies100_sim[j]
    frequencies100_sim_accu.append(sim_accu)

# Plot the PSD curve with log scale on x-axis
plt.figure(figsize=(8, 4))
plt.semilogx(particle_sizes, frequencies100, 'bo-', linewidth=2,label="Input")
plt.semilogx(particle_sizes, frequencies100_sim_accu, 'ro-', linewidth=2, label="Simulated")
plt.xlabel('Particle Size / mm')
plt.ylabel('Finer / %')
plt.title('Particle Size Distribution')
plt.grid(True, which='both')
plt.xlim(0.01, 1)
plt.ylim(0, 110)
plt.legend()
plt.show()
