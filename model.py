# --- START OF FILE model.py ---

import numpy as np

class PhysicsModel:
    """
    Calculates the trajectory of a point mass moving on the inner surface
    of a sphere. The path follows a prescribed Archimedean-like spiral,
    and the simulation stops if the normal force becomes negative (detachment).
    """
    def __init__(self, radius):
        """
        Initializes the physics model.

        Args:
            radius (float): The radius of the sphere (meters).
        """
        if radius <= 0:
            raise ValueError("Radius must be positive")
        self.radius = radius
        self.g = 9.81  # Acceleration due to gravity (m/s^2)

    def calculate_trajectory(self, acceleration, k, sim_time, mass):
        """
        Calculates the trajectory based on a prescribed spiral path.

        Args:
            acceleration (float): Parameter related to the rate of spiraling (m/s^2).
                                  Interpreted as R * alpha_phi.
            k (float):            Parameter controlling the pitch of the spiral.
            sim_time (float):     Total simulation time (seconds).
            mass (float):         Mass of the point (kg).

        Returns:
            list: A list of (x, y, z) tuples for the animation (Y-up).
                  Returns an empty list if detachment occurs immediately.
        """
        if self.radius <= 0:
             print("Error: Radius must be positive.")
             return []
        if sim_time <= 0:
             print("Warning: Simulation time must be positive.")
             return []
        if mass <= 0:
            print("Warning: Mass must be positive.")

        trajectory_points = []
        dt = 0.01  # Time step for simulation (seconds)
        n_steps = int(sim_time / dt)

        if self.radius == 0:
            alpha_phi = 0
        else:
            alpha_phi = acceleration / self.radius # rad/s^2

        # *** ИЗМЕНЕНИЕ ЗДЕСЬ ***
        initial_theta_offset = 0.01 # Небольшой угол в радианах, чтобы начать чуть выше южного полюса
        # ***********************

        print(f"Starting calculation: R={self.radius}m, acc_param={acceleration}, k={k}, time={sim_time}s, mass={mass}kg")
        print(f"Derived alpha_phi = {alpha_phi:.4f} rad/s^2")
        print(f"Starting slightly above South Pole by {np.degrees(initial_theta_offset):.3f} degrees.")


        for i in range(n_steps):
            t = i * dt

            # Kinematic path definition (Physics standard: Z-up, theta from Z-axis)
            phi = 0.5 * alpha_phi * t**2

            # *** ИЗМЕНЕНИЕ ЗДЕСЬ ***
            # Начинаем с theta = pi - initial_theta_offset и уменьшаем
            theta = np.pi - initial_theta_offset - 0.5 * k * alpha_phi * t**2
            # ***********************

            # Clamp theta to physical range [0, pi]
            if theta < 0:
                theta = 0
            elif theta > np.pi: # Should not happen for k>=0 starting near pi
                 theta = np.pi

            # Derivatives needed for Normal Force calculation
            phi_dot = alpha_phi * t
            # Производная от новой формулы theta не изменилась
            theta_dot = -k * alpha_phi * t

            # Calculate Normal Force (N) required to maintain this kinematic path
            cos_theta = np.cos(theta)
            sin_theta = np.sin(theta)
            N = mass * ( self.g * cos_theta - self.radius * (theta_dot**2 + (sin_theta * phi_dot)**2) )

            # Check for detachment
            # Разрешаем N < 0 только на самом первом шаге i=0 (t=0), если смещение мало
            if N < 0 and i > 0:
                print(f"Detachment predicted at t={t:.3f} s (step {i}). Normal force became negative: N = {N:.3f}")
                if i < 5: # If detaches almost immediately despite offset
                     # You might want to keep the few points generated or return empty
                     # Keep points for now to see if it calculates *anything*
                     # return []
                     pass # Allow short trajectory display
                break # Stop calculating further points

            # Convert spherical coordinates (Physics: Z-up) to Cartesian (Physics: Z-up)
            x_phys = self.radius * sin_theta * np.cos(phi)
            y_phys = self.radius * sin_theta * np.sin(phi)
            z_phys = self.radius * cos_theta

            # Convert Cartesian (Physics: Z-up) to Cartesian (Animation: Y-up)
            anim_x = x_phys
            anim_y = z_phys
            anim_z = y_phys

            trajectory_points.append((anim_x, anim_y, anim_z))

            # Stop if we reached the North Pole
            if theta == 0 and i > 0:
                 print(f"Reached North Pole at t={t:.3f} s.")
                 break

        if not trajectory_points and sim_time > 0: # Check if list is empty after loop
             print("Warning: No trajectory points generated, likely immediate detachment despite offset.")
             return [] # Ensure empty list is returned if needed by GUI
        elif trajectory_points:
             print(f"Calculation finished. Generated {len(trajectory_points)} points.")

        return trajectory_points

# --- END OF FILE model.py ---