import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.animation import FuncAnimation
import matplotlib.colors as mcolors
import json
import os

# Function to spread bits (Morton Order)
def spread_bits(v):
    v = (v | (v << 8)) & 0x00FF00FF
    v = (v | (v << 4)) & 0x0F0F0F0F
    v = (v | (v << 2)) & 0x33333333
    v = (v | (v << 1)) & 0x55555555
    return v

# Function to compute Morton Order
def morton_order(city):
    x, y = city['x'], city['y']
    x = int(x * 10000)
    y = int(y * 10000)
    return spread_bits(x) | (spread_bits(y) << 1)

# Function to check if a path intersects with any existing paths
def path_intersects(new_path, existing_paths):
    for path in existing_paths:
        path = [np.array(p) for p in path]
        new_path = [np.array(p) for p in new_path]

        # Ensure all paths are 3D by adding a zero z-coordinate if missing
        if len(path[0]) == 2:
            path[0] = np.append(path[0], 0)
        if len(path[1]) == 2:
            path[1] = np.append(path[1], 0)
        if len(new_path[0]) == 2:
            new_path[0] = np.append(new_path[0], 0)
        if len(new_path[1]) == 2:
            new_path[1] = np.append(new_path[1], 0)
        
        cross1 = np.cross(path[1] - path[0], new_path[0] - path[0])
        cross2 = np.cross(path[1] - path[0], new_path[1] - path[0])
        cross3 = np.cross(new_path[1] - new_path[0], path[0] - new_path[0])
        cross4 = np.cross(new_path[1] - new_path[0], path[1] - new_path[0])

        if (np.all(cross1 * cross2 <= 0) and np.all(cross3 * cross4 <= 0)):
            return True
    return False

# Function to sort and connect cities from highest to lowest x and y values
def sort_cities(cities):
    if not len(cities):
        print("No cities to process. Please check the input data.")
        return []

    # Sort cities based on the highest value of x and y
    cities_sorted = sorted(cities, key=lambda c: (c['x'], c['y']), reverse=True)
    sorted_path = [cities_sorted.pop(0)]
    existing_paths = []

    while len(cities_sorted):
        current_city = sorted_path[-1]
        current_coords = [current_city.get('x', 0), current_city.get('y', 0)]
        if 'z' in current_city:
            current_coords.append(current_city['z'])

        min_distance = float('inf')
        closest_city_idx = -1
        
        for i, city in enumerate(cities_sorted):
            city_coords = [city.get('x', 0), city.get('y', 0)]
            if 'z' in city:
                city_coords.append(city['z'])
            
            distance = np.linalg.norm(np.array(city_coords) - np.array(current_coords))
            if distance < min_distance:
                new_path = [np.array(current_coords), np.array(city_coords)]
                if not path_intersects(new_path, existing_paths):
                    min_distance = distance
                    closest_city_idx = i

        sorted_path.append(cities_sorted.pop(closest_city_idx))
        new_path = [np.array([current_city['x'], current_city['y'], current_city.get('z', 0)]), 
                    np.array([sorted_path[-1]['x'], sorted_path[-1]['y'], sorted_path[-1].get('z', 0)])]
        existing_paths.append(new_path)

    sorted_path.append(sorted_path[0])  # Complete the loop
    return sorted_path

# Draw cities and connecting lines within a bounded container
def draw_cities(ax, sorted_path, zoom_level=1, offset_x=0, offset_y=0):
    ax.clear()
    ax.set_facecolor('black')
    ax.set_xticks([])
    ax.set_yticks([])

    # Find min and max of x and y to define the container
    min_x = min(city.get('x', 0) for city in sorted_path)
    max_x = max(city.get('x', 0) for city in sorted_path)
    min_y = min(city.get('y', 0) for city in sorted_path)
    max_y = max(city.get('y', 0) for city in sorted_path)

    # Draw container outline in white
    container_coords = [
        (min_x, min_y), (min_x, max_y), (max_x, max_y), (max_x, min_y), (min_x, min_y)
    ]
    ax.plot([c[0] + offset_x for c in container_coords],
            [c[1] + offset_y for c in container_coords], color='white')

    colors = list(mcolors.TABLEAU_COLORS.values())

    for index in range(1, len(sorted_path)):
        city = sorted_path[index]
        prev_city = sorted_path[index - 1]
        color = colors[index % len(colors)]
        x_coords = [prev_city.get('x', 0) + offset_x, city.get('x', 0) + offset_x]
        y_coords = [prev_city.get('y', 0) + offset_y, city.get('y', 0) + offset_y]
        if 'z' in city and 'z' in prev_city:
            z_coords = [prev_city.get('z', 0), city.get('z', 0)]
            ax.plot(x_coords, y_coords, zs=z_coords, color=color)
        else:
            ax.plot(x_coords, y_coords, color=color)

    if 'z' in sorted_path[0]:
        ax.scatter([city.get('x', 0) + offset_x for city in sorted_path], 
                   [city.get('y', 0) + offset_y for city in sorted_path], 
                   [city.get('z', 0) for city in sorted_path], 
                   c='white', s=5)
    else:
        ax.scatter([city.get('x', 0) + offset_x for city in sorted_path], 
                   [city.get('y', 0) + offset_y for city in sorted_path], 
                   c='white', s=5)

# Animation loop
def animate(frame, sorted_path, ax):
    ax.clear()
    draw_cities(ax, sorted_path[:frame + 1])

# Save and load object data
def save_object_data(filename, obj):
    with open(filename, 'w') as file:
        json.dump(obj, file)

def load_object_data(filename):
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            return json.load(file)
    else:
        return []

def get_file_info(filename):
    if os.path.exists(filename):
        size = os.path.getsize(filename)
        with open(filename, 'r') as file:
            lines = file.readlines()
        return size, len(lines)
    else:
        return 0, 0

# Main

filename = 'usa_states.json'
usa_states = load_object_data(filename)

if not usa_states:
    print("No paths were given to calculate.")
    print("Example command to issue the request:")
    print("python script_name.py --num_cities 50")
else:
    sorted_path = sort_cities(usa_states)
    save_object_data('sorted_path.json', sorted_path)

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d' if 'z' in usa_states[0] else 'rectilinear')

    # Initial draw to set up plot
    draw_cities(ax, sorted_path)

    ani = FuncAnimation(fig, animate, frames=len(sorted_path), fargs=(sorted_path, ax), interval=1, repeat=False)
    plt.show()

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