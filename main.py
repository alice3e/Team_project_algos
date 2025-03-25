import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                            QPushButton, QFormLayout, QLineEdit, QLabel,
                            QSlider, QHBoxLayout, QMessageBox)
from PyQt5.QtCore import Qt
from animation import SphereWidget
from model import PhysicsModel

class AlgorithmWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Motorcycle on Sphere Physics")
        self.setMinimumSize(1000, 800)
        
        self.physics_model = PhysicsModel()
        self.sphere_radius = 1.0
        
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        self.visualization = SphereWidget()
        self.visualization.set_physics_parameters(self.sphere_radius)
        layout.addWidget(self.visualization, stretch=1)
        
        self.parameters_widget = QWidget()
        parameters_layout = QFormLayout(self.parameters_widget)
        
        self.mass_input = QLineEdit("1.0")
        parameters_layout.addRow(QLabel("Масса (кг):"), self.mass_input)
        
        self.velocity_input = QLineEdit("3.13")
        parameters_layout.addRow(QLabel("Скорость (м/с):"), self.velocity_input)
        
        self.time_input = QLineEdit("5")
        parameters_layout.addRow(QLabel("Время симуляции (сек):"), self.time_input)
        
        layout.addWidget(self.parameters_widget)
        
        self.timeline = QSlider(Qt.Horizontal)
        self.timeline.setRange(0, 100)
        self.timeline.valueChanged.connect(self.update_frame)
        layout.addWidget(self.timeline)
        
        control_widget = QWidget()
        control_layout = QHBoxLayout(control_widget)
        
        self.calculate_btn = QPushButton("Рассчитать траекторию")
        self.calculate_btn.clicked.connect(self.calculate_trajectory)
        
        self.info_btn = QPushButton("Минимальная скорость")
        self.info_btn.clicked.connect(self.show_min_speed)
        
        control_layout.addWidget(self.calculate_btn)
        control_layout.addWidget(self.info_btn)
        layout.addWidget(control_widget)

    def calculate_trajectory(self):
        try:
            mass = float(self.mass_input.text())
            velocity = float(self.velocity_input.text())
            simulation_time = float(self.time_input.text())
            
            if velocity <= 0 or mass <= 0 or simulation_time <= 0:
                raise ValueError
                
            trajectory = self.physics_model.calculate_trajectory(mass, velocity, simulation_time)
            self.visualization.set_trajectory(trajectory)
            self.timeline.setRange(0, len(trajectory)-1)
            
            v_min = self.physics_model.calculate_min_speed()
            if velocity < v_min:
                QMessageBox.warning(self, "Предупреждение", 
                    f"Скорость ниже минимальной ({v_min:.2f} м/с)!")
            
        except ValueError:
            QMessageBox.critical(self, "Ошибка", "Некорректные входные параметры!")

    def show_min_speed(self):
        v_min = self.physics_model.calculate_min_speed()
        QMessageBox.information(self, "Минимальная скорость",
                               f"Минимальная скорость для радиуса {self.sphere_radius} м:\n"
                               f"{v_min:.2f} м/с")

    def update_frame(self, value):
        max_frame = self.timeline.maximum()
        current_frame = max_frame - value  # Инвертируем значение ползунка
        self.visualization.set_current_frame(current_frame)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AlgorithmWindow()
    window.show()
    sys.exit(app.exec_())