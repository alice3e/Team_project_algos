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
        self.sphere_radius = 1.0
        self.zoom = 1.0

    def set_force_direction(self, force_vec):
        self.force_direction = force_vec

    def set_sphere_radius(self, radius):
        self.sphere_radius = radius
        self.update()

    def set_trajectory(self, trajectory):
        self.trajectory = trajectory
        self.current_frame = 0
        self.update()

    def set_current_frame(self, frame):
        if self.trajectory:
            self.current_frame = max(0, min(frame, len(self.trajectory) - 1))
        else:
            self.current_frame = 0
        self.update()

    def initializeGL(self):
        glEnable(GL_DEPTH_TEST)
        glClearColor(1.0, 1.0, 1.0, 1.0)
        glEnable(GL_LINE_SMOOTH)
        glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        camera_distance = self.sphere_radius * 3.5 * self.zoom
        gluLookAt(camera_distance, camera_distance, camera_distance,
                  0, 0, 0,
                  0, 1, 0)

        rot_matrix = QMatrix4x4()
        rot_matrix.rotate(self.rotation)
        glMultMatrixf(rot_matrix.data())

        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        glColor4f(0.0, 0.6, 1.0, 1.0)
        glLineWidth(1.2)

        num_meridians = 32
        num_parallels = 32
        for j in range(num_meridians):
            phi = j * 2 * np.pi / num_meridians
            glBegin(GL_LINE_STRIP)
            for i in range(num_parallels + 1):
                theta = i * np.pi / num_parallels
                x = self.sphere_radius * np.sin(theta) * np.cos(phi)
                z_phys = self.sphere_radius * np.cos(theta)
                y_anim = z_phys
                z_anim = self.sphere_radius * np.sin(theta) * np.sin(phi)
                glVertex3f(x, y_anim, z_anim)
            glEnd()

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

        glLineWidth(1.8)
        glColor4f(1.0, 0.2, 0.2, 1.0)
        glBegin(GL_LINE_LOOP)
        theta = np.pi / 2
        num_equator_points = 64
        for j in range(num_equator_points):
            phi = j * 2 * np.pi / num_equator_points
            x = self.sphere_radius * np.sin(theta) * np.cos(phi)
            y_anim = self.sphere_radius * np.cos(theta)
            z_anim = self.sphere_radius * np.sin(theta) * np.sin(phi)
            glVertex3f(x, y_anim, z_anim)
        glEnd()
        glLineWidth(1.0)

        arrow_length_gravity = self.sphere_radius * 0.3
        glColor4f(0.0, 0.8, 0.0, 1.0)
        start_y = self.sphere_radius
        end_y = start_y - arrow_length_gravity

        glLineWidth(5.0)
        glBegin(GL_LINES)
        glVertex3f(0, start_y, 0)
        glVertex3f(0, end_y, 0)
        glEnd()

        head_size_gravity = arrow_length_gravity * 0.2
        glBegin(GL_LINES)
        glVertex3f(0, end_y, 0)
        glVertex3f(-head_size_gravity, end_y + head_size_gravity, 0)
        glEnd()
        glBegin(GL_LINES)
        glVertex3f(0, end_y, 0)
        glVertex3f(head_size_gravity, end_y + head_size_gravity, 0)
        glEnd()
        glLineWidth(1.0)

        if self.trajectory:
            glColor4f(1.0, 0.0, 0.0, 1.0)
            glLineWidth(5.0)
            glBegin(GL_LINE_STRIP)
            for point in self.trajectory[:self.current_frame+1]:
                glVertex3f(*point)
            glEnd()

            if self.current_frame < len(self.trajectory):
                current_pos = self.trajectory[self.current_frame]
                glPushMatrix()
                glTranslatef(*current_pos)
                quad = gluNewQuadric()
                glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
                glColor4f(0.9, 0.7, 0.0, 1.0)
                gluSphere(quad, self.sphere_radius * 0.05, 16, 16)
                gluDeleteQuadric(quad)
                glPopMatrix()

                if self.current_frame + 1 < len(self.trajectory):
                    next_pos = self.trajectory[self.current_frame + 1]
                    vel_dir = (next_pos[0] - current_pos[0],
                               next_pos[1] - current_pos[1],
                               next_pos[2] - current_pos[2])
                    mag = np.linalg.norm(vel_dir)
                    if mag > 1e-6:
                        norm_vel_dir = (vel_dir[0] / mag, vel_dir[1] / mag, vel_dir[2] / mag)
                        arrow_length_vel = self.sphere_radius * 0.2
                        arrow_end = (current_pos[0] + norm_vel_dir[0] * arrow_length_vel,
                                     current_pos[1] + norm_vel_dir[1] * arrow_length_vel,
                                     current_pos[2] + norm_vel_dir[2] * arrow_length_vel)
                        glColor4f(0.0, 0.6, 1.0, 1.0)
                        glLineWidth(5.0)
                        glBegin(GL_LINES)
                        glVertex3f(*current_pos)
                        glVertex3f(*arrow_end)
                        glEnd()
                        glLineWidth(1.0)
                glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

            if hasattr(self, 'force_direction') and self.force_direction is not None:
                force_dir = np.array(self.force_direction)
                force_mag = np.linalg.norm(force_dir)
                if force_mag > 1e-6:
                    force_dir /= force_mag
                    glColor4f(1.0, 0.5, 0.0, 1.0)
                    glLineWidth(2.0)
                    glBegin(GL_LINES)
                    glVertex3f(*current_pos)
                    glVertex3f(current_pos[0] + force_dir[0] * 0.5,
                               current_pos[1] + force_dir[1] * 0.5,
                               current_pos[2] + force_dir[2] * 0.5)
                    glEnd()

            if self.trajectory and self.current_frame < len(self.trajectory):
                pos = self.trajectory[self.current_frame]
                glColor3f(0.0, 0.8, 0.0)
                glBegin(GL_LINES)
                glVertex3f(*pos)
                glVertex3f(pos[0], pos[1] - 0.5, pos[2])
                glEnd()

        glFlush()

    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        if h == 0: h = 1
        aspect_ratio = w / h
        gluPerspective(45, aspect_ratio, 0.1, 100.0 * self.sphere_radius)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.last_pos = QVector3D(event.x() / self.width(), event.y() / self.height(), 0)

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            new_pos = QVector3D(event.x() / self.width(), event.y() / self.height(), 0)
            diff = new_pos - self.last_pos
            self.last_pos = new_pos
            rotation_scale = 180.0
            rot_x = diff.y() * rotation_scale
            rot_y = diff.x() * rotation_scale
            axis_x = QVector3D(1, 0, 0)
            axis_y = QVector3D(0, 1, 0)
            rotation_y_quat = QQuaternion.fromAxisAndAngle(axis_y, rot_y)
            rotation_x_quat = QQuaternion.fromAxisAndAngle(axis_x, rot_x)
            self.rotation = rotation_y_quat * rotation_x_quat * self.rotation
            self.rotation.normalize()
            self.update()

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        zoom_factor = 0.9 if delta > 0 else 1.1
        self.zoom *= zoom_factor
        self.zoom = max(0.1, min(self.zoom, 5.0))
        print(f"Zoom factor: {self.zoom:.2f}")
        self.update()
