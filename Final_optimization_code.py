import pulp

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

#Solor realistic value, with varying values throughout the day.
P_PV_values = [
    0, 0, 0, 0, 0,
    0.005, 0.046, 0.098, 0.091, 0.129,
    0.259, 0.303, 0.215, 0.146, 0.129,
    0.092, 0.057, 0.037, 0.011, 0,
    0, 0, 0, 0
]
P_PV = {i: 5 * P_PV_values[i-1] for i in time_steps}
print("Energy Prices (€/kWh):", C)
print("Load (kW):", P_L)
print("Solar Generation (kW):", P_PV)
# 3. Battery Parameters (UPDATED WITH LIMITS)
bat_capacity_max = 20.0  # Total physical capacity in kWh
b_min_percent = 0.20     # 20%
b_max_percent = 0.90     # 90%

# Calculate the actual kWh limits
b_min = bat_capacity_max * b_min_percent  # 2.0 kWh
b_max = bat_capacity_max * b_max_percent  # 9.0 kWh

charge_eff = 0.8      
discharge_eff = 1

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
print(f"Total Cost: €{pulp.value(prob.objective):.2f}")     




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