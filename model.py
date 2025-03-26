import math

class PhysicsModel:
    def __init__(self, radius):
        self.radius = radius

    def calculate_trajectory(self, acceleration, angle_deg, sim_time, mass):
        """
        Вычисляет траекторию материальной точки, движущейся по спирали вдоль поверхности сферы.

        Параметры:
            acceleration - ускорение точки (м/с^2). Предполагается, что точка начинает с нулевой скорости.
            angle_deg - параметр, определяющий «размазанность» спирали (в градусах). 
                        Если равен 0, движение происходит по меридиану, при увеличении – спираль становится более заметной.
            sim_time - время симуляции (секунды).
            mass - масса точки (кг).

        Возвращает:
            Список точек (x, y, z), описывающих траекторию движения.
        """
        dt = 0.05  # шаг по времени в секундах
        num_steps = int(sim_time / dt) + 1
        trajectory = []

        # Определяем максимальную пройденную дугу, чтобы не выйти за пределы экватора.
        # Дистанция от южного полюса (θ = π) до экватора (θ = π/2): s_max = R * (π/2)
        max_s = self.radius * (math.pi / 2)

        # Пройденную дугу s вычисляем по формуле равномерного ускорения (начиная с нуля): s = 0.5 * a * t^2
        for i in range(num_steps):
            t = i * dt
            s = 0.5 * acceleration * t**2
            # Ограничим s, чтобы точка не «залезла» за экватор
            if s > max_s:
                s = max_s

            # Определяем угол θ: от южного полюса (θ=π) до экватора (θ=π/2)
            theta = math.pi - (s / self.radius)

            # Определяем угол φ, который задаёт спиральность.
            # Преобразуем заданный угол из градусов в радианы.
            spiral_factor = math.radians(angle_deg)
            # φ пропорционально пройденной дуге s.
            phi = spiral_factor * (s / self.radius)

            # Преобразование из сферических координат в декартовы:
            x = self.radius * math.sin(theta) * math.cos(phi)
            y = self.radius * math.cos(theta)
            z = self.radius * math.sin(theta) * math.sin(phi)

            trajectory.append((x, y, z))
        return trajectory
