import matplotlib.pyplot as plt

def plot_mohrs_circle(sigma_x, sigma_y, tau_xy):
    # Compute the principal stresses
    sigma_avg = (sigma_x + sigma_y) / 2
    R = ((sigma_x - sigma_y) / 2)**2 + tau_xy**2
    R = R**0.5

    sigma_1 = sigma_avg + R
    sigma_2 = sigma_avg - R

    # Define the circle
    circle = plt.Circle((sigma_avg, 0), R, color='b', fill=False)

    fig, ax = plt.subplots()
    ax.add_artist(circle)
    ax.set_xlim(-4, 4)
    ax.set_ylim(-4, 4)
    ax.set_aspect('equal', 'box')
    plt.axhline(0, color='black', linewidth=0.5)
    plt.axvline(0, color='black', linewidth=0.5)
    plt.grid(True)
    
    # Plot the principal stresses
    plt.plot([sigma_1], [0], 'ro')  # Sigma 1
    plt.plot([sigma_2], [0], 'ro')  # Sigma 2
    plt.title("Mohr's Circle")
    plt.xlabel("Normal Stress")
    plt.ylabel("Shear Stress")
    plt.show()

# Example usage:
sigma_x = 5
sigma_y = 1
tau_xy = 2

plot_mohrs_circle(sigma_x, sigma_y, tau_xy)
