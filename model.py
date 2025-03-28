# --- START OF FILE model.py ---

import numpy as np

class PhysicsModel:
    """
    Calculates the trajectory of a point mass moving on the inner surface
    of a sphere. The path follows a prescribed Archimedean-like spiral,
    and the simulation stops if the normal force becomes negative (detachment).
    Uses corrected Normal Force calculation.
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
                                  k=0 means purely horizontal motion at initial height.
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

        initial_theta_offset = 0.01 # Небольшой угол в радианах
        # Для k=0 - это будет угол, определяющий высоту горизонтального движения

        print(f"Starting calculation: R={self.radius}m, acc_param={acceleration}, k={k}, time={sim_time}s, mass={mass}kg")
        print(f"Derived alpha_phi = {alpha_phi:.4f} rad/s^2")
        print(f"Starting theta = {np.degrees(np.pi - initial_theta_offset):.3f} degrees (from Z-axis).")

        if k == 0:
            print("Warning: k=0 selected. Point will attempt purely horizontal motion.")

        for i in range(n_steps):
            t = i * dt

            # Kinematic path definition (Physics standard: Z-up, theta from Z-axis)
            phi = 0.5 * alpha_phi * t**2
            # Начальная высота задается смещением, k определяет изменение высоты
            theta = np.pi - initial_theta_offset - 0.5 * k * alpha_phi * t**2

            # Clamp theta to physical range [0, pi]
            if theta < 0:
                theta = 0
            elif theta > np.pi:
                 theta = np.pi # Should not happen now

            # Derivatives needed for Normal Force calculation
            phi_dot = alpha_phi * t
            theta_dot = -k * alpha_phi * t # Правильно равно 0 при k=0

            # Calculate Normal Force (N) required to maintain this kinematic path
            # Используем ИСПРАВЛЕННУЮ формулу
            cos_theta = np.cos(theta)
            sin_theta = np.sin(theta)
            term_gravity = -mass * self.g * cos_theta
            term_centripetal = -mass * self.radius * (theta_dot**2 + (sin_theta * phi_dot)**2)
            N = term_gravity + term_centripetal

            # Отладочный вывод сил для первых шагов
            if i < 5 or i % 100 == 0 : # Вывод чаще в начале и реже потом
                 print(f"t={t:.2f}s, theta={np.degrees(theta):.2f}deg, N={N:.3f} (Grav: {term_gravity:.3f}, Centr: {term_centripetal:.3f})")


            # Check for detachment (N < 0 means sphere needs to pull inwards)
            # N - это сила, которую сфера прикладывает наружу. Если она < 0, значит нужен "крюк".
            if N < 0:
                 # Разрешим очень маленькие отрицательные значения из-за погрешностей
                 tolerance = -1e-6
                 if N < tolerance:
                    print(f"Detachment predicted at t={t:.3f} s (step {i}). Normal force became negative: N = {N:.3f}")
                    # Возвращаем пустой список, только если отрыв происходит почти мгновенно
                    if i < 5 and len(trajectory_points) == 0:
                         print("Immediate detachment, returning empty trajectory.")
                         return []
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

        if not trajectory_points and sim_time > 0:
             print("Warning: No trajectory points generated.")
             return []
        elif trajectory_points:
             print(f"Calculation finished. Generated {len(trajectory_points)} points.")

        return trajectory_points

# --- END OF FILE model.py ---