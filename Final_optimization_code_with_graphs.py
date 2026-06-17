import pulp
import matplotlib.pyplot as plt
# 1. Time Discretization (24 hours)
time_steps = range(1, 25) 

# 2. Model Inputs (Forecasts)

#ENERGY PRICES realistic value, with varying values throughout the day.
P_C_values =  [
    0.12, 0.12, 0.12, 0.12,
    0.13, 0.14, 0.16, 0.18,
    0.20, 0.18, 0.15, 0.14,
    0.13, 0.13, 0.14, 0.16,
    0.22, 0.30, 0.42, 0.48,
    0.40, 0.30, 0.20, 0.15
]
C = {i: P_C_values[i-1] for i in time_steps}

#Load realistic value, with varying values throughout the day. 
P_L_values = [
    0.45, 0.42, 0.40, 0.40, 0.45, 0.60,
    1.20, 2.80, 3.20, 1.50, 1.20, 1.10,
    1.30, 1.10, 1.10, 1.40, 2.20, 3.50,
    4.80, 5.20, 4.10, 2.50, 1.20, 0.60
]

P_L = {i: P_L_values[i-1] for i in time_steps}

#Solar realistic value, with varying values throughout the day.
P_PV_values = [
    0, 0, 0, 0, 0,
    0.005, 0.046, 0.098, 0.091, 0.129,
    0.259, 0.303, 0.215, 0.146, 0.129,
    0.092, 0.057, 0.037, 0.011, 0,
    0, 0, 0, 0
]
P_PV = {i: 20 * P_PV_values[i-1] for i in time_steps}
print("Energy Prices (€/kWh):", C)
print("Load (kW):", P_L)
print("Solar Generation (kW):", P_PV)
# 3. Battery Parameters (UPDATED WITH LIMITS)
bat_capacity_max = 30.0  # Total physical capacity in kWh
b_min_percent = 0.20     # 20%
b_max_percent = 0.90     # 90%

# Calculate the actual kWh limits
b_min = bat_capacity_max * b_min_percent  # 2.0 kWh
b_max = bat_capacity_max * b_max_percent  # 9.0 kWh

charge_eff = 0.90      
discharge_eff = 0.95

# 4. Initialize Problem
prob = pulp.LpProblem("Battery_Optimization_With_Limits", pulp.LpMinimize)

# 5. Decision Variables 
P_GL = pulp.LpVariable.dicts("Grid_to_Load", time_steps, lowBound=0)
P_GB = pulp.LpVariable.dicts("Grid_to_Battery", time_steps, lowBound=0)
P_BL = pulp.LpVariable.dicts("Battery_to_Load", time_steps, lowBound=0)
P_SL = pulp.LpVariable.dicts("Solar_to_Load", time_steps, lowBound=0)
P_SB = pulp.LpVariable.dicts("Solar_to_Battery", time_steps, lowBound=0)

# UPDATED: State of Charge is now strictly bounded by b_min and b_max
SoC = pulp.LpVariable.dicts("State_of_Charge", time_steps, lowBound=b_min, upBound=b_max)

# 6. Objective Function 
prob += pulp.lpSum([C[i] * (P_GL[i] + P_GB[i]) for i in time_steps]), "Total_Cost"

# 7. Constraints
for i in time_steps:
    
    # A. Power Balance
    prob += P_BL[i] + P_GL[i] + P_SL[i] == P_L[i]
    
    # B. Solar Generation Constraint
    prob += P_SB[i] + P_SL[i] <= P_PV[i]
    
    # C. Battery SoC Dynamics
    if i == 1:
        # NOTE: If the battery minimum is 20%, it must start at >= 20%.
        # Let's assume it starts exactly at the minimum limit (20%)
        initial_soc = b_min 
        prob += SoC[i] == initial_soc + (P_SB[i] + P_GB[i]) * charge_eff - (P_BL[i] / discharge_eff)
    else:
        prob += SoC[i] == SoC[i-1] + (P_SB[i] + P_GB[i]) * charge_eff - (P_BL[i] / discharge_eff)

# 8. Solve & Output
prob.solve()
#print(f"Status: {pulp.LpStatus[prob.status]}")
Total_load = sum(P_L_values[i] for i in range(24))
baseline_cost = sum(P_C_values[i] * P_L_values[i] for i in range(24))
print(f"Total_load: {Total_load:.2f} KWh")
print(f"Baseline Cost (No Optimization): €{baseline_cost:.2f}")

print(f"Optimum Cost: €{pulp.value(prob.objective):.2f}")     




# 9. Export Results to DataFrame
import pandas as pd

results = pd.DataFrame({
    "Hour": list(time_steps),
    "Grid_to_Load": [P_GL[i].varValue for i in time_steps],
    "Grid_to_Battery": [P_GB[i].varValue for i in time_steps],
    "Battery_to_Load": [P_BL[i].varValue for i in time_steps],
    "Solar_to_Load": [P_SL[i].varValue for i in time_steps],
    "Solar_to_Battery": [P_SB[i].varValue for i in time_steps],
    "State_of_Charge": [SoC[i].varValue for i in time_steps]
})

print("\nResults DataFrame:")
print(results)

# 10. Print Detailed Results
print("\nDetailed Results:")
print("-" * 80)

