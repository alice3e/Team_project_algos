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
        self.current_frame = min(frame, len(self.trajectory)-1)
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
                  0, 1, 0)
        
        rot_matrix = QMatrix4x4()
        rot_matrix.rotate(self.rotation)
        glMultMatrixf(rot_matrix.data())
        
        # Устанавливаем режим отрисовки линий и прозрачность
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        # Устанавливаем белый цвет с прозрачностью (альфа = 0.4)
        glColor4f(1.0, 1.0, 1.0, 0.4)

        # Рисуем меридианы (линии, проходящие от одного полюса к другому)
        num_meridians = 32
        num_parallels = 32
        glLineWidth(0.5)
        for j in range(num_meridians):
            phi = j * 2 * np.pi / num_meridians
            glBegin(GL_LINE_STRIP)
            for i in range(num_parallels + 1):
                theta = i * np.pi / num_parallels
                x = self.sphere_radius * np.sin(theta) * np.cos(phi)
                y = self.sphere_radius * np.cos(theta)
                z = self.sphere_radius * np.sin(theta) * np.sin(phi)
                glVertex3f(x, y, z)
            glEnd()

        # Рисуем параллели (окружности с постоянным θ)
        for i in range(1, num_parallels):
            theta = i * np.pi / num_parallels
            glBegin(GL_LINE_LOOP)
            for j in range(num_meridians):
                phi = j * 2 * np.pi / num_meridians
                x = self.sphere_radius * np.sin(theta) * np.cos(phi)
                y = self.sphere_radius * np.cos(theta)
                z = self.sphere_radius * np.sin(theta) * np.sin(phi)
                glVertex3f(x, y, z)
            glEnd()

        # Рисуем экватор (θ = π/2) более толстой красной линией
        glLineWidth(1.5)
        glColor4f(1.0, 0.0, 0.0, 0.8)
        glBegin(GL_LINE_LOOP)
        theta = np.pi / 2
        num_equator_points = 64
        for j in range(num_equator_points):
            phi = j * 2 * np.pi / num_equator_points
            x = self.sphere_radius * np.sin(theta) * np.cos(phi)
            y = self.sphere_radius * np.cos(theta)
            z = self.sphere_radius * np.sin(theta) * np.sin(phi)
            glVertex3f(x, y, z)
        glEnd()
        glLineWidth(1.0)
        
        # Отрисовка стрелки, указывающей на направление силы тяжести.
        # Северный полюс сферы имеет координаты (0, sphere_radius, 0)
        # Стрелка направлена вниз по оси Y.
        arrow_length = self.sphere_radius * 0.3
        glColor4f(0.0, 1.0, 0.0, 0.8)
        
        # Ствол стрелки
        glBegin(GL_LINES)
        glVertex3f(0, self.sphere_radius, 0)
        glVertex3f(0, self.sphere_radius - arrow_length, 0)
        glEnd()
        
        # Голова стрелки (две линии, имитирующие наконечник)
        head_size = arrow_length * 0.2
        glBegin(GL_LINES)
        glVertex3f(0, self.sphere_radius - arrow_length, 0)
        glVertex3f(-head_size, self.sphere_radius - arrow_length + head_size, 0)
        glEnd()
        glBegin(GL_LINES)
        glVertex3f(0, self.sphere_radius - arrow_length, 0)
        glVertex3f(head_size, self.sphere_radius - arrow_length + head_size, 0)
        glEnd()

        # Отрисовка траектории материальной точки
        if self.trajectory:
            glColor4f(1.0, 0.0, 0.0, 0.8)
            glBegin(GL_LINE_STRIP)
            for point in self.trajectory[:self.current_frame+1]:
                glVertex3f(*point)
            glEnd()
            
            # Отрисовка самой точки
            if self.current_frame < len(self.trajectory):
                glPushMatrix()
                glTranslatef(*self.trajectory[self.current_frame])
                quad = gluNewQuadric()
                gluSphere(quad, 0.05, 16, 16)
                gluDeleteQuadric(quad)
                glPopMatrix()

        glFlush()
        
    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, w/h, 0.1, 100.0)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.last_pos = QVector3D(event.x(), event.y(), 0)

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            new_pos = QVector3D(event.x(), event.y(), 0)
            diff = new_pos - self.last_pos
            self.last_pos = new_pos
            
            rot_x = diff.y() * self.rotation_speed
            rot_y = diff.x() * self.rotation_speed
            self.rotation = QQuaternion.fromEulerAngles(rot_x, rot_y, 0) * self.rotation
            self.update()

    def wheelEvent(self, event):
        # Изменение зума при прокрутке колесика мыши
        delta = event.angleDelta().y()
        # Корректируем коэффициент зума: при положительном значении - приближение, отрицательном - отдаление
        if delta > 0:
            self.zoom *= 0.9
        else:
            self.zoom *= 1.1
        self.update()
