import time
import random
import math

def morton_order(target):
    def interleave_bits(x, y):
        def spread_bits(v):
            v = (v | (v << 8)) & 0x00FF00FF
            v = (v | (v << 4)) & 0x0F0F0F0F
            v = (v | (v << 2)) & 0x33333333
            v = (v | (v << 1)) & 0x55555555
            return v
        return spread_bits(x) | (spread_bits(y) << 1)
    x = int(target['x'] * 10000)
    y = int(target['y'] * 10000)
    return interleave_bits(x, y)

def find_closest_target(current_target, targets_sorted):
    closest_target = min(targets_sorted, key=lambda target: math.sqrt((target['x'] - current_target['x'])**2 + (target['y'] - current_target['y'])**2))
    return closest_target

def dynamic_time_adjustment(sorted_path, lead_time_ms):
    dynamic_path = []
    for i in range(len(sorted_path) - 1):
        start_target = sorted_path[i]
        end_target = sorted_path[i + 1]
        dynamic_time = lead_time_ms * (i + 1) / len(sorted_path)
        adjusted_x = start_target['x'] + (end_target['x'] - start_target['x']) * (dynamic_time / lead_time_ms)
        adjusted_y = start_target['y'] + (end_target['y'] - start_target['y']) * (dynamic_time / lead_time_ms)
        dynamic_path.append({'x': adjusted_x, 'y': adjusted_y})
    dynamic_path.append(sorted_path[0])  # Close the loop
    return dynamic_path

def predict_next_positions(current_position, speed, time_ms):
    possible_positions = []
    for angle in range(-90, 91, 90):
        rad_angle = math.radians(angle)
        next_x = current_position['x'] + speed * (time_ms / 1000) * math.cos(rad_angle)
        next_y = current_position['y'] + speed * (time_ms / 1000) * math.sin(rad_angle)
        possible_positions.append({'x': next_x, 'y': next_y})
    return random.choice(possible_positions)

def dont_matter(targets, lead_time_range=(100, 200), target_speed=1.5, your_speed=1.2):
    if not targets:
        print("No targets to process. Please check the input data.")
        return []

    start_sort_time = time.time()
    targets_sorted = sorted(targets, key=morton_order)
    sorted_path = []
    current_target = targets_sorted[0]
    sorted_path.append(current_target)

    while targets_sorted:
        targets_sorted.remove(current_target)
        if not targets_sorted:
            break
        current_target = find_closest_target(current_target, targets_sorted)
        sorted_path.append(current_target)

    if sorted_path:
        sorted_path.append(sorted_path[0])

    end_sort_time = time.time()
    sort_time = round((end_sort_time - start_sort_time) * 1000, 2)
    print(f"Sort Time (ms): {sort_time}")

    lead_time_ms = random.uniform(*lead_time_range)
    print(f"Lead Time (ms): {round(lead_time_ms, 2)}")
    
    dynamic_path = dynamic_time_adjustment(sorted_path, lead_time_ms)
    
    return dynamic_path

# Example usage
current_target = {'x': 220, 'y': 660}
predicted_position = predict_next_positions(current_target, speed=9, time_ms=120)

targets = [
    current_target,
    predicted_position
]

result = dont_matter(targets)
if result:
    first_target = result[0]
    second_to_last_target = result[-2]
    last_target = result[-1]

    print(f"First target: {first_target}")
    print(f"Second-to-last target: {second_to_last_target}")
    print(f"Last target: {last_target}")
