import matplotlib.pyplot as plt

# 1. Define Data Points
battery_capacity = [0, 10, 20, 30, 40]
solar_capacity = [0, 5, 10, 15, 20]
price = [11.74, 6.1, 5.03, 2.90, 1.76]

# 2. Print the Data Table in VS Code Terminal
print("\n" + "="*50)
print(f"{'Battery (kWh)':<15} | {'Solar (kW)':<12} | {'Price (€)':<10}")
print("-"*50)
for x, y, z in zip(battery_capacity, solar_capacity, price):
    print(f"{x:<15} | {y:<12} | {z:<10.2f}")
print("="*50 + "\n")

# 3. Create the 3D Plot
fig, ax = plt.subplots(subplot_kw={"projection": "3d"})

# Set exact limits starting from 0
ax.set_xlim(0, 35)
ax.set_ylim(0, 20)
ax.set_zlim(0, 13)

# Force identical intervals on axes
ax.set_xticks([0, 10, 20, 30, 40])        # Intervals of 10
ax.set_yticks([0, 5, 10, 15, 20])     
ax.set_zticks([0, 2, 4, 6, 8, 10, 12]) 

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
    # ADDED color='darkgreen' and weight='bold' here
    ax.text(x, y, z + 0.8, f"€{z:.2f}", ha='center', fontsize=10, color='darkgreen', weight='bold')
# Axis Labels
ax.set_xlabel('Battery Capacity (kWh)')
ax.set_ylabel('Solar Capacity (kW)')
ax.set_zlabel('Price (€)')

plt.show()