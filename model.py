import numpy as np

class PhysicsModel:
    def __init__(self, radius):
        if radius <= 0: raise ValueError("Radius must be positive")
        self.radius = radius
        self.g = 9.81

    def calculate_trajectory(self, initial_pos, initial_vel, drive_force_magnitude, sim_time, mass):
        if sim_time <= 0: return [], []
        if mass <= 0: return [], []
        if drive_force_magnitude < 0: drive_force_magnitude = 0

        dt = 0.005
        n_steps = int(sim_time / dt)
        restitution_coefficient = 0.3
        surface_tolerance = 1e-5

        pos = np.array(initial_pos, dtype=float)
        vel = np.array(initial_vel, dtype=float)

        trajectory_points = [tuple(pos)]
        velocity_points = [tuple(vel)]

        print(f"Starting dynamic calculation: R={self.radius}m, F_drive={drive_force_magnitude}N, time={sim_time}s, mass={mass}kg")
        print(f"Initial pos: {pos}, Initial vel: {vel}")

        dist_sq = np.dot(pos, pos)
        if dist_sq >= (self.radius - surface_tolerance)**2:
            contact = True
            print("Starting on or outside the surface.")
            if dist_sq > self.radius**2 + surface_tolerance:
                 print(f"Error: Initial position {pos} is too far outside the sphere.")
                 return [],[]
            elif dist_sq > self.radius**2:
                 pos *= self.radius / np.sqrt(dist_sq)
                 trajectory_points[-1] = tuple(pos)

            normal_vec = pos / self.radius
            vel_normal_comp = np.dot(vel, normal_vec)
            if vel_normal_comp < -1e-6:
                 vel -= vel_normal_comp * normal_vec
                 velocity_points[-1] = tuple(vel)
                 print("Adjusted initial velocity to be tangential.")

        else:
            contact = False
            print("Starting inside the sphere. Simulating free fall until contact.")

        for i in range(n_steps):
            force_gravity = np.array([0.0, -mass * self.g, 0.0])
            force_drive = np.zeros(3)

            if contact and drive_force_magnitude > 0:
                radial_dir = pos / (np.linalg.norm(pos) + 1e-9)
                tangent_dir = np.array([
                    -radial_dir[2],
                    0,
                    radial_dir[0]
                ])
                tangent_norm = np.linalg.norm(tangent_dir)
                if tangent_norm > 1e-6:
                    tangent_dir /= tangent_norm
                    force_drive = drive_force_magnitude * tangent_dir
                else:
                    force_drive = np.array([drive_force_magnitude, 0, 0])
            else:
                force_drive = np.zeros(3)

            force_net = force_gravity + force_drive if contact else force_gravity

            if contact:
                speed_sq = np.dot(vel, vel)
                radial_dir = pos / (np.linalg.norm(pos) + 1e-9)
                F_centrifugal = mass * speed_sq / self.radius
                F_gravity_normal = mass * self.g * abs(radial_dir[1])

                if F_centrifugal >= F_gravity_normal * 1.05:
                    contact = False
                    print(f"Отрыв при v={np.sqrt(speed_sq):.2f} м/с (требуется {np.sqrt(self.g * self.radius * abs(radial_dir[1])):.2f} м/с)")

            acc = force_net / mass

            vel = vel + acc * dt
            pos = pos + vel * dt

            dist = np.linalg.norm(pos)
            if dist > 1e-6:
                pos = pos * (self.radius / dist)
                radial_vel = np.dot(vel, pos/dist)
                vel = vel - radial_vel * (pos/dist)

            dist_sq_new = np.dot(pos, pos)
            radius_sq = self.radius**2

            if not contact:
                if dist_sq_new >= (self.radius - surface_tolerance)**2:
                    contact = True
                    print(f"--- Contact established at t={i*dt:.3f} ---")

                    dist_new = np.sqrt(dist_sq_new)
                    normal_vec = pos / dist_new if dist_new > 1e-9 else np.array([0,1,0])

                    pos = normal_vec * self.radius

                    vel_normal_comp = np.dot(vel, normal_vec)
                    if vel_normal_comp < -1e-6:
                        vel = vel - (1 + restitution_coefficient) * vel_normal_comp * normal_vec

            else:
                if dist_sq_new < radius_sq - surface_tolerance:
                    dist_new = np.sqrt(dist_sq_new)
                    normal_vec = pos / dist_new if dist_new > 1e-9 else np.array([0,1,0])
                    pos = normal_vec * self.radius
                    vel_normal_comp = np.dot(vel, normal_vec)
                    if vel_normal_comp < -1e-6:
                        vel = vel - (1 + restitution_coefficient) * vel_normal_comp * normal_vec

                else:
                    dist_new = np.sqrt(dist_sq_new)
                    normal_vec = pos / dist_new if dist_new > 1e-9 else np.array([0,1,0])
                    radial_vel_comp = np.dot(vel, normal_vec)

                    pos_on_surface = normal_vec * self.radius
                    vel_sq_est = np.dot(vel, vel)
                    n_y_est = pos_on_surface[1] / self.radius if self.radius > 0 else 0
                    required_N = -mass * (vel_sq_est / self.radius if self.radius > 0 else 0) - mass * self.g * n_y_est

                    min_inward_vel_for_contact = -0.01

                    if required_N >= -1e-6 or radial_vel_comp < min_inward_vel_for_contact:
                        contact = True
                        if dist_sq_new > radius_sq + surface_tolerance:
                            pos = normal_vec * self.radius
                        vel_normal_comp_after_proj = np.dot(vel, normal_vec)
                        if vel_normal_comp_after_proj > 1e-6:
                            vel = vel - vel_normal_comp_after_proj * normal_vec
                    else:
                        if contact:
                            print(f"--- Detachment detected at t={i*dt:.3f} --- Est.N={required_N:.3f}, rad_vel={radial_vel_comp:.3f}")
                        contact = False

            trajectory_points.append(tuple(pos))

            if hasattr(self, 'visualization'):
                self.visualization.set_force_direction(force_drive)

            velocity_points.append(tuple(vel))

        print(f"Dynamic calculation finished. Generated {len(trajectory_points)} points.")
        return trajectory_points, velocity_points
