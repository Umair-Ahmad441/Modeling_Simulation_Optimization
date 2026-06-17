import matplotlib.pyplot as plt

# 1. Time Discretization (Hours 1 to 24)
time_steps = list(range(1, 25))

# 2. Electricity Prices
P_C_values = [
    0.12, 0.12, 0.12, 0.12,
    0.13, 0.14, 0.16, 0.18,
    0.20, 0.18, 0.15, 0.14,
    0.13, 0.13, 0.14, 0.16,
    0.22, 0.30, 0.42, 0.48,
    0.40, 0.30, 0.20, 0.15
]

# 3. Setup the Figure
plt.figure(figsize=(10, 6))


plt.plot(time_steps, P_C_values, marker='o', color='#e74c3c', linewidth=2)

# 4. Formatting labels and titles
plt.xlabel('Time (Hours)', fontsize=20,)
plt.ylabel('Price (€/kWh)', fontsize=20)

# Set X-axis to show every single hour clearly
plt.xticks(range(0, 24, 3), [f"{h:02d}:00" for h in range(0, 24, 3)], rotation=45, fontsize=24)
plt.yticks(fontsize=24)

# Start Y-axis at 0 so the visual scale isn't distorted
plt.ylim(bottom=0, top=max(P_C_values) + 0.05) 
plt.grid(True, linestyle='--', alpha=0.7)

# Adjust layout to prevent clipping
plt.tight_layout()

# 5. Save the graph with the exact requested name
filename = 'Electricity Price Graph_May 8, 2019.png'
plt.savefig(filename, dpi=300, bbox_inches='tight')

print(f"Graph successfully saved as: {filename}")

# Optional: Show the plot on your screen
plt.show()