import matplotlib.pyplot as plt

# Create a 3D plot
fig, ax = plt.subplots(subplot_kw={"projection": "3d"})

# Data points
battery_capacity = [0, 10, 20, 30]
solar_capacity = [0, 5, 10, 15]
price = [11.74, 8.03, 5.09, 2.90]

# Set exact limits starting from 0
ax.set_xlim(0, 35)
ax.set_ylim(0, 20)
ax.set_zlim(0, 13)

# --- FORCE EXACT TICK INTERVALS HERE ---
ax.set_xticks([0, 10, 20, 30])        # Intervals of 10
ax.set_yticks([0, 5, 10, 15, 20])     # Intervals of 5 (Prevents the 2.5 split)
ax.set_zticks([0, 2, 4, 6, 8, 10, 12]) # Fixed price intervals
# ---------------------------------------

# Draw the explicit axis lines intersecting at (0,0,0)
ax.plot([0, 35], [0, 0], [0, 0], color='black', linewidth=2)  
ax.plot([0, 0], [0, 20], [0, 0], color='black', linewidth=2)  
ax.plot([0, 0], [0, 0], [0, 13], color='black', linewidth=2)  

# Label the origin
ax.text(0, 0, 0, ' (0,0,0)', color='black', weight='bold', fontsize=10, ha='right', va='top')

# Plot points and trend line
ax.scatter(battery_capacity, solar_capacity, price, color='red', s=80, label='Data Points', zorder=5)
ax.plot(battery_capacity, solar_capacity, price, color='blue', linestyle='-', linewidth=2, label='Trend Line')

# Draw dashed projection lines
for x, y, z in zip(battery_capacity, solar_capacity, price):
    ax.plot([x, x], [y, y], [0, z], linestyle='--', color='gray', alpha=0.6)
    ax.plot([x, x], [0, y], [0, 0], linestyle='--', color='gray', alpha=0.6)
    ax.plot([0, x], [y, y], [0, 0], linestyle='--', color='gray', alpha=0.6)
    ax.plot([0, x], [0, y], [z, z], linestyle='--', color='gray', alpha=0.6)
    ax.text(x, y, z + 0.4, f"€{z:.2f}", ha='center', fontsize=9)

# Labels
ax.set_xlabel('Battery Capacity (kWh)')
ax.set_ylabel('Solar Capacity (kW)')
ax.set_zlabel('Price (€)')

ax.view_init(elev=20, azim=-55)
ax.set_title('3D Graph with Fixed Ticks')
ax.legend()

plt.show()