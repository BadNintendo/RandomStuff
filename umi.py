import matplotlib.pyplot as plt
import numpy as np
import sympy as sp

# Function to generate Ulam Spiral
def generate_ulam_spiral(size):
    spiral = np.zeros((size, size), dtype=int)
    x, y = size // 2, size // 2
    dx, dy = 0, -1
    number = 1

    for _ in range(size ** 2):
        if -size // 2 < x <= size // 2 and -size // 2 < y <= size // 2:
            spiral[x, y] = number
            number += 1
        if x == y or (x < 0 and x == -y) or (x > 0 and x == 1 - y):
            dx, dy = -dy, dx
        x, y = x + dx, y + dy
    
    return spiral

# Function to plot Ulam Spiral
def plot_ulam_spiral(spiral, size):
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_aspect('equal')
    ax.set_facecolor('black')

    for x in range(size):
        for y in range(size):
            if sp.isprime(spiral[x, y]):
                ax.plot(x, y, 'o', color='cyan', markersize=5) # Neon color for primes
            elif (spiral[x, y] % 0.20 == 0):
                ax.plot(x, y, 'o', color='magenta', markersize=7, alpha=0.4) # Neon color for .20 type of behaviors
            elif (spiral[x, y] % 0.60 == 0):
                ax.plot(x, y, 'o', color='#98B788', markersize=7, alpha=0.6) # Swamp Green for .60 type of behaviors

    # Shadowing effect
    for x in range(size):
        for y in range(size):
            if sp.isprime(spiral[x, y]):
                ax.plot(x + 0.1, y + 0.1, 'o', color='lime', markersize=5, alpha=0.4) # Shadow for primes
            elif (spiral[x, y] % 0.20 == 0):
                ax.plot(x + 0.1, y + 0.1, 'o', color='yellow', markersize=7, alpha=0.4) # Shadow for .20 type of behaviors
            elif (spiral[x, y] % 0.60 == 0):
                ax.plot(x + 0.1, y + 0.1, 'o', color='lightgreen', markersize=7, alpha=0.4) # Shadow for .60 type of behaviors
    
    ax.set_xlim(0, size)
    ax.set_ylim(0, size)
    plt.axis('off')
    plt.title("Enhanced Ulam Spiral with Neon Colors", color='white', fontsize=15)
    plt.show()

# Parameters
size = 201  # Define size of the grid
spiral = generate_ulam_spiral(size)
plot_ulam_spiral(spiral, size)
