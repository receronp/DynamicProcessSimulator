"""
dynamic_process_simulator.py
Autor: Raul Eugenio Ceron Pineda
Version: 1.0.0
"""
import sys
import math
import random
from PyQt5 import QtWidgets, QtCore
from matplotlib.spines import Spine
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

time_data = [0]
input_data = list()
output_data = list()
noise_data = list()

class Window(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)
        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.update_figure)
        timer.start(1000)

        self.file_data = list()

        self.gain = 0
        self.tau = 0
        self.theta_prime = 0
        self.period = 0

        self.n_value = 0

        self.a1 = 0
        self.b1 = 0
        self.b2 = 0
        self.magnitude = 0
        self.noise = 0

        self.setWindowTitle("Dynamic Process Simulator")

        # Figure instance to plot on
        self.figure = Figure()
        self.figure.set_facecolor("none")
        self.setStyleSheet("background-color:#252526;")

        # Canvas Widget that displays the `figure`
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setMinimumWidth(1200)

        # Navigation widget
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.toolbar.setStyleSheet("background-color : white;")
        
        # First line Widgets
        self.gain_label = QtWidgets.QLabel(self, text="Gain (k):", styleSheet="color : white")
        self.tau_label = QtWidgets.QLabel(self, text="Time Constant (𝜏):", styleSheet="color : white")
        self.theta_prime_label = QtWidgets.QLabel(self, text="Dead Time (θ'):", styleSheet="color : white")
        self.period_label = QtWidgets.QLabel(self, text="Period (T)", styleSheet="color : white")

        self.gain_line_edit = QtWidgets.QLineEdit(self, styleSheet="color : white")
        self.gain_line_edit.returnPressed.connect(self.edit_return)
        self.tau_line_edit = QtWidgets.QLineEdit(self, styleSheet="color : white")
        self.tau_line_edit.returnPressed.connect(self.edit_return)
        self.theta_prime_line_edit = QtWidgets.QLineEdit(self, styleSheet="color : white")
        self.theta_prime_line_edit.returnPressed.connect(self.edit_return)
        self.period_line_edit = QtWidgets.QLineEdit(self, styleSheet="color : white")
        self.period_line_edit.returnPressed.connect(self.edit_return)

        # First line elements.
        hbox1 = QtWidgets.QHBoxLayout()
        hbox1.addWidget(self.gain_label)
        hbox1.addWidget(self.gain_line_edit)
        hbox1.addWidget(self.tau_label)
        hbox1.addWidget(self.tau_line_edit)
        hbox1.addWidget(self.theta_prime_label)
        hbox1.addWidget(self.theta_prime_line_edit)
        hbox1.addWidget(self.period_label)
        hbox1.addWidget(self.period_line_edit)
        
        # Second line Widgets
        self.a1_label = QtWidgets.QLabel(self, text="a1 = ?", styleSheet="color : white")
        self.b1_label = QtWidgets.QLabel(self, text="b1 = ?", styleSheet="color : white")
        self.b2_label = QtWidgets.QLabel(self, text="b2 = ?", styleSheet="color : white")

        self.input_label = QtWidgets.QLabel(self, text="Input: ", styleSheet="color : white")
        self.step_box = QtWidgets.QCheckBox("Step Function", self, checked = True, styleSheet="color : white")
        self.noise_box = QtWidgets.QCheckBox("Add Noise", self, checked = False, styleSheet="color : white")

        self.step_magnitude_label = QtWidgets.QLabel(self, text="Magnitude of step (Mo): ", styleSheet="color : white")
        self.step_magnitude_line_edit = QtWidgets.QLineEdit(self, styleSheet="color : white")

        self.step_noise_label = QtWidgets.QLabel(self, text="Magnitude of noise step (Po): ", styleSheet="color : white")
        self.step_noise_line_edit = QtWidgets.QLineEdit(self, styleSheet="color : black")
        self.step_noise_line_edit.setDisabled(True)

        self.step_box.stateChanged.connect(lambda:self.input_button_state(self.step_box))
        self.noise_box.stateChanged.connect(lambda:self.noise_button_state(self.noise_box))

        self.file_button = QtWidgets.QPushButton("Browse File", styleSheet="color : black;")
        self.file_button.setDisabled(True)
        self.file_button.setAutoDefault(False)
        self.file_button.clicked.connect(self.getfile)

        self.reset_button = QtWidgets.QPushButton("Reset", styleSheet="color : white;")
        self.reset_button.setAutoDefault(False)
        self.reset_button.clicked.connect(self.reset)

        # Second line column of labels.
        vbox1 = QtWidgets.QVBoxLayout()
        vbox1.addWidget(self.a1_label)
        vbox1.addWidget(self.b1_label)
        vbox1.addWidget(self.b2_label)
        
        # Second line column of buttons.
        vbox2 = QtWidgets.QVBoxLayout()
        vbox2.addWidget(self.input_label)
        vbox2.addWidget(self.step_box)
        vbox2.addWidget(self.noise_box)

        # Third line column of additional information.
        vbox3 = QtWidgets.QVBoxLayout()
        vbox3.addWidget(self.step_magnitude_label)
        vbox3.addWidget(self.step_magnitude_line_edit)
        vbox3.addWidget(self.step_noise_label)
        vbox3.addWidget(self.step_noise_line_edit)

        vbox4 = QtWidgets.QVBoxLayout()
        vbox4.addWidget(self.file_button)
        vbox4.addWidget(self.reset_button)

        # Second line elements.
        hbox2 = QtWidgets.QHBoxLayout()
        hbox2.addStretch()
        hbox2.addLayout(vbox1)
        hbox2.addStretch()
        hbox2.addLayout(vbox4)
        hbox2.addStretch()
        hbox2.addLayout(vbox2)
        hbox2.addLayout(vbox3)
        hbox2.addStretch()

        # set the layout
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addLayout(hbox1)
        layout.addLayout(hbox2)
        layout.addWidget(self.canvas)
        # layout.addWidget(self.button)
        self.setLayout(layout)
    
    def reset(self):
        global time_data
        time_data = [0]
        self.noise = 0
        input_data.clear()
        output_data.clear()
        noise_data.clear()
        self.file_data.clear()
        self.step_magnitude_line_edit.clear()
        self.step_noise_line_edit.clear()

    def edit_return(self):
        self.focusNextChild()

    def input_button_state(self, state):
        if state.isChecked() == True:
            self.step_magnitude_line_edit.setEnabled(True)
            self.file_button.setDisabled(True)
            self.file_button.setStyleSheet("color : black;")
            self.step_magnitude_line_edit.setStyleSheet("color : white;")
        else:
            self.step_magnitude_line_edit.setDisabled(True)
            self.file_button.setEnabled(True)
            self.file_button.setStyleSheet("color : white;")
            self.step_magnitude_line_edit.setStyleSheet("color : black;")

    def noise_button_state(self,state):
        if state.isChecked() == True:
            self.step_noise_line_edit.setEnabled(True)
            self.step_noise_line_edit.setStyleSheet("color : white;")
        else:
            self.step_noise_line_edit.setDisabled(True)
            self.step_noise_line_edit.setStyleSheet("color : black;")

    def update_figure(self):
        if self.validate_input():
            self.calculate_parameters()
            self.plot_graphs()
            time_data.append(time_data[-1] + 1)

    def validate_input(self):
        try:
            self.gain = float(self.gain_line_edit.text())
            self.tau = float(self.tau_line_edit.text())
            self.theta_prime = float(self.theta_prime_line_edit.text())
            self.period = float(self.period_line_edit.text())
            if self.gain > 0 and self.tau > 0 and self.theta_prime > 0 and self.period > 0 :
                if self.step_box.isChecked():
                    self.magnitude = float(self.step_magnitude_line_edit.text())
                else:
                    if self.file_data[time_data[-1]] is None:
                        return False
                if self.noise_box.isChecked():
                    self.noise = float(self.step_noise_line_edit.text())
                return True
            else:
                return False
        except:
            return False

    def update_labels(self):
        self.a1_label.setText("a1 = {}".format(self.a1))
        self.b1_label.setText("b1 = {}".format(self.b1))
        self.b2_label.setText("b2 = {}".format(self.b2))

    def calculate_parameters(self):
        self.n_value = int(self.theta_prime / self.period)
        theta = self.theta_prime - self.n_value * self.period
        m = 1 - theta / self.period
        self.a1 = math.exp((-self.period)/self.tau)
        self.b1 = self.gain * (1 - math.exp((-m * self.period) / self.tau))
        self.b2 = self.gain * (math.exp((-m * self.period) / self.tau) - math.exp((-self.period)/self.tau))
        self.update_labels()

    def getfile(self):
        try:
            self.file_data.clear()
            fname = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file', '.',"Text files (*.txt)")
            with open(fname[0], 'r') as file_input:
                for line in file_input.readlines():
                    self.file_data.append(float(line.split()[0]))
        except FileNotFoundError as fnf:
            print(fnf)
    
    def plot_graphs(self):
        self.plot_input()
        self.plot_noise()
        self.plot_response()

    def plot_input(self):
        if(self.step_box.isChecked()):
            global input_data
            input_data.append(self.magnitude)
        else:
            input_data.append(self.file_data[time_data[-1]])

        # create an axis
        ax = self.figure.add_subplot(131)
        self.plot_to_figure(ax, input_data, "Input")

    def plot_noise(self):
        global noise_data
        if self.noise_box.isChecked():
            noise_data.append(self.noise)
        else:
            noise_data.append(0)
        
        # create an axis
        ax = self.figure.add_subplot(132)
        self.plot_to_figure(ax, noise_data, "Noise")

    def plot_response(self):
        if self.step_box.isChecked():
            try:
                if self.magnitude > 0:
                    self.generate_response()
            except ValueError as ve:
                print(ve)
        else:
            try:
                self.generate_response()
            except:
                print("Unexpected error:", sys.exc_info()[0])
                raise

        ax = self.figure.add_subplot(133)
        self.plot_to_figure(ax, output_data, "Output")

    def generate_response(self):
        if time_data[-1] - self.n_value - 2 > 0:
            output_data.append(self.a1 * output_data[time_data[-1]-1] + \
                                    self.b1 * input_data[time_data[-1] - self.n_value - 1] + \
                                    self.b2 * input_data[time_data[-1] - self.n_value - 2] + self.noise)
        elif time_data[-1] - self.n_value - 1 > 0:
            output_data.append(self.a1 * output_data[time_data[-1]-1] + \
                                    self.b1 * input_data[time_data[-1] - self.n_value - 1] + self.noise)
        elif time_data[-1] > 0:
            output_data.append(self.a1 * output_data[time_data[-1]-1] + self.noise)
        else: 
            output_data.append(0.0 + self.noise)

    def plot_to_figure(self, ax, data, title):
        ax.set_facecolor('#252526')
        for child in ax.get_children():
            if isinstance(child, Spine):
                child.set_color('white')

        ax.tick_params(axis='both', colors='white')
        ax.set_title(title)
        ax.clear()
        if len(time_data) > 50:
            ax.plot(list(range(len(time_data) - 50, len(time_data))), 
                    data[len(time_data) - 50 :], '.-', color = 'white')
        else:
            ax.plot(list(range(0, len(time_data))), data, '.-', color = 'white')
        self.canvas.draw()

if __name__ == '__main__':
    app = QtWidgets.QApplication([])

    main = Window()
    main.show()

    sys.exit(app.exec_())
