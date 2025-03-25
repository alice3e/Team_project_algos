from PyQt5.QtWidgets import QOpenGLWidget
from PyQt5.QtGui import QVector3D, QMatrix4x4, QQuaternion
from PyQt5.QtCore import Qt, QPoint
from OpenGL.GL import *
from OpenGL.GLU import *
import math

class SphereWidget(QOpenGLWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.rotation = QQuaternion()
        self.last_pos = QVector3D()
        self.radius = 1.0
        self.segments = 32
        self.rotation_speed = 0.7

    def set_sphere_parameters(self, radius, segments):
        self.radius = radius
        self.segments = segments
        self.update()

    def initializeGL(self):
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glClearColor(0.1, 0.1, 0.1, 1.0)
        glEnable(GL_LINE_SMOOTH)
        glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        # Настройка камеры
        gluLookAt(3, 3, 3, 0, 0, 0, 0, 1, 0)
        
        # Применение вращения
        rot_matrix = QMatrix4x4()
        rot_matrix.rotate(self.rotation)
        glMultMatrixf(rot_matrix.data())
        
        # Отрисовка wireframe сферы
        glColor4f(0.0, 0.5, 1.0, 0.5)  # Прозрачный голубой цвет
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        quadric = gluNewQuadric()
        gluQuadricDrawStyle(quadric, GLU_LINE)
        gluSphere(quadric, self.radius, self.segments, self.segments)
        gluDeleteQuadric(quadric)

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

            # Рассчитываем углы вращения
            rot_x = diff.y() * self.rotation_speed
            rot_y = diff.x() * self.rotation_speed
            
            # Создаем кватернионы вращения
            euler_rot = QQuaternion.fromEulerAngles(rot_x, rot_y, 0)
            self.rotation = euler_rot * self.rotation
            self.update()