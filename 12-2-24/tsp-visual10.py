import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.animation import FuncAnimation
import matplotlib.colors as mcolors
import json
import os

def bit_spread(value):
    if value & 0x00FF00FF != value:
        raise ValueError("Value exceeds the allowed criteria for 8-bit and below")
    value |= ((value << 8) & 0x00FF00FF)
    value |= ((value << 4) & 0x0F0F0F0F)
    value |= ((value << 2) & 0x33333333)
    value |= ((value << 1) & 0x55555555)
    return value

def morton_code(city):
    x, y = city['x'], city['y']
    x = int(x * 10000)
    y = int(y * 10000)
    return bit_spread(x) | (bit_spread(y) << 1)

def euclidean_distance(coord1, coord2):
    return sum((a - b) ** 2 for a, b in zip(coord1, coord2)) ** 0.5

def is_path_intersect(new_path, paths):
    def cross_product_2d(a, b):
        return a[0] * b[1] - a[1] * b[0]

    def check_intersection(path, new_path):
        if len(path[0]) == 2:
            path[0].append(0)
        if len(path[1]) == 2:
            path[1].append(0)
        if len(new_path[0]) == 2:
            new_path[0].append(0)
        if len(new_path[1]) == 2:
            new_path[1].append(0)
        cross1 = cross_product_2d([path[1][i] - path[0][i] for i in range(2)], [new_path[0][i] - path[0][i] for i in range(2)])
        cross2 = cross_product_2d([path[1][i] - path[0][i] for i in range(2)], [new_path[1][i] - path[0][i] for i in range(2)])
        cross3 = cross_product_2d([new_path[1][i] - new_path[0][i] for i in range(2)], [path[0][i] - new_path[0][i] for i in range(2)])
        cross4 = cross_product_2d([new_path[1][i] - new_path[0][i] for i in range(2)], [path[1][i] - new_path[0][i] for i in range(2)])
        return (cross1 * cross2 <= 0) and (cross3 * cross4 <= 0)

    for path in paths:
        if check_intersection(path, new_path):
            return True
    return False

def connect_cities(cities):
    if not cities:
        print("No cities to process.")
        return []

    cities_sorted = sorted(cities, key=morton_code, reverse=True)
    sorted_route = [cities_sorted.pop(0)]
    paths = []

    def find_closest_city(current_coords):
        min_distance = float('inf')
        closest_city_idx = -1
        for i, city in enumerate(cities_sorted):
            city_coords = [city.get('x', 0), city.get('y', 0)]
            if 'z' in city:
                city_coords.append(city['z'])
            distance = euclidean_distance(current_coords, city_coords)
            if distance < min_distance:
                new_path = [current_coords, city_coords]
                if not is_path_intersect(new_path, paths):
                    min_distance = distance
                    closest_city_idx = i
        return closest_city_idx

    def process_cities():
        if not cities_sorted:
            return
        current_city = sorted_route[-1]
        current_coords = [current_city.get('x', 0), current_city.get('y', 0)]
        if 'z' in current_city:
            current_coords.append(current_city['z'])

        closest_city_idx = find_closest_city(current_coords)
        if closest_city_idx != -1:
            new_city = cities_sorted.pop(closest_city_idx)
            sorted_route.append(new_city)
            new_path = [current_coords, [new_city.get('x', 0), new_city.get('y', 0), new_city.get('z', 0)]]
            paths.append(new_path)
        process_cities()

    process_cities()
    sorted_route.append(sorted_route[0])
    return sorted_route

def visualize_route(ax, sorted_route, zoom=1, offset_x=0, offset_y=0):
    ax.clear()
    ax.set_facecolor('black')
    ax.set_xticks([])
    ax.set_yticks([])
    min_x = min(city.get('x', 0) for city in sorted_route)
    max_x = max(city.get('x', 0) for city in sorted_route)
    min_y = min(city.get('y', 0) for city in sorted_route)
    max_y = max(city.get('y', 0) for city in sorted_route)
    container_coords = [(min_x, min_y), (min_x, max_y), (max_x, max_y), (max_x, min_y), (min_x, min_y)]
    ax.plot([c[0] + offset_x for c in container_coords], [c[1] + offset_y for c in container_coords], color='white')
    colors = list(mcolors.TABLEAU_COLORS.values())
    for index in range(1, len(sorted_route)):
        city = sorted_route[index]
        prev_city = sorted_route[index - 1]
        color = colors[index % len(colors)]
        x_coords = [prev_city.get('x', 0) + offset_x, city.get('x', 0) + offset_x]
        y_coords = [prev_city.get('y', 0) + offset_y, city.get('y', 0) + offset_y]
        if 'z' in city and 'z' in prev_city:
            z_coords = [prev_city.get('z', 0), city.get('z', 0)]
            ax.plot(x_coords, y_coords, zs=z_coords, color=color)
        else:
            ax.plot(x_coords, y_coords, color=color)
    if 'z' in sorted_route[0]:
        ax.scatter([city.get('x', 0) + offset_x for city in sorted_route],
                   [city.get('y', 0) + offset_y for city in sorted_route],
                   [city.get('z', 0) for city in sorted_route],
                   c='white', s=5)
    else:
        ax.scatter([city.get('x', 0) + offset_x for city in sorted_route],
                   [city.get('y', 0) + offset_y for city in sorted_route],
                   c='white', s=5)

def animate_route(frame, sorted_route, ax):
    ax.clear()
    visualize_route(ax, sorted_route[:frame + 1])

def save_data(file, primary, secondary=None):
    with open(file, 'w') as f:
        data = {'primary': primary}
        if secondary:
            data['secondary'] = secondary
        json.dump(data, f)

def load_data(file):
    if os.path.exists(file):
        with open(file, 'r') as f:
            data = json.load(f)
            if isinstance(data, list):
                return data, []
            return data.get('primary', []), data.get('secondary', [])
    return [], []

def calculate_short_paths(cities):
    # Implement your logic here
    return []

file = 'usa_states.json'
primary, secondary = load_data(file)
usa_states = primary

if not usa_states:
    print("No paths found.")
else:
    sorted_route = connect_cities(usa_states)
    short_paths = []
    if not secondary:
        short_paths = calculate_short_paths(usa_states)
        save_data('sorted_paths.json', sorted_route, short_paths)
    else:
        short_paths = secondary

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d' if 'z' in usa_states[0] else 'rectilinear')
    visualize_route(ax, sorted_route)
    ani = FuncAnimation(fig, animate_route, frames=len(sorted_route), fargs=(sorted_route, ax), interval=1, repeat=False)
    plt.show()
