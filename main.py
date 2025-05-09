import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                            QPushButton, QFormLayout, QLineEdit, QLabel,
                            QSlider, QHBoxLayout, QMessageBox, QGroupBox)
from PyQt5.QtCore import Qt
from animation import SphereWidget
from model import PhysicsModel
import numpy as np

class AlgorithmWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sphere Motion Simulator (Dynamic Model)")

        self.physics_model = None
        self.trajectory = []


        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)

        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        self.visualization = SphereWidget()
        left_layout.addWidget(self.visualization, stretch=1)
        self.timeline = QSlider(Qt.Horizontal)
        self.timeline.setRange(0, 100)
        self.timeline.setValue(0)
        self.timeline.valueChanged.connect(self.update_frame)
        left_layout.addWidget(self.timeline)
        main_layout.addWidget(left_widget, stretch=3)

        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        params_group = QGroupBox("Параметры симуляции")
        params_layout = QFormLayout()
        self.radius_input = QLineEdit("4.0")
        params_layout.addRow(QLabel("Радиус сферы (м):"), self.radius_input)
        self.mass_input = QLineEdit("100.0")
        params_layout.addRow(QLabel("Масса точки (кг):"), self.mass_input)
        self.drive_force_input = QLineEdit("15.0")
        params_layout.addRow(QLabel("Сила тяги (Н):"), self.drive_force_input)
        self.time_input = QLineEdit("15.0")
        params_layout.addRow(QLabel("Время симуляции (сек):"), self.time_input)
        params_group.setLayout(params_layout)
        right_layout.addWidget(params_group)

        initial_conditions_group = QGroupBox("Начальные условия")
        initial_conditions_layout = QFormLayout()
        init_pos_group = QGroupBox("Позиция (x, y, z)")
        init_pos_layout = QHBoxLayout()
        self.initial_pos_x_input = QLineEdit("0.1")
        self.initial_pos_y_input = QLineEdit("-3.95")
        self.initial_pos_z_input = QLineEdit("0.0")
        init_pos_layout.addWidget(QLabel("X:"))
        init_pos_layout.addWidget(self.initial_pos_x_input)
        init_pos_layout.addWidget(QLabel("Y:"))
        init_pos_layout.addWidget(self.initial_pos_y_input)
        init_pos_layout.addWidget(QLabel("Z:"))
        init_pos_layout.addWidget(self.initial_pos_z_input)
        init_pos_group.setLayout(init_pos_layout)
        initial_conditions_layout.addRow(init_pos_group)
        init_vel_group = QGroupBox("Скорость (vx, vy, vz)")
        init_vel_layout = QHBoxLayout()
        self.initial_vel_x_input = QLineEdit("0.0")
        self.initial_vel_y_input = QLineEdit("0.0")
        self.initial_vel_z_input = QLineEdit("2.0")
        init_vel_layout.addWidget(QLabel("Vx:"))
        init_vel_layout.addWidget(self.initial_vel_x_input)
        init_vel_layout.addWidget(QLabel("Vy:"))
        init_vel_layout.addWidget(self.initial_vel_y_input)
        init_vel_layout.addWidget(QLabel("Vz:"))
        init_vel_layout.addWidget(self.initial_vel_z_input)
        init_vel_group.setLayout(init_vel_layout)
        initial_conditions_layout.addRow(init_vel_group)
        initial_conditions_group.setLayout(initial_conditions_layout)
        right_layout.addWidget(initial_conditions_group)

        info_group = QGroupBox("Информация о точке (текущий кадр)")
        info_layout = QFormLayout()
        self.info_time_label = QLabel("Время: -")
        self.info_pos_label = QLabel("Позиция (x,y,z): -")
        self.info_vel_label = QLabel("Скорость (vx,vy,vz): -")
        self.info_speed_label = QLabel("Скорость (скаляр): -")
        self.info_critical_label = QLabel("Критическая скорость: -")
        info_layout.addRow(self.info_critical_label)
        info_layout.addRow(self.info_time_label)
        info_layout.addRow(self.info_pos_label)
        info_layout.addRow(self.info_vel_label)
        info_layout.addRow(self.info_speed_label)
        info_group.setLayout(info_layout)
        right_layout.addWidget(info_group)

        self.calculate_btn = QPushButton("Рассчитать траекторию")
        self.calculate_btn.clicked.connect(self.calculate)
        right_layout.addWidget(self.calculate_btn)

        right_layout.addStretch(1)
        right_widget.setLayout(right_layout)
        main_layout.addWidget(right_widget, stretch=1)

        self.radius_input.textChanged.connect(self.update_default_y)
        self.update_default_y(self.radius_input.text())

    def update_default_y(self, radius_text):
        try:
            radius = float(radius_text)
            if radius > 0:
                default_y = -radius + 0.05
                current_y_text = self.initial_pos_y_input.text()
                try:
                    # Check if the current value is likely the old default based on the *current* sphere radius in visualization
                    # This check is complex and might not be perfectly accurate if visualization radius isn't set yet
                    is_old_default = False
                    if hasattr(self.visualization, 'sphere_radius') and self.visualization.sphere_radius is not None:
                         is_old_default = abs(float(current_y_text) - (-self.visualization.sphere_radius + 0.05)) < 1e-3

                    # If it's the old default or the field is empty, update it
                    if is_old_default or not current_y_text:
                        self.initial_pos_y_input.setText(f"{default_y:.2f}")
                except ValueError:
                     # Handle case where current text is not a float, update it
                    self.initial_pos_y_input.setText(f"{default_y:.2f}")
                except AttributeError:
                     # Handle case where visualization.sphere_radius doesn't exist yet
                     if not current_y_text: # Only update if empty
                         self.initial_pos_y_input.setText(f"{default_y:.2f}")

        except ValueError:
            pass # Ignore if radius_text is not a valid float

    def calculate(self):
        try:
            radius = float(self.radius_input.text())
            mass = float(self.mass_input.text())
            drive_force = float(self.drive_force_input.text())
            sim_time = float(self.time_input.text())
            initial_pos = (
                float(self.initial_pos_x_input.text()),
                float(self.initial_pos_y_input.text()),
                float(self.initial_pos_z_input.text())
            )
            initial_vel = (
                float(self.initial_vel_x_input.text()),
                float(self.initial_vel_y_input.text()),
                float(self.initial_vel_z_input.text())
            )

            if radius <= 0 or mass <= 0 or sim_time <= 0:
                raise ValueError("Радиус, масса и время > 0.")
            if drive_force < 0:
                drive_force = 0
                self.drive_force_input.setText("0.0")
            pos_norm_sq = sum(p ** 2 for p in initial_pos)
            if pos_norm_sq > radius ** 2 + 1e-3:
                raise ValueError("Начальная позиция вне сферы.")

            critical_speed = np.sqrt(9.81 * radius)
            self.info_critical_label.setText(f"Критическая скорость: {critical_speed:.2f} м/с")

            self.physics_model = PhysicsModel(radius)
            self.visualization.set_sphere_radius(radius)

            results = self.physics_model.calculate_trajectory(
                initial_pos, initial_vel, drive_force, sim_time, mass
            )
            if not isinstance(results, tuple) or len(results) != 2:
                print("Warning: Model did not return expected (positions, velocities) tuple.")
                if isinstance(results, list):
                    self.trajectory = results
                    self.velocities = []
                else:
                    raise ValueError("Model returned unexpected data format.")
            else:
                self.trajectory, self.velocities = results

            if not self.trajectory:
                QMessageBox.warning(self, "Предупреждение", "Не удалось сгенерировать траекторию.")
                self.timeline.setRange(0, 0)
                self.timeline.setValue(0)
                self.visualization.set_trajectory([])
                self.velocities = []
                self.clear_info_labels()
                return

            print(f"Generated {len(self.trajectory)} trajectory points.")
            self.visualization.set_trajectory(self.trajectory)
            if len(self.trajectory) > 1:
                self.timeline.setRange(0, len(self.trajectory) - 1)
                self.timeline.setValue(0)
                self.update_frame(0)
            else:
                self.timeline.setRange(0, 0)
                self.timeline.setValue(0)
                self.update_frame(0)

        except ValueError as e:
            QMessageBox.critical(self, "Ошибка ввода", str(e))
            self.clear_info_labels()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка расчета", f"Произошла ошибка во время расчета:\n{e}")
            self.clear_info_labels()

    def update_frame(self, value):
        if self.trajectory:
            max_frame = self.timeline.maximum()
            frame_index = max(0, min(value, max_frame))

            self.visualization.set_current_frame(frame_index)

            pos = self.trajectory[frame_index]
            time_step = 0.005
            current_time = frame_index * time_step

            self.info_time_label.setText(f"Время: {current_time:.3f} сек")
            self.info_pos_label.setText(f"Позиция (x,y,z): ({pos[0]:.3f}, {pos[1]:.3f}, {pos[2]:.3f})")

            if self.velocities and frame_index < len(self.velocities):
                vel = self.velocities[frame_index]
                speed = np.linalg.norm(vel)
                self.info_vel_label.setText(f"Скорость (vx,vy,vz): ({vel[0]:.3f}, {vel[1]:.3f}, {vel[2]:.3f})")
                self.info_speed_label.setText(f"Скорость (скаляр): {speed:.3f} м/с")
            else:
                self.info_vel_label.setText("Скорость (vx,vy,vz): -")
                self.info_speed_label.setText("Скорость (скаляр): -")
        else:
            self.clear_info_labels()

    def clear_info_labels(self):
        self.info_time_label.setText("Время: -")
        self.info_pos_label.setText("Позиция (x,y,z): -")
        self.info_vel_label.setText("Скорость (vx,vy,vz): -")
        self.info_speed_label.setText("Скорость (скаляр): -")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet("""
        QWidget {
            background-color: #FFFFFF;
            color: #000000;
            font-size: 14px;
        }
        QGroupBox {
            background-color: #F7F7F7;
            border: 1px solid #CCCCCC;
            margin-top: 10px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px;
            color: #333333;
        }
        QPushButton {
            background-color: #E8E8E8;
            border: 1px solid #AAAAAA;
            padding: 5px;
        }
        QPushButton:hover {
            background-color: #D0D0D0;
        }
        QLineEdit {
            background-color: #FFFFFF;
            border: 1px solid #AAAAAA;
            padding: 3px;
        }
        QSlider::groove:horizontal {
            border: 1px solid #999999;
            height: 8px;
            background: #BFBFBF;
            margin: 2px 0;
        }
        QSlider::handle:horizontal {
            background: #CCCCCC;
            border: 1px solid #777777;
            width: 20px;
            margin: -2px 0;
            border-radius: 3px;
        }
    """)
    window = AlgorithmWindow()
    window.show()
    sys.exit(app.exec_())