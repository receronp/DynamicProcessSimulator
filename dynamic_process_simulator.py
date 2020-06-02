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
system_data = list()
noise_data = list()


class Window(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)
        self.time_on = False
        self.file_to_input = False
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

        self.kc = 0
        self.set_point = 0
        self.integral_constant = 0
        self.derivative_constant = 0

        self.q0 = 0
        self.q1 = 0
        self.q2 = 0

        self.e_k0 = 0
        self.e_k1 = 0
        self.e_k2 = 0
        self.m_k = 0

        self.setWindowTitle("Dynamic Process Simulator")

        # Figure instance to plot on
        self.figure = Figure()
        self.figure.set_facecolor("none")
        self.setStyleSheet("background-color:#252526;")

        # Canvas Widget that displays the `figure`
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setMinimumSize(1200, 600)

        # Navigation widget
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.toolbar.setStyleSheet("background-color : white;")

        # First line Widgets
        self.gain_line_edit = QtWidgets.QLineEdit(self, styleSheet="color : white")
        self.gain_line_edit.returnPressed.connect(self.edit_return)
        self.tau_line_edit = QtWidgets.QLineEdit(self, styleSheet="color : white")
        self.tau_line_edit.returnPressed.connect(self.edit_return)
        self.theta_prime_line_edit = QtWidgets.QLineEdit(
            self, styleSheet="color : white"
        )
        self.theta_prime_line_edit.returnPressed.connect(self.edit_return)
        self.period_line_edit = QtWidgets.QLineEdit(self, styleSheet="color : white")
        self.period_line_edit.returnPressed.connect(self.edit_return)

        # First line elements.
        hbox1 = QtWidgets.QHBoxLayout()
        hbox1.addWidget(QtWidgets.QLabel(text="Gain (k):", styleSheet="color : white"))
        hbox1.addWidget(self.gain_line_edit)
        hbox1.addWidget(
            QtWidgets.QLabel(text="Time Constant (𝜏):", styleSheet="color : white")
        )
        hbox1.addWidget(self.tau_line_edit)
        hbox1.addWidget(
            QtWidgets.QLabel(text="Dead Time (θ'):", styleSheet="color : white")
        )
        hbox1.addWidget(self.theta_prime_line_edit)
        hbox1.addWidget(QtWidgets.QLabel(text="Period (T)", styleSheet="color : white"))
        hbox1.addWidget(self.period_line_edit)

        # Second line Widgets
        self.a1_label = QtWidgets.QLabel(
            self, text="a1 = ?", styleSheet="color : white"
        )
        self.b1_label = QtWidgets.QLabel(
            self, text="b1 = ?", styleSheet="color : white"
        )
        self.b2_label = QtWidgets.QLabel(
            self, text="b2 = ?", styleSheet="color : white"
        )
        self.n_value_label = QtWidgets.QLabel(
            self, text="N = ?", styleSheet="color : white"
        )

        self.q0_label = QtWidgets.QLabel(
            self, text="q0 = ?", styleSheet="color : white"
        )

        self.q1_label = QtWidgets.QLabel(
            self, text="q1 = ?", styleSheet="color : white"
        )

        self.q2_label = QtWidgets.QLabel(
            self, text="q2 = ?", styleSheet="color : white"
        )

        self.error_label = QtWidgets.QLabel(
            self, text="error = ?", styleSheet="color : white"
        )

        self.step_box = QtWidgets.QCheckBox(
            "Step Function", self, checked=True, styleSheet="color : white"
        )
        self.noise_box = QtWidgets.QCheckBox(
            "Add Noise", self, checked=False, styleSheet="color : white"
        )

        self.manual_mode = QtWidgets.QRadioButton(
            self, text="Manual Mode", checked=True, styleSheet="color : white"
        )
        self.auto_mode = QtWidgets.QRadioButton(
            self, text="Auto Mode", styleSheet="color : white"
        )

        self.kc_line_edit = QtWidgets.QLineEdit(self, styleSheet="color : white")
        self.set_point_line_edit = QtWidgets.QLineEdit(self, styleSheet="color : white")
        self.integral_line_edit = QtWidgets.QLineEdit(self, styleSheet="color : white")
        self.derivative_line_edit = QtWidgets.QLineEdit(
            self, styleSheet="color : white"
        )
        self.kc_line_edit.returnPressed.connect(self.set_auto_time_on)
        self.kc_line_edit.textChanged.connect(self.set_auto_time_off)
        self.set_point_line_edit.returnPressed.connect(self.set_auto_time_on)
        self.set_point_line_edit.textChanged.connect(self.set_auto_time_off)
        self.integral_line_edit.returnPressed.connect(self.set_auto_time_on)
        self.integral_line_edit.textChanged.connect(self.set_auto_time_off)
        self.derivative_line_edit.returnPressed.connect(self.set_auto_time_on)
        self.derivative_line_edit.textChanged.connect(self.set_auto_time_off)

        self.step_magnitude_line_edit = QtWidgets.QLineEdit(
            self, styleSheet="color : white"
        )
        self.step_magnitude_line_edit.returnPressed.connect(self.set_time_on)
        self.step_magnitude_line_edit.textChanged.connect(self.set_time_off)

        self.step_noise_line_edit = QtWidgets.QLineEdit(
            self, styleSheet="color : black"
        )
        self.step_noise_line_edit.setDisabled(True)
        self.step_noise_line_edit.returnPressed.connect(self.set_time_on)
        self.step_noise_line_edit.textChanged.connect(self.set_time_off)

        self.step_box.stateChanged.connect(
            lambda: self.input_button_state(self.step_box)
        )
        self.noise_box.stateChanged.connect(
            lambda: self.noise_button_state(self.noise_box)
        )

        self.file_button = QtWidgets.QPushButton(
            "Browse File", styleSheet="color : black;"
        )
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
        vbox1.addWidget(self.n_value_label)

        vbox8 = QtWidgets.QVBoxLayout()
        vbox8.addWidget(self.q0_label)
        vbox8.addWidget(self.q1_label)
        vbox8.addWidget(self.q2_label)
        vbox8.addWidget(self.error_label)

        # Second line column of buttons.
        vbox2 = QtWidgets.QVBoxLayout()
        vbox2.addWidget(QtWidgets.QLabel(text="Input: ", styleSheet="color : white"))
        vbox2.addWidget(self.step_box)
        vbox2.addWidget(self.noise_box)
        vbox2.addStretch()

        # Third line column of additional information.
        vbox3 = QtWidgets.QVBoxLayout()
        vbox3.addWidget(
            QtWidgets.QLabel(
                text="Magnitude of step (Mo): ", styleSheet="color : white"
            )
        )
        vbox3.addWidget(self.step_magnitude_line_edit)
        vbox3.addWidget(
            QtWidgets.QLabel(
                text="Magnitude of noise step (Po): ", styleSheet="color : white"
            )
        )
        vbox3.addWidget(self.step_noise_line_edit)

        vbox4 = QtWidgets.QVBoxLayout()
        vbox4.addWidget(self.file_button)
        vbox4.addWidget(self.reset_button)

        # Automatic line column.
        vbox5 = QtWidgets.QVBoxLayout()
        vbox5.addWidget(
            QtWidgets.QLabel(text="Mode selection:", styleSheet="color : white")
        )
        vbox5.addWidget(self.manual_mode)
        vbox5.addWidget(self.auto_mode)
        vbox5.addStretch()

        # Auto input column.
        vbox6 = QtWidgets.QVBoxLayout()
        vbox6.addWidget(
            QtWidgets.QLabel(text="Controller Gain (Kc):", styleSheet="color : white")
        )
        vbox6.addWidget(self.kc_line_edit)
        vbox6.addWidget(
            QtWidgets.QLabel(text="Set Point (r):", styleSheet="color : white")
        )
        vbox6.addWidget(self.set_point_line_edit)

        vbox7 = QtWidgets.QVBoxLayout()
        vbox7.addWidget(
            QtWidgets.QLabel(
                text="Integral Time Constant (𝜏i):", styleSheet="color : white"
            )
        )
        vbox7.addWidget(self.integral_line_edit)
        vbox7.addWidget(
            QtWidgets.QLabel(
                text="Derivative Time Constant (𝜏d):", styleSheet="color : white"
            )
        )
        vbox7.addWidget(self.derivative_line_edit)

        # Second line elements.
        hbox2 = QtWidgets.QHBoxLayout()
        hbox2.addStretch()
        hbox2.addLayout(vbox5)
        hbox2.addStretch()
        hbox2.addLayout(vbox2)
        hbox2.addLayout(vbox3)
        hbox2.addStretch()
        hbox2.addLayout(vbox4)
        hbox2.addStretch()
        hbox2.addLayout(vbox6)
        hbox2.addLayout(vbox7)
        hbox2.addStretch()
        hbox2.addLayout(vbox1)
        hbox2.addStretch()
        hbox2.addLayout(vbox8)
        hbox2.addStretch()

        # Setting of layout
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addLayout(hbox1)
        layout.addLayout(hbox2)
        layout.addWidget(self.canvas)
        self.setLayout(layout)

    def set_auto_time_on(self):
        if self.auto_mode.isChecked():
            self.set_time_on()

    def set_auto_time_off(self):
        if self.auto_mode.isChecked():
            self.set_time_off()

    def set_time_on(self):
        self.time_on = True

    def set_time_off(self):
        self.time_on = False
        if self.file_to_input == True:
            # self.file_data.clear()
            self.time_on = True
            self.file_to_input = False

    def reset(self):
        global time_data
        time_data = [0]
        self.noise = 0
        input_data.clear()
        system_data.clear()
        output_data.clear()
        noise_data.clear()
        self.file_data.clear()
        self.step_magnitude_line_edit.clear()
        self.step_noise_line_edit.clear()
        self.kc_line_edit.clear()
        self.set_point_line_edit.clear()
        self.derivative_line_edit.clear()
        self.integral_line_edit.clear()
        self.manual_mode.toggle()

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
            self.file_data.clear()

    def noise_button_state(self, state):
        if state.isChecked() == True:
            self.step_noise_line_edit.setEnabled(True)
            self.step_noise_line_edit.setStyleSheet("color : white;")
        else:
            self.step_noise_line_edit.setDisabled(True)
            self.step_noise_line_edit.setStyleSheet("color : black;")

    def update_figure(self):
        if self.validate_input() and self.time_on:
            self.calculate_parameters()
            self.plot_graphs()
            time_data.append(time_data[-1] + 1)

    def validate_input(self):
        try:
            self.gain = float(self.gain_line_edit.text())
            self.tau = float(self.tau_line_edit.text())
            self.theta_prime = float(self.theta_prime_line_edit.text())
            self.period = float(self.period_line_edit.text())
            if (
                self.gain > 0
                and self.tau > 0
                and self.theta_prime > 0
                and self.period > 0
            ):
                if self.auto_mode.isChecked():
                    self.kc = float(self.kc_line_edit.text())
                    self.set_point = float(self.set_point_line_edit.text())
                    self.integral_constant = float(self.integral_line_edit.text())
                    self.derivative_constant = float(self.derivative_line_edit.text())
                elif self.step_box.isChecked():
                    if float(self.step_magnitude_line_edit.text()) == 0.0:
                        self.magnitude = 0.0000000000001
                    else:
                        self.magnitude = float(self.step_magnitude_line_edit.text())
                else:
                    if len(self.file_data) == 0:
                        return False
                    if len(self.file_data) <= time_data[-1]:
                        self.file_to_input = True
                        self.magnitude = float(self.file_data[-1])
                        self.step_magnitude_line_edit.setText(
                            f"{self.file_data[-1]:.3f}"
                        )
                        self.step_box.setChecked(True)
                if self.noise_box.isChecked():
                    self.noise = float(self.step_noise_line_edit.text())
                return True
            else:
                return False
        except:
            return False

    def update_labels(self):
        self.a1_label.setText(f"a1 = {self.a1:.3f}")
        self.b1_label.setText(f"b1 = {self.b1:.3f}")
        self.b2_label.setText(f"b2 = {self.b2:.3f}")
        self.n_value_label.setText(f"N = {self.n_value:.3f}")
        if self.auto_mode.isChecked():
            self.q0_label.setText(f"q0 = {self.q0:.3f}")
            self.q1_label.setText(f"q1 = {self.q1:.3f}")
            self.q2_label.setText(f"q2 = {self.q2:.3f}")

    def calculate_parameters(self):
        self.n_value = int(self.theta_prime / self.period)
        theta = self.theta_prime - self.n_value * self.period
        m = 1 - theta / self.period
        self.a1 = math.exp((-self.period) / self.tau)
        self.b1 = self.gain * (1 - math.exp((-m * self.period) / self.tau))
        self.b2 = self.gain * (
            math.exp((-m * self.period) / self.tau)
            - math.exp((-self.period) / self.tau)
        )

        if self.auto_mode.isChecked():
            self.q0 = self.kc * (
                1
                + self.period / self.integral_constant
                + self.derivative_constant / self.period
            )
            self.q1 = self.kc * (-1 - 2 * self.derivative_constant / self.period)
            self.q2 = self.kc * self.derivative_constant / self.period

        self.update_labels()

    def getfile(self):
        try:
            self.file_data.clear()
            fname = QtWidgets.QFileDialog.getOpenFileName(
                self, "Open file", ".", "Text files (*.txt)"
            )
            self.file_data = input_data.copy()
            with open(fname[0], "r") as file_input:
                for line in file_input.readlines():
                    if line[0] != "\n":
                        self.file_data.append(float(line.split()[0]))
            self.time_on = True
        except FileNotFoundError as fnf:
            print(fnf)

    def plot_graphs(self):
        self.plot_inputs()
        self.plot_response()

    def plot_inputs(self):
        global input_data
        if self.auto_mode.isChecked():
            input_data.append(self.m_k)
        elif self.step_box.isChecked():
            input_data.append(self.magnitude)
        else:
            input_data.append(self.file_data[time_data[-1]])

        global noise_data
        if self.noise_box.isChecked():
            noise_data.append(self.noise)
        else:
            noise_data.append(0)

        ax = self.figure.add_subplot(211)
        self.plot_to_figure(ax, [input_data, noise_data], "Input", [-10, 100])

    def plot_response(self):
        self.generate_response()
        ax = self.figure.add_subplot(212)
        self.plot_to_figure(ax, [output_data], "Output", [-10, 100])

    def generate_response(self):
        if time_data[-1] - self.n_value - 2 > -1:
            system_data.append(
                self.a1 * system_data[time_data[-1] - 1]
                + self.b1 * input_data[time_data[-1] - self.n_value]
                + self.b2 * input_data[time_data[-1] - self.n_value - 1]
            )
        elif time_data[-1] - self.n_value - 1 > -1:
            system_data.append(
                self.a1 * system_data[time_data[-1] - 1]
                + self.b1 * input_data[time_data[-1] - self.n_value]
            )
        elif time_data[-1] > 0:
            system_data.append(self.a1 * system_data[time_data[-1] - 1])
        else:
            system_data.append(0.0)

        output_data.append(system_data[-1] + self.noise)
        if self.manual_mode.isChecked():
            self.set_point = output_data[-1]
            self.set_point_line_edit.setText(f"{self.set_point:.3f}")

        self.e_k2 = self.e_k1
        self.e_k1 = self.e_k0
        self.e_k0 = self.set_point - output_data[-1]
        self.m_k = (
            input_data[-1]
            + self.q0 * self.e_k0
            + self.q1 * self.e_k1
            + self.q2 * self.e_k2
        )
        self.error_label.setText(f"error = {self.e_k0:.3f}")

    def plot_to_figure(self, ax, datas, title, ylim):
        ax.set_facecolor("#252526")
        for child in ax.get_children():
            if isinstance(child, Spine):
                child.set_color("white")

        ax.tick_params(axis="both", colors="white")
        ax.clear()
        ax.set_title(title, color="white")
        ax.set_ylim(ylim)
        colors = ["lime", "red", "white"]
        for data in range(len(datas)):
            if len(time_data) > 50:
                ax.plot(
                    list(range(len(time_data) - 50, len(time_data))),
                    datas[data][len(time_data) - 50 :],
                    ".-",
                    color=colors[data],
                )
            else:
                ax.plot(
                    list(range(0, len(time_data))),
                    datas[data],
                    ".-",
                    color=colors[data],
                )
        self.figure.tight_layout()
        self.canvas.draw()


if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    main = Window()
    main.show()

    sys.exit(app.exec_())
