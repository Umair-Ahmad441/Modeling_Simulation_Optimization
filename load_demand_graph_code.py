import matplotlib.pyplot as plt
import io
import pandas as pd

data = """Hour,Time,Load_kW,Description
0,00:00,0.45,Base Load (Standby)
1,01:00,0.42,Base Load
2,02:00,0.40,Base Load
3,03:00,0.40,Base Load
4,04:00,0.45,Base Load
5,05:00,0.60,Early Morning Start
6,06:00,1.20,Morning Routine (Lights/Coffee)
7,07:00,2.80,Morning Peak (Showers/Breakfast)
8,08:00,3.20,Morning Peak (Laundry/Dishwasher)
9,09:00,1.50,Mid-day Low (Residents out)
10,10:00,1.20,Solar Window Starts
11,11:00,1.10,Solar Window
12,12:00,1.30,Lunch Time
13,13:00,1.10,Solar Window
14,14:00,1.10,Solar Window
15,15:00,1.40,Solar Window Ends
16,16:00,2.20,Evening Ramp Up
17,17:00,3.50,Dinner Prep Peak
18,18:00,4.80,Evening Peak (Full House)
19,19:00,5.20,Evening Peak (HVAC/Entertainment)
20,20:00,4.10,High Usage
21,21:00,2.50,Winding Down
22,22:00,1.20,Late Night
23,23:00,0.60,Midnight Base
24,24:00,0.45,Base Load"""

df = pd.read_csv(io.StringIO(data))

plt.figure(figsize=(12, 6))
plt.plot(df['Time'], df['Load_kW'], marker='o', linestyle='-', color='#2c3e50', linewidth=2)
plt.fill_between(df['Time'], df['Load_kW'], color='#3498db', alpha=0.3)

# Highlighting the "Solar Window" area
plt.axvspan('10:00', '15:00', color='yellow', alpha=0.1, label='Peak Solar Generation Window')

plt.title('Typical Household Hourly Load Profile', fontsize=14, fontweight='bold')
plt.xlabel('Time of Day (24h)', fontsize=12)
plt.ylabel('Power Demand (kW)', fontsize=12)
plt.xticks(rotation=45)
plt.grid(True, linestyle='--', alpha=0.6)
plt.legend()
plt.tight_layout()

plt.show()