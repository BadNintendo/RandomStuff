import time
import colorsys

def generate_color_transition(cycle_count, total_duration):
    colors = []
    for i in range(cycle_count):
        # Normalize to a value between 0 and 1
        hue = i / cycle_count
        # Convert HSV to RGB
        rgb = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
        # Convert to 0-255 range
        rgb = tuple(int(c * 255) for c in rgb)
        colors.append(rgb)
    return colors

def display_color_sequence(colors, total_duration):
    cycle_time = total_duration / len(colors)
    for color in colors:
        # Simulate displaying color in a single pixel
        print(f"Displaying color: {color}")
        time.sleep(cycle_time)

# Total duration in seconds
total_duration = 60
# Number of transitions
cycle_count = int((60 * 60) / 3.20)

# Generate the color transitions
colors = generate_color_transition(cycle_count, total_duration)

# Display the color sequence
display_color_sequence(colors, total_duration)
