# --- START OF FILE model.py ---

import numpy as np

class PhysicsModel:
    """
    Dynamic simulation with corrections for constraint, contact-dependent
    driving force, and proper handling of starting inside the sphere.
    """
    def __init__(self, radius):
        if radius <= 0: raise ValueError("Radius must be positive")
        self.radius = radius
        self.g = 9.81 # Acceleration due to gravity (m/s^2) Y-down in simulation coords

    def calculate_trajectory(self, initial_pos, initial_vel, drive_force_magnitude, sim_time, mass):
        """
        Calculates the trajectory using dynamic simulation.

        Handles starting inside the sphere by simulating free fall until contact.

        Args:
            initial_pos (tuple): Initial position (x, y, z) in Animation coords (Y-up).
            initial_vel (tuple): Initial velocity (vx, vy, vz) in Animation coords.
            drive_force_magnitude (float): Magnitude of the driving force applied tangentially.
            sim_time (float): Total simulation time (seconds).
            mass (float): Mass of the point (kg).

        Returns:
            tuple: (list_of_positions, list_of_velocities)
                   Each list contains tuples (x, y, z) or (vx, vy, vz).
                   Returns ([], []) if parameters are invalid.
        """
        if sim_time <= 0: return [], []
        if mass <= 0: return [], []
        if drive_force_magnitude < 0: drive_force_magnitude = 0

        # Simulation parameters
        dt = 0.005
        n_steps = int(sim_time / dt)
        restitution_coefficient = 0.3
        surface_tolerance = 1e-5 # Tolerance for checking surface contact/penetration

        # Initial state
        pos = np.array(initial_pos, dtype=float)
        vel = np.array(initial_vel, dtype=float)

        trajectory_points = [tuple(pos)]
        velocity_points = [tuple(vel)]

        print(f"Starting dynamic calculation: R={self.radius}m, F_drive={drive_force_magnitude}N, time={sim_time}s, mass={mass}kg")
        print(f"Initial pos: {pos}, Initial vel: {vel}")

        # --- Initial Contact Status Check ---
        dist_sq = np.dot(pos, pos)
        if dist_sq >= (self.radius - surface_tolerance)**2:
            contact = True
            print("Starting on or outside the surface.")
            # Project onto surface if starting slightly outside but within tolerance
            if dist_sq > self.radius**2 + surface_tolerance:
                 print(f"Error: Initial position {pos} is too far outside the sphere.")
                 return [],[] # Treat starting too far outside as an error
            elif dist_sq > self.radius**2:
                 pos *= self.radius / np.sqrt(dist_sq) # Project back if slightly out
                 trajectory_points[-1] = tuple(pos) # Update last (initial) point

            # Ensure initial velocity isn't pointing inward when starting on surface
            normal_vec = pos / self.radius
            vel_normal_comp = np.dot(vel, normal_vec)
            if vel_normal_comp < -1e-6: # If pointing inward
                 vel -= vel_normal_comp * normal_vec # Make it tangential
                 velocity_points[-1] = tuple(vel) # Update initial velocity
                 print("Adjusted initial velocity to be tangential.")

        else:
            contact = False
            print("Starting inside the sphere. Simulating free fall until contact.")
        # ---------------------------------

        for i in range(n_steps):
            # 1. Calculate Forces
            force_gravity = np.array([0.0, -mass * self.g, 0.0])
            force_drive = np.zeros(3)

            # --- Apply Drive Force ONLY if contact is true ---
            if contact and drive_force_magnitude > 0:
                pos_norm = np.linalg.norm(pos)
                if pos_norm > 1e-9: # Avoid division by zero at origin
                    radial_dir = pos / pos_norm
                    up_vector = np.array([0.0, 1.0, 0.0])
                    # Use cross product Z x R = horizontal approx. (if R is not along Z)
                    z_axis = np.array([0.0, 0.0, 1.0])
                    horizontal_dir_approx = np.cross(z_axis, radial_dir)
                    if np.linalg.norm(horizontal_dir_approx) < 1e-6: # Handle if R is along Z axis (poles)
                          # Try X x R
                          x_axis = np.array([1.0, 0.0, 0.0])
                          horizontal_dir_approx = np.cross(x_axis, radial_dir)
                          # If still zero (at origin?), default maybe?
                          if np.linalg.norm(horizontal_dir_approx) < 1e-9:
                              horizontal_dir_approx = np.array([0.0, 0.0, 1.0]) # Default to Z direction? Or based on Vel?

                    drive_dir = horizontal_dir_approx / (np.linalg.norm(horizontal_dir_approx) + 1e-9)
                    # Ensure drive force is tangential
                    drive_dir_tangent = drive_dir - np.dot(drive_dir, radial_dir) * radial_dir
                    if np.linalg.norm(drive_dir_tangent) > 1e-9:
                        drive_dir_tangent /= np.linalg.norm(drive_dir_tangent)
                        force_drive = drive_force_magnitude * drive_dir_tangent
            # ----------------------------------------------------

            # If not in contact, only gravity acts (plus air resistance if added later)
            force_net = force_gravity + force_drive if contact else force_gravity

            # 2. Calculate Acceleration
            acc = force_net / mass

            # 3. Integrate (Semi-implicit Euler)
            vel = vel + acc * dt
            pos = pos + vel * dt

            # 4. Constraint Check and Handling
            dist_sq_new = np.dot(pos, pos)
            radius_sq = self.radius**2

            # --- Check if contact state changes ---
            if not contact:
                # Was in free fall, check if contact is made
                if dist_sq_new >= (self.radius - surface_tolerance)**2:
                    # Contact established!
                    contact = True
                    print(f"--- Contact established at t={i*dt:.3f} ---")

                    # Apply contact constraints immediately for this step
                    dist_new = np.sqrt(dist_sq_new)
                    normal_vec = pos / dist_new if dist_new > 1e-9 else np.array([0,1,0])

                    # Correct Position: Project onto surface
                    pos = normal_vec * self.radius

                    # Correct Velocity: Reflect normal component from the impact
                    vel_normal_comp = np.dot(vel, normal_vec)
                    if vel_normal_comp < -1e-6: # Was moving into the wall
                        vel = vel - (1 + restitution_coefficient) * vel_normal_comp * normal_vec
                    # If somehow hit exactly tangentially or moving out (unlikely), just keep vel
                # else: still in free fall, no changes needed to pos/vel

            else: # Was in contact, check if detachment occurs or penetration needs fixing
                if dist_sq_new < radius_sq - surface_tolerance:
                    # Penetration occurred while in contact state
                    #print(f"Penetration at t={i*dt:.3f}")
                    dist_new = np.sqrt(dist_sq_new)
                    normal_vec = pos / dist_new if dist_new > 1e-9 else np.array([0,1,0])
                    pos = normal_vec * self.radius # Project back
                    vel_normal_comp = np.dot(vel, normal_vec)
                    if vel_normal_comp < -1e-6:
                        vel = vel - (1 + restitution_coefficient) * vel_normal_comp * normal_vec
                    # Stay in contact = True

                else: # On or outside the sphere while contact=True
                    dist_new = np.sqrt(dist_sq_new)
                    normal_vec = pos / dist_new if dist_new > 1e-9 else np.array([0,1,0])
                    radial_vel_comp = np.dot(vel, normal_vec)

                    # Estimate required Normal force
                    pos_on_surface = normal_vec * self.radius
                    vel_sq_est = np.dot(vel, vel)
                    n_y_est = pos_on_surface[1] / self.radius if self.radius > 0 else 0
                    required_N = -mass * (vel_sq_est / self.radius if self.radius > 0 else 0) - mass * self.g * n_y_est

                    min_inward_vel_for_contact = -0.01 # Threshold

                    if required_N >= -1e-6 or radial_vel_comp < min_inward_vel_for_contact:
                        # Maintain contact
                        contact = True
                        # Correct Position if we exited slightly
                        if dist_sq_new > radius_sq + surface_tolerance:
                            pos = normal_vec * self.radius # Project back
                        # Correct Velocity ONLY if moving outwards
                        vel_normal_comp_after_proj = np.dot(vel, normal_vec)
                        if vel_normal_comp_after_proj > 1e-6:
                            vel = vel - vel_normal_comp_after_proj * normal_vec # Make tangential
                    else:
                        # Detachment condition met
                        if contact: # Print only on the transition
                            print(f"--- Detachment detected at t={i*dt:.3f} --- Est.N={required_N:.3f}, rad_vel={radial_vel_comp:.3f}")
                        contact = False
                        # No correction needed for pos or vel, let it fly

            # Store the validated/corrected state for this step
            trajectory_points.append(tuple(pos))
            velocity_points.append(tuple(vel))

        print(f"Dynamic calculation finished. Generated {len(trajectory_points)} points.")
        return trajectory_points, velocity_points

# --- END OF FILE model.py ---