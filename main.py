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
        self.setWindowTitle("Sphere Motion Simulator")
        self.setMinimumSize(1000, 800)
        
        self.physics_model = None
        self.trajectory = []
        
        # Инициализация интерфейса
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # 3D визуализация
        self.visualization = SphereWidget()
        layout.addWidget(self.visualization, stretch=1)
        
        # Панель параметров
        params_widget = QWidget()
        params_layout = QFormLayout(params_widget)
        
        self.radius_input = QLineEdit("1.0")  # Поле для радиуса
        params_layout.addRow(QLabel("Радиус сферы (м):"), self.radius_input)
        
        self.velocity_input = QLineEdit("5.0")  # Переименовано в ускорение
        params_layout.addRow(QLabel("Ускорение (м/с²):"), self.velocity_input)
        
        # движение всегда осуществляется по Архимедовой спирали, где k — смещение точки M по лучу r при повороте на угол, равный одному радиану.
        self.k_input = QLineEdit("0.0")
        params_layout.addRow(QLabel("K:"), self.k_input)
        
        self.time_input = QLineEdit("10.0")
        params_layout.addRow(QLabel("Время симуляции (сек):"), self.time_input)
        
        # Новое поле для массы точки
        self.mass_input = QLineEdit("1.0")
        params_layout.addRow(QLabel("Масса точки (кг):"), self.mass_input)
        
        layout.addWidget(params_widget)
        
        # Таймлайн
        self.timeline = QSlider(Qt.Horizontal)
        self.timeline.setRange(0, 100)
        self.timeline.valueChanged.connect(self.update_frame)
        layout.addWidget(self.timeline)
        
        # Кнопки управления
        control_widget = QWidget()
        control_layout = QHBoxLayout(control_widget)
        
        self.calculate_btn = QPushButton("Рассчитать")
        self.calculate_btn.clicked.connect(self.calculate)
        control_layout.addWidget(self.calculate_btn)
        layout.addWidget(control_widget)
        
    def calculate(self):
        try:
            radius = float(self.radius_input.text())
            acceleration = float(self.velocity_input.text())  # Переименовано в ускорение
            k = float(self.k_input.text())
            sim_time = float(self.time_input.text())
            mass = float(self.mass_input.text())
            
            if radius <= 0 or acceleration <= 0 or sim_time <= 0 or mass <= 0:
                raise ValueError("Параметры должны быть положительными числами")
                
            self.physics_model = PhysicsModel(radius)
            self.visualization.set_sphere_radius(radius)
            
            # Расчет траектории с учетом ускорения и массы
            self.trajectory = self.physics_model.calculate_trajectory(acceleration, k, sim_time, mass)
                        
            # Проверка на пустую траекторию
            if not self.trajectory:
                QMessageBox.warning(self, "Предупреждение", "Точка сразу оторвалась от поверхности!")
                return
                
            # Обновление визуализации
            self.visualization.set_trajectory(self.trajectory)
            self.timeline.setRange(0, len(self.trajectory)-1)
            self.timeline.setValue(0)
            
        except ValueError as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    def update_frame(self, value):
        # Прямое соответствие: влево - начало, вправо - конец
        self.visualization.set_current_frame(value)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AlgorithmWindow()
    window.show()
    sys.exit(app.exec_())
