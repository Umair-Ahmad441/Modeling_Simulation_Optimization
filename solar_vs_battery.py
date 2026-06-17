import pulp
import matplotlib.pyplot as plt

# 1. Time Discretization (24 hours)
time_steps = range(1, 25) 

# 2. Static Inputs
P_C_values = [
    0.12, 0.12, 0.12, 0.12, 0.13, 0.14, 0.16, 0.18, 
    0.20, 0.18, 0.15, 0.14, 0.13, 0.13, 0.14, 0.16, 
    0.22, 0.30, 0.42, 0.48, 0.40, 0.30, 0.20, 0.15
]
C = {i: P_C_values[i-1] for i in time_steps}

P_L_values = [
    0.45, 0.42, 0.40, 0.40, 0.45, 0.60, 1.20, 2.80, 
    3.20, 1.50, 1.20, 1.10, 1.30, 1.10, 1.10, 1.40, 
    2.20, 3.50, 4.80, 5.20, 4.10, 2.50, 1.20, 0.60
]
P_L = {i: P_L_values[i-1] for i in time_steps}

P_PV_values = [
    0, 0, 0, 0, 0, 0.005, 0.046, 0.098, 0.091, 0.129, 
    0.259, 0.303, 0.215, 0.146, 0.129, 0.092, 0.057, 
    0.037, 0.011, 0, 0, 0, 0, 0
]

# 3. Battery Parameters
bat_capacity_max = 30.0  # Total physical capacity in kWh
b_min = bat_capacity_max * 0.20  
b_max = bat_capacity_max * 0.90  
charge_eff = 0.90       
discharge_eff = 0.95

# ==========================================
# 4. SENSITIVITY ANALYSIS LOOP
# ==========================================
# Define the range of solar multipliers (e.g., 0, 2, 4, ... up to 40)
solar_multipliers = list(range(0, 42, 1))

# Array to store the final optimal cost for each iteration
optimum_costs = []

print("Running Optimization Loop...\n")

for solar_power in solar_multipliers:
    
    # A. Update the Solar Generation Dictionary for this specific iteration
    P_PV = {i: solar_power * P_PV_values[i-1] for i in time_steps}
    
    # B. Initialize a FRESH Problem instance
    prob = pulp.LpProblem(f"Optimization_Solar_{solar_power}", pulp.LpMinimize)

    # C. Define Fresh Variables
    P_GL = pulp.LpVariable.dicts("Grid_to_Load", time_steps, lowBound=0)
    P_GB = pulp.LpVariable.dicts("Grid_to_Battery", time_steps, lowBound=0)
    P_BL = pulp.LpVariable.dicts("Battery_to_Load", time_steps, lowBound=0)
    P_SL = pulp.LpVariable.dicts("Solar_to_Load", time_steps, lowBound=0)
    P_SB = pulp.LpVariable.dicts("Solar_to_Battery", time_steps, lowBound=0)
    SoC = pulp.LpVariable.dicts("State_of_Charge", time_steps, lowBound=b_min, upBound=b_max)

    # D. Define Objective Function
    prob += pulp.lpSum([C[i] * (P_GL[i] + P_GB[i]) for i in time_steps])

    # E. Define Constraints
    for i in time_steps:
        # Power Balance
        prob += P_BL[i] + P_GL[i] + P_SL[i] == P_L[i]
        
        # Solar Generation Constraint
        prob += P_SB[i] + P_SL[i] <= P_PV[i]
        
        # Battery SoC Dynamics
        if i == 1:
            prob += SoC[i] == b_min + (P_SB[i] + P_GB[i]) * charge_eff - (P_BL[i] / discharge_eff)
        else:
            prob += SoC[i] == SoC[i-1] + (P_SB[i] + P_GB[i]) * charge_eff - (P_BL[i] / discharge_eff)

    # F. Solve the Problem
    # Turn off PuLP's internal messaging so it doesn't flood your console 20 times
    prob.solve(pulp.PULP_CBC_CMD(msg=0)) 
    
    # G. Store the objective value in our array
    current_cost = pulp.value(prob.objective)
    optimum_costs.append(current_cost)
    
    print(f"Solar Multiplier: {solar_power:2d} | Optimum Cost: €{current_cost:.2f}")

# ==========================================
# 5. GENERATE IMPACT GRAPH
# ==========================================
# Plotting how increasing solar capacity impacts the daily bill
plt.figure(figsize=(10, 6))
plt.plot(solar_multipliers, optimum_costs, marker='o', color='#2ecc71', linewidth=2.5, markersize=8)

plt.title('Impact of Solar Capacity on Energy Cost with 30 kwh Battery Storage', fontsize=16, fontweight='bold')
plt.xlabel('Solar Power Multiplier', fontsize=16)
plt.ylabel('Optimum Cost (€)', fontsize=16)
plt.grid(True, linestyle='--', alpha=0.7)
plt.xticks(range(0, 41, 5) , fontsize=16)  # Show every 5th multiplier + the last one
plt.yticks(range(0, 8, 1), fontsize=16)
# Add baseline reference (cost when solar = 0)
baseline_cost = optimum_costs[0]
plt.axhline(y=baseline_cost, color='red', linestyle=':', alpha=0.6, label=f'Baseline Cost (€{baseline_cost:.2f})')
plt.legend(fontsize=16)

plt.tight_layout()
plt.savefig('Cost_vs_Solar_Capacity.png', dpi=300)
plt.show()

print("\nFinal Array of Costs:")
print([round(cost, 2) for cost in optimum_costs])