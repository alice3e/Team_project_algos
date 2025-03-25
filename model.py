import numpy as np

class PhysicsModel:
    def __init__(self, sphere_radius=1.0):
        self.sphere_radius = sphere_radius
        self.g = 9.82
        self.trajectory = []
    
    def calculate_min_speed(self):
        return np.sqrt(self.g * self.sphere_radius)
    
    def calculate_trajectory(self, mass, velocity, simulation_time):
        """Расчет траектории с учетом времени симуляции"""
        v_min = self.calculate_min_speed()
        time_steps = int(simulation_time * 20)  # 20 кадров в секунду
        theta = np.linspace(0, simulation_time * 2 * np.pi, time_steps)
        
        if velocity >= v_min:
            # Движение по экватору
            self.trajectory = [
                (
                    self.sphere_radius * np.cos(t),
                    self.sphere_radius * np.sin(t),
                    0.0
                ) for t in theta
            ]
        else:
            # Спиральное падение
            self.trajectory = [
                (
                    (self.sphere_radius - 0.1 * t) * np.cos(t),
                    (self.sphere_radius - 0.1 * t) * np.sin(t),
                    -0.1 * t
                ) for t in theta
            ]
        return self.trajectory