import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                            QPushButton, QFormLayout, QLineEdit, QLabel)
from PyQt5.QtCore import Qt
from animation import SphereWidget

class AlgorithmWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("3D Sphere Visualizer")
        self.setMinimumSize(800, 600)
        
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # 3D виджет из отдельного файла
        self.visualization = SphereWidget()
        layout.addWidget(self.visualization, stretch=1)
        
        # Панель параметров
        self.parameters_widget = QWidget()
        parameters_layout = QFormLayout(self.parameters_widget)
        self.create_parameters(parameters_layout)
        layout.addWidget(self.parameters_widget)
        
        # Кнопка расчета
        self.calculate_btn = QPushButton("Рассчитать")
        self.calculate_btn.clicked.connect(self.calculate)
        layout.addWidget(self.calculate_btn, alignment=Qt.AlignRight)
    
    def create_parameters(self, layout):
        self.radius_input = QLineEdit("1.0")
        layout.addRow(QLabel("Радиус:"), self.radius_input)
        
        self.segments_input = QLineEdit("32")
        layout.addRow(QLabel("Сегменты:"), self.segments_input)
    
    def calculate(self):
        try:
            radius = float(self.radius_input.text())
            segments = int(self.segments_input.text())
            self.visualization.set_sphere_parameters(radius, segments)
        except ValueError:
            print("Ошибка ввода параметров")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AlgorithmWindow()
    window.show()
    sys.exit(app.exec_())