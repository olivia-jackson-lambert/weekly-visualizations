"""
Daylight Hours - Polar Visualization
Showing daylight duration across 2025 as a radial chart
"""

# === IMPORTS ===
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
from datetime import datetime, timedelta
from astral import LocationInfo
from astral.sun import sun
from scipy.ndimage import gaussian_filter1d

# === CUSTOM STYLING ===
colors = {
    'daylight': '#f6ad55',      # Warm orange/gold
    'daylight_edge': '#dd6b20', # Darker orange for edge
    'night': '#2d3748',         # Dark blue-gray
    'text': '#4a5568',          # Gray for labels
    'grid': '#e2e8f0',          # Light gray for grid
}

# Adding custom fonts
fm.fontManager.addfont("assets/fonts/Lora-Regular.ttf")
fm.fontManager.addfont("assets/fonts/Lora-SemiBold.ttf")

# Setting matplotlib parameters
plt.rcParams.update({
    "figure.dpi": 120,
    "savefig.dpi": 200,
    "font.size": 10,
    "font.family": "Lora",
    "axes.titlesize": 14,
    "axes.titleweight": "semibold",
    "axes.labelsize": 10,
})

# === CONFIGURATION ===
city = LocationInfo("Edinburgh", "UK", "Europe/London", 55.9533, -3.1883)
year = 2025

# === CALCULATE DAYLIGHT DATA ===
daylight_hours = []
day_numbers = []

for day_num in range(365):
    current = datetime(year, 1, 1) + timedelta(days=day_num)
    try:
        s = sun(city.observer, date=current, tzinfo=city.timezone)
        sunrise = s["sunrise"]
        sunset = s["sunset"]
        duration = (sunset - sunrise).total_seconds() / 3600
        daylight_hours.append(duration)
        day_numbers.append(day_num)
    except Exception as e:
        # Use interpolated value if calculation fails
        if daylight_hours:
            daylight_hours.append(daylight_hours[-1])
            day_numbers.append(day_num)

# Convert to numpy arrays
daylight_hours = np.array(daylight_hours)
day_numbers = np.array(day_numbers)

# Smooth the data to remove DST jumps
daylight_smooth = gaussian_filter1d(daylight_hours, sigma=5)

# Convert day of year to angle (radians)
# 0° at top (January), going clockwise
angles = 2 * np.pi * day_numbers / 365

# Close the loop
angles = np.append(angles, angles[0])
daylight_smooth = np.append(daylight_smooth, daylight_smooth[0])

# === PLOTTING ===
fig, ax = plt.subplots(figsize=(10, 10), subplot_kw={'projection': 'polar'})

# Fill the daylight area
ax.fill(angles, daylight_smooth, color=colors['daylight'], alpha=0.6)
ax.plot(angles, daylight_smooth, color=colors['daylight_edge'], linewidth=2.5)

# Add a center reference circle at minimum daylight
min_hours = daylight_smooth.min()
theta_circle = np.linspace(0, 2 * np.pi, 100)
ax.plot(theta_circle, [min_hours] * 100, color=colors['grid'], linewidth=1, linestyle='--', alpha=0.6)

# Configure the polar plot
ax.set_theta_zero_location('N')   # January at top
ax.set_theta_direction(-1)         # Clockwise

# Set radial limits
ax.set_rlim(0, 20)

# Month labels at the 1st of each month
month_starts = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
month_angles = [2 * np.pi * d / 365 for d in month_starts]
month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
               'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
ax.set_xticks(month_angles)
ax.set_xticklabels(month_names, fontsize=14, color=colors['text'])

# Radial labels (hours) - position them at a specific angle to avoid overlap
ax.set_rticks([6, 10, 14, 18])
ax.set_yticklabels(['6h', '10h', '14h', '18h'], fontsize=12, color=colors['text'])
ax.set_rlabel_position(45)  # Put radial labels at 45 degrees

# Grid styling
ax.grid(True, color=colors['grid'], linestyle='-', linewidth=0.5, alpha=0.7)
ax.spines['polar'].set_color(colors['grid'])

# Title
ax.set_title(f'Daylight Hours in {city.name} in {year}', 
             pad=20, fontsize=24, fontweight='semibold', color=colors['night'])

# Add annotations for max/min
max_idx = daylight_smooth[:-1].argmax()  # Exclude the wrapped point
min_idx = daylight_smooth[:-1].argmin()

# Summer solstice annotation (outside the shape)
ax.annotate(f'{daylight_smooth[max_idx]:.1f}h', 
            xy=(angles[max_idx], daylight_smooth[max_idx]),
            xytext=(angles[max_idx], daylight_smooth[max_idx] + 1.5),
            ha='center', fontsize=14, color=colors['text'], fontweight='semibold')

# Winter solstice annotation (outside the shape = further from center)
ax.annotate(f'{daylight_smooth[min_idx]:.1f}h', 
            xy=(angles[min_idx], daylight_smooth[min_idx]),
            xytext=(angles[min_idx], daylight_smooth[min_idx] + 1),
            ha='center', fontsize=14, color=colors['text'], fontweight='semibold')

plt.tight_layout()
plt.savefig('figures/daylight_hours_polar.png', dpi=200, bbox_inches='tight', facecolor='white')
plt.show()

# === QUICK STATS ===
print(f"\n📊 Quick Stats for {city.name}:")
print(f"   Longest day:  {daylight_hours.max():.1f} hours (June)")
print(f"   Shortest day: {daylight_hours.min():.1f} hours (December)")
print(f"   Difference:   {daylight_hours.max() - daylight_hours.min():.1f} hours")