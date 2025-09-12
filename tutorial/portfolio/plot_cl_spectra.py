import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.colors import Normalize

# Read the CL data
df = pd.read_csv('CL_data.csv')

# Extract energy values (first column)
energy = df.iloc[:, 0].values

# Extract all 30 spectra (columns 1-30)
spectra_data = df.iloc[:, 1:31].values

# Create figure with multiple subplots for better visualization
fig = plt.figure(figsize=(20, 16))

# Plot 1: All spectra on a single plot with log scale and color mapping
plt.subplot(2, 2, 1)
colors = cm.viridis(np.linspace(0, 1, 30))
for i in range(30):
    plt.semilogy(energy, spectra_data[:, i], color=colors[i], alpha=0.7, linewidth=1.5, label=f'Spectrum {i+1}')

plt.xlabel('Energy (eV)', fontsize=12)
plt.ylabel('CL Intensity (a.u.)', fontsize=12)
plt.title('All 30 CL Spectra - Log Scale Overview', fontsize=14, fontweight='bold')
plt.grid(True, alpha=0.3)
plt.xlim(1.0, 4.0)
# Add colorbar to show spectrum number
sm = cm.ScalarMappable(cmap=cm.viridis, norm=Normalize(vmin=1, vmax=30))
sm.set_array([])
cbar = plt.colorbar(sm, ax=plt.gca())
cbar.set_label('Spectrum Number', fontsize=12)

# Plot 2: Selected spectra with linear scale for detail
plt.subplot(2, 2, 2)
# Show every 5th spectrum for clarity
selected_indices = [0, 4, 9, 14, 19, 24, 29]  # Spectra 1, 5, 10, 15, 20, 25, 30
selected_colors = ['blue', 'red', 'green', 'orange', 'purple', 'brown', 'pink']
for i, idx in enumerate(selected_indices):
    plt.plot(energy, spectra_data[:, idx], color=selected_colors[i], 
             linewidth=2, label=f'Spectrum {idx+1}')

plt.xlabel('Energy (eV)', fontsize=12)
plt.ylabel('CL Intensity (a.u.)', fontsize=12)
plt.title('Selected CL Spectra - Linear Scale Detail', fontsize=14, fontweight='bold')
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.grid(True, alpha=0.3)
plt.xlim(1.0, 4.0)

# Plot 3: Peak analysis - find and highlight peak positions
plt.subplot(2, 2, 3)
peak_energies = []
peak_intensities = []

for i in range(30):
    # Find the peak (maximum) for each spectrum
    peak_idx = np.argmax(spectra_data[:, i])
    peak_energy = energy[peak_idx]
    peak_intensity = spectra_data[peak_idx, i]
    peak_energies.append(peak_energy)
    peak_intensities.append(peak_intensity)

# Plot peak positions vs spectrum number
spectrum_numbers = np.arange(1, 31)
plt.scatter(spectrum_numbers, peak_energies, c=peak_intensities, 
           cmap='plasma', s=100, alpha=0.8, edgecolors='black', linewidth=1)
plt.xlabel('Spectrum Number', fontsize=12)
plt.ylabel('Peak Energy (eV)', fontsize=12)
plt.title('CL Peak Energy vs Spectrum Number', fontsize=14, fontweight='bold')
plt.grid(True, alpha=0.3)
cbar2 = plt.colorbar()
cbar2.set_label('Peak Intensity (a.u.)', fontsize=12)

# Plot 4: Heatmap representation
plt.subplot(2, 2, 4)
# Create a 2D array for the heatmap
heatmap_data = spectra_data.T  # Transpose so spectra are rows and energy points are columns

# Use log scale for better contrast
heatmap_log = np.log10(heatmap_data + 1e-30)  # Add small value to avoid log(0)

im = plt.imshow(heatmap_log, aspect='auto', cmap='hot', origin='lower',
                extent=[energy[0], energy[-1], 1, 30])
plt.xlabel('Energy (eV)', fontsize=12)
plt.ylabel('Spectrum Number', fontsize=12)
plt.title('CL Intensity Heatmap (Log Scale)', fontsize=14, fontweight='bold')
cbar3 = plt.colorbar(im)
cbar3.set_label('Log₁₀(CL Intensity)', fontsize=12)

# Add some energy reference lines for common semiconductor bandgaps
energy_refs = [1.42, 1.55, 2.2, 3.4]  # Common bandgaps in eV
for e_ref in energy_refs:
    if energy[0] <= e_ref <= energy[-1]:
        plt.axvline(x=e_ref, color='white', linestyle='--', alpha=0.7, linewidth=1)

plt.tight_layout()
plt.savefig('CL_spectra_analysis.png', dpi=300, bbox_inches='tight')
plt.show()

# Create a second figure with individual spectrum plots for detailed examination
fig2, axes = plt.subplots(6, 5, figsize=(20, 24))
axes = axes.flatten()

for i in range(30):
    ax = axes[i]
    ax.semilogy(energy, spectra_data[:, i], 'b-', linewidth=1.5)
    ax.set_title(f'Spectrum {i+1}', fontsize=12, fontweight='bold')
    ax.set_xlabel('Energy (eV)', fontsize=10)
    ax.set_ylabel('CL Intensity (a.u.)', fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(1.0, 4.0)
    
    # Highlight the peak
    peak_idx = np.argmax(spectra_data[:, i])
    peak_energy = energy[peak_idx]
    peak_intensity = spectra_data[peak_idx, i]
    ax.plot(peak_energy, peak_intensity, 'ro', markersize=6)
    ax.text(0.05, 0.95, f'Peak: {peak_energy:.2f} eV', 
            transform=ax.transAxes, fontsize=9, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

plt.tight_layout()
plt.savefig('CL_individual_spectra.png', dpi=300, bbox_inches='tight')
plt.show()

# Print summary statistics
print("CL Spectra Analysis Summary:")
print("=" * 40)
print(f"Number of spectra: 30")
print(f"Energy range: {energy[0]:.3f} - {energy[-1]:.3f} eV")
print(f"Number of energy points: {len(energy)}")
print(f"Peak energy range: {min(peak_energies):.3f} - {max(peak_energies):.3f} eV")
print(f"Peak intensity range: {min(peak_intensities):.2e} - {max(peak_intensities):.2e}")
print("\nPeak positions for each spectrum:")
for i, (peak_e, peak_i) in enumerate(zip(peak_energies, peak_intensities)):
    print(f"Spectrum {i+1:2d}: Peak at {peak_e:.3f} eV, Intensity = {peak_i:.2e}")