for i in time_steps:
    print(
        f"Hour {i:2d} | "
        f"P_GL = {P_GL[i].varValue:.2f} | "
        f"P_GB = {P_GB[i].varValue:.2f} | "
        f"P_BL = {P_BL[i].varValue:.2f} | "
        f"P_SL = {P_SL[i].varValue:.2f} | "
        f"P_SB = {P_SB[i].varValue:.2f} | "
        f"SoC = {SoC[i].varValue:.2f}"
    )
# ==========================================
# 10. GENERATE SEPARATE GRAPHS
# ==========================================
# Extract values into lists for plotting
hours = list(time_steps)
val_P_GL = [P_GL[i].varValue for i in time_steps]
val_P_GB = [P_GB[i].varValue for i in time_steps]
val_P_BL = [P_BL[i].varValue for i in time_steps]
val_P_SL = [P_SL[i].varValue for i in time_steps]
val_P_SB = [P_SB[i].varValue for i in time_steps]
val_SoC = [SoC[i].varValue for i in time_steps]

# Common settings for presentation-quality graphs
fig_size = (8, 5)
dpi_setting = 300

# 1. P_GL (Grid to Load)
plt.figure(figsize=fig_size)
plt.plot(hours, val_P_GL, marker='o', color='#e74c3c', linewidth=2)
plt.title('Grid to Load (P_GL)', fontsize=16, fontweight='bold')
plt.xlabel('Time (Hours)', fontsize=16)
plt.ylabel('Power (kW)', fontsize=16)
plt.ylim(bottom=0)
plt.xticks(range(0, 25, 2), [f"{h:02d}:00" for h in range(0, 25, 2)], rotation=45, fontsize=16)
plt.yticks(fontsize=16)
plt.grid(True, linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig('Graph_1_P_GL.png', dpi=dpi_setting)
plt.close()

# 2. P_GB (Grid to Battery)
plt.figure(figsize=fig_size)
plt.plot(hours, val_P_GB, marker='o', color="#1411b6", linewidth=2)
plt.title('Grid to Battery (P_GB)', fontsize=16, fontweight='bold')
plt.xlabel('Time (Hours)', fontsize=16)
plt.ylabel('Power (kW)', fontsize=16)
plt.ylim(bottom=0)
plt.xticks(range(0, 25, 2), [f"{h:02d}:00" for h in range(0, 25, 2)], rotation=45, fontsize=16)
plt.yticks(fontsize=16)
plt.grid(True, linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig('Graph_2_P_GB.png', dpi=dpi_setting)
plt.close()

# 3. P_BL (Battery to Load)
plt.figure(figsize=fig_size)
plt.plot(hours, val_P_BL, marker='o', color='#3498db', linewidth=2)
plt.title('Battery to Load (P_BL)', fontsize=16, fontweight='bold')
plt.xlabel('Time (Hours)', fontsize=16)
plt.ylabel('Power (kW)', fontsize=16)
plt.ylim(bottom=0)
plt.xticks(range(0, 25, 2), [f"{h:02d}:00" for h in range(0, 25, 2)], rotation=45, fontsize=16)
plt.yticks(fontsize=16)
plt.grid(True, linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig('Graph_3_P_BL.png', dpi=dpi_setting)
plt.close()

# 4. P_SL (Solar to Load)
plt.figure(figsize=fig_size)
plt.plot(hours, val_P_SL, marker='o', color="#0B1B3D", linewidth=2)
#plt.title('Solar to Load (P_SL)', fontsize=16, fontweight='bold')
plt.xlabel('Time (Hours)', fontsize=16)
plt.ylabel('Power (kW)', fontsize=16)
plt.ylim(bottom=0)
plt.xticks(range(0, 25, 2), [f"{h:02d}:00" for h in range(0, 25, 2)], rotation=45, fontsize=16)
plt.yticks(fontsize=16)
plt.grid(True, linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig('Graph_4_P_SL.png', dpi=dpi_setting)
plt.close()

# 5. P_SB (Solar to Battery)
plt.figure(figsize=fig_size)
plt.plot(hours, val_P_SB, marker='o', color="#eb1409", linewidth=2)
#plt.title('Solar to Battery (P_SB)', fontsize=16, fontweight='bold')
plt.xlabel('Time (Hours)', fontsize=16)
plt.ylabel('Power (kW)', fontsize=16)
plt.ylim(bottom=0)
plt.xticks(range(0, 25, 2), [f"{h:02d}:00" for h in range(0, 25, 2)], rotation=45, fontsize=16)
plt.yticks(fontsize=16)
plt.grid(True, linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig('Graph_5_P_SB.png', dpi=dpi_setting)
plt.close()

# 6. SoC (State of Charge)
plt.figure(figsize=fig_size)
plt.plot(hours, val_SoC, marker='o', color="#8628AE", linewidth=2)
plt.title('Battery State of Charge (SoC)', fontsize=16, fontweight='bold')
plt.xlabel('Time (Hours)', fontsize=16)
plt.ylabel('Energy (kWh)', fontsize=16)
plt.ylim(0, 30.5)
plt.xticks(range(0, 25, 2), [f"{h:02d}:00" for h in range(0, 25, 2)], rotation=45, fontsize=16)
plt.yticks(fontsize=16)
plt.axhline(y=b_min, color='black', linestyle='--', alpha=0.5, label='Min Limit (20%)')
plt.axhline(y=b_max, color='black', linestyle='-.', alpha=0.5, label='Max Limit (90%)')
plt.legend()
plt.grid(True, linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig('Graph_6_SoC0.png', dpi=dpi_setting)
plt.close()

print("All 6 graphs have been successfully saved as individual PNG files.")
