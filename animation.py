# --- START OF FILE animation.py ---

from PyQt5.QtWidgets import QOpenGLWidget
from PyQt5.QtGui import QVector3D, QMatrix4x4, QQuaternion
from PyQt5.QtCore import Qt, QPoint
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np

class SphereWidget(QOpenGLWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.rotation = QQuaternion()
        self.last_pos = QVector3D()
        self.rotation_speed = 1.0
        self.trajectory = []
        self.current_frame = 0
        self.sphere_radius = 1.0  # Начальное значение радиуса
        self.zoom = 1.0  # Коэффициент приближения камеры

    def set_sphere_radius(self, radius):
        self.sphere_radius = radius
        self.update()

    def set_trajectory(self, trajectory):
        self.trajectory = trajectory
        self.current_frame = 0
        self.update()

    def set_current_frame(self, frame):
        # Ограничиваем значение кадра допустимым диапазоном
        if self.trajectory:
            self.current_frame = max(0, min(frame, len(self.trajectory) - 1))
        else:
            self.current_frame = 0
        self.update()


    def initializeGL(self):
        glEnable(GL_DEPTH_TEST)
        glClearColor(0.1, 0.1, 0.1, 1.0)
        glEnable(GL_LINE_SMOOTH)
        glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
        # Включаем альфа-смешивание для прозрачности
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        # Динамическое позиционирование камеры с учетом зума
        camera_distance = self.sphere_radius * 3.5 * self.zoom
        gluLookAt(camera_distance, camera_distance, camera_distance,
                  0, 0, 0,
                  0, 1, 0) # Y - up

        rot_matrix = QMatrix4x4()
        rot_matrix.rotate(self.rotation)
        glMultMatrixf(rot_matrix.data())

        # --- Отрисовка Сферы ---
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        glColor4f(1.0, 1.0, 1.0, 0.4) # Белый, полупрозрачный
        glLineWidth(0.5)

        num_meridians = 32
        num_parallels = 32
        # Меридианы
        for j in range(num_meridians):
            phi = j * 2 * np.pi / num_meridians
            glBegin(GL_LINE_STRIP)
            for i in range(num_parallels + 1):
                theta = i * np.pi / num_parallels # От 0 (север) до pi (юг)
                # Конвертация из сферических (физика, Z-up) в декартовы (анимация, Y-up)
                x = self.sphere_radius * np.sin(theta) * np.cos(phi)
                z_phys = self.sphere_radius * np.cos(theta) # Z физический
                y_anim = z_phys # Y анимации
                z_anim = self.sphere_radius * np.sin(theta) * np.sin(phi) # Z анимации
                glVertex3f(x, y_anim, z_anim)
            glEnd()

        # Параллели
        for i in range(1, num_parallels):
            theta = i * np.pi / num_parallels
            glBegin(GL_LINE_LOOP)
            for j in range(num_meridians):
                phi = j * 2 * np.pi / num_meridians
                x = self.sphere_radius * np.sin(theta) * np.cos(phi)
                y_anim = self.sphere_radius * np.cos(theta)
                z_anim = self.sphere_radius * np.sin(theta) * np.sin(phi)
                glVertex3f(x, y_anim, z_anim)
            glEnd()

        # Экватор (theta = pi/2)
        glLineWidth(1.5)
        glColor4f(1.0, 0.0, 0.0, 0.8) # Красный
        glBegin(GL_LINE_LOOP)
        theta = np.pi / 2
        num_equator_points = 64
        for j in range(num_equator_points):
            phi = j * 2 * np.pi / num_equator_points
            x = self.sphere_radius * np.sin(theta) * np.cos(phi)
            y_anim = self.sphere_radius * np.cos(theta) # Должен быть 0
            z_anim = self.sphere_radius * np.sin(theta) * np.sin(phi)
            glVertex3f(x, y_anim, z_anim)
        glEnd()
        glLineWidth(1.0)

        # --- Стрелка силы тяжести (вниз по Y) ---
        arrow_length_gravity = self.sphere_radius * 0.3
        glColor4f(0.0, 1.0, 0.0, 0.8) # Зеленый

        # Начало стрелки может быть не на полюсе, а рядом с точкой для наглядности
        # Но пока оставим от полюса для простоты
        start_y = self.sphere_radius # Северный полюс Y
        end_y = start_y - arrow_length_gravity

        # Ствол
        glBegin(GL_LINES)
        glVertex3f(0, start_y, 0)
        glVertex3f(0, end_y, 0)
        glEnd()

        # Голова
        head_size_gravity = arrow_length_gravity * 0.2
        glBegin(GL_LINES)
        glVertex3f(0, end_y, 0)
        glVertex3f(-head_size_gravity, end_y + head_size_gravity, 0)
        glEnd()
        glBegin(GL_LINES)
        glVertex3f(0, end_y, 0)
        glVertex3f(head_size_gravity, end_y + head_size_gravity, 0)
        glEnd()

        # --- Отрисовка траектории и точки ---
        if self.trajectory:
            # Траектория (пройденный путь)
            glColor4f(1.0, 0.0, 0.0, 0.8) # Красный
            glBegin(GL_LINE_STRIP)
            for point in self.trajectory[:self.current_frame+1]:
                glVertex3f(*point)
            glEnd()

            # Сама точка (в текущем кадре)
            if self.current_frame < len(self.trajectory):
                current_pos = self.trajectory[self.current_frame]
                glPushMatrix()
                glTranslatef(*current_pos)
                quad = gluNewQuadric()
                # Возвращаем сплошной режим для точки
                glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
                glColor4f(1.0, 1.0, 0.0, 1.0) # Желтый, непрозрачный
                gluSphere(quad, self.sphere_radius * 0.05, 16, 16) # Размер точки зависит от радиуса
                gluDeleteQuadric(quad)
                glPopMatrix()

                # --- Отрисовка стрелки вектора скорости ---
                # Проверяем, есть ли следующий кадр для расчета направления
                if self.current_frame + 1 < len(self.trajectory):
                    next_pos = self.trajectory[self.current_frame + 1]

                    # Вектор направления скорости (не нормированный)
                    vel_dir = (next_pos[0] - current_pos[0],
                               next_pos[1] - current_pos[1],
                               next_pos[2] - current_pos[2])

                    # Нормализуем вектор
                    mag = np.linalg.norm(vel_dir)
                    if mag > 1e-6: # Избегаем деления на ноль, если точка стоит
                        norm_vel_dir = (vel_dir[0] / mag, vel_dir[1] / mag, vel_dir[2] / mag)

                        # Длина стрелки скорости
                        arrow_length_vel = self.sphere_radius * 0.2 # Можно сделать зависимой от mag

                        # Конечная точка стрелки
                        arrow_end = (current_pos[0] + norm_vel_dir[0] * arrow_length_vel,
                                     current_pos[1] + norm_vel_dir[1] * arrow_length_vel,
                                     current_pos[2] + norm_vel_dir[2] * arrow_length_vel)

                        # Рисуем ствол стрелки
                        glColor4f(0.0, 0.5, 1.0, 0.9) # Синий
                        glLineWidth(1.5)
                        glBegin(GL_LINES)
                        glVertex3f(*current_pos)
                        glVertex3f(*arrow_end)
                        glEnd()
                        glLineWidth(1.0) # Возвращаем толщину по умолчанию

                        # (Опционально) Можно добавить наконечник стрелки,
                        # но это сложнее, требует расчета перпендикулярных векторов.
                        # Пока оставим только ствол для простоты.

                # Возвращаем режим отрисовки линий для следующих элементов
                glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)


        glFlush()

    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        if h == 0: h = 1
        aspect_ratio = w / h
        gluPerspective(45, aspect_ratio, 0.1, 100.0 * self.sphere_radius) # Увеличиваем far clip

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # Нормализуем координаты мыши для корректного расчета вращения
            self.last_pos = QVector3D(event.x() / self.width(), event.y() / self.height(), 0)


    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            # Нормализуем координаты мыши
            new_pos = QVector3D(event.x() / self.width(), event.y() / self.height(), 0)
            diff = new_pos - self.last_pos
            self.last_pos = new_pos

            # Уменьшаем скорость вращения для более плавного управления
            rotation_scale = 180.0 # Градусы поворота на полное перемещение мыши по экрану
            rot_x = diff.y() * rotation_scale
            rot_y = diff.x() * rotation_scale

            # Применяем вращение: сначала вокруг Y (по горизонтали мыши), потом вокруг X (по вертикали мыши)
            # Нужно вращать вокруг осей объекта, а не мировых - используем кватернионы
            axis_x = QVector3D(1, 0, 0)
            axis_y = QVector3D(0, 1, 0)

            # Вращение вокруг оси Y, перпендикулярной экрану
            rotation_y_quat = QQuaternion.fromAxisAndAngle(axis_y, rot_y)
            # Вращение вокруг оси X, перпендикулярной экрану
            rotation_x_quat = QQuaternion.fromAxisAndAngle(axis_x, rot_x)

            # Комбинируем вращения: новое вращение применяется к текущему
            # Порядок важен! rot_y * rot_x * self.rotation вращает сначала вокруг X, потом Y в локальной системе
            self.rotation = rotation_y_quat * rotation_x_quat * self.rotation
            # Нормализуем кватернион для стабильности
            self.rotation.normalize()

            self.update()


    def wheelEvent(self, event):
        # Изменение зума при прокрутке колесика мыши
        delta = event.angleDelta().y()
        zoom_factor = 0.9 if delta > 0 else 1.1
        self.zoom *= zoom_factor
        # Ограничиваем зум, чтобы не улететь слишком далеко или близко
        self.zoom = max(0.1, min(self.zoom, 5.0))
        print(f"Zoom factor: {self.zoom:.2f}") # Отладочный вывод
        self.update()


# --- END OF FILE animation.py ---