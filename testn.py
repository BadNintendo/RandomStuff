import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.animation import FuncAnimation
import matplotlib.colors as mcolors

# Generate random cities with coordinates
def generate_cities(num_cities):
    cities = np.random.rand(num_cities, 3)  # Generate cities with random x, y, z coordinates
    return cities

# Function to spread bits (Morton Order)
def spread_bits(v):
    v = (v | (v << 8)) & 0x00FF00FF
    v = (v | (v << 4)) & 0x0F0F0F0F
    v = (v | (v << 2)) & 0x33333333
    v = (v | (v << 1)) & 0x55555555
    return v

# Function to compute Morton Order
def morton_order(city):
    x, y = city[:2]  # Only use x and y for Morton order
    x = int(x * 10000)
    y = int(y * 10000)
    return spread_bits(x) | (spread_bits(y) << 1)

# Function to sort and connect cities based on Morton order
def sort_cities(cities):
    if not len(cities):
        print("No cities to process. Please check the input data.")
        return []
    
    cities_sorted = sorted(cities, key=morton_order)
    sorted_path = [cities_sorted.pop(0)]

    while len(cities_sorted):
        print(f"Current sorted path length: {len(sorted_path)}")
        current_city = sorted_path[-1]
        distances = np.linalg.norm(cities_sorted - current_city, axis=1)
        closest_city_idx = np.argmin(distances)
        sorted_path.append(cities_sorted[closest_city_idx])
        cities_sorted = np.delete(cities_sorted, closest_city_idx, 0)

    sorted_path.append(sorted_path[0])  # Complete the loop
    return np.array(sorted_path)

# Draw cities and connecting lines
def draw_cities(ax, sorted_path, zoom_level=1, offset_x=0, offset_y=0):
    ax.clear()
    ax.set_facecolor('black')
    ax.set_xticks([])
    ax.set_yticks([])

    colors = list(mcolors.TABLEAU_COLORS.values())
    
    for index in range(1, len(sorted_path)):
        city = sorted_path[index]
        prev_city = sorted_path[index - 1]
        color = colors[index % len(colors)]
        ax.plot([prev_city[0] + offset_x, city[0] + offset_x],
                [prev_city[1] + offset_y, city[1] + offset_y],
                zs=[prev_city[2], city[2]], color=color)

    ax.scatter(sorted_path[:, 0] + offset_x, sorted_path[:, 1] + offset_y, sorted_path[:, 2], c='white', s=5)

# Animation loop
def animate(frame, sorted_path, ax):
    ax.clear()
    draw_cities(ax, sorted_path[:frame + 1])

# Main
num_cities = 3000  # Using fewer cities for debugging
cities = generate_cities(num_cities)
sorted_path = sort_cities(cities)

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Initial draw to set up plot
draw_cities(ax, sorted_path)

ani = FuncAnimation(fig, animate, frames=len(sorted_path), fargs=(sorted_path, ax), interval=1)

# Zoom functionality
zoom_level = 1
offset_x = 0
offset_y = 0

def on_scroll(event):
    global zoom_level, offset_x, offset_y
    zoom_factor = 1.1 if event.button == 'up' else 0.9
    zoom_level *= zoom_factor
    offset_x = event.xdata - (event.xdata - offset_x) * zoom_factor
    offset_y = event.ydata - (event.ydata - offset_y) * zoom_factor
    draw_cities(ax, sorted_path, zoom_level, offset_x, offset_y)
    plt.draw()

fig.canvas.mpl_connect('scroll_event', on_scroll)

# Pause and resume animation on click
is_animating = [True]
def on_click(event):
    if is_animating[0]:
        ani.event_source.stop()
    else:
        ani.event_source.start()
    is_animating[0] = not is_animating[0]

fig.canvas.mpl_connect('button_press_event', on_click)

plt.show()
