from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QCheckBox,
    QVBoxLayout,
    QWidget,
    QFormLayout,
    QSlider,
    QPushButton,
    QBoxLayout,
)
from time import sleep
from copy import deepcopy
from .cv2_thread import Cv2Thread
from .config import (
    window_title,
    window_geometry,
    IMAGE_WIDTH,
    IMAGE_HEIGHT,
    auto_start_camera,
    AppConfig,
)
from .utils import list_camera_ports
from .logs import LogsWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.app_config = AppConfig()

        print("get working camera ports")
        _, self.camera_ports = list_camera_ports()

        # Thread in charge of updating the image
        self.create_cv2_thread()

        # Create logs window
        self.logs_window = LogsWindow(
            parent_window=self,
        )

        # Title and dimensions
        self.setWindowTitle(window_title)
        self.setGeometry(*window_geometry)

        # Create a label for the display camera
        self.camera_label = QLabel()
        self.camera_label.setFixedSize(IMAGE_WIDTH, IMAGE_HEIGHT)

        # Create a button to start/stop the camera
        self.cv2_btn = QPushButton()
        self.cv2_btn.styleSheet = "margin-top: 10px;"
        self.cv2_btn.setFixedHeight(30)
        self.cv2_btn.clicked.connect(self.cv2_btn_clicked)

        # Add logs window button
        logs_window_button = QPushButton("Show logs")
        logs_window_button.setFixedHeight(30)
        logs_window_button.clicked.connect(self.logs_window.toggle)

        config_layout = QVBoxLayout()
        # Add camera ports combobox
        self.add_controls_camera_ports(config_layout)

        # Add inputs
        for input in self.app_config.get_config_fields():
            if input.get("hidden", False):
                continue
            input_type = input["input"]
            if input_type == "checkbox":
                self.add_checkbox(input, config_layout)
            elif "slider" in input_type:
                self.add_slider(input, config_layout)
            elif input_type == "label":
                label = QLabel(input["name"])
                label.setStyleSheet("font-weight: bold;")
                config_layout.addWidget(label)

        # self.add_controls_mode_combobox(log_layout)

        # Left layout
        left_layout = QVBoxLayout()
        left_layout.addWidget(self.camera_label)
        left_layout_buttons = QHBoxLayout()
        left_layout_buttons.addWidget(self.cv2_btn)
        left_layout_buttons.addWidget(logs_window_button)
        left_layout.addLayout(left_layout_buttons)

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.addLayout(left_layout)
        main_layout.addLayout(config_layout)

        # Central widget
        main_widget = QWidget(self)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # Auto start camera
        if auto_start_camera:
            self.cv2_thread.start()
        else:
            self.cv2_btn.setText("Start camera")
            self.cv2_btn.setDisabled(False)

    # when window change position
    def moveEvent(self, event):
        self.logs_window.move_by_parent(
            self.pos().x(),
            self.pos().y(),
        )

    def create_cv2_thread(self):
        self.cv2_thread = Cv2Thread(
            parent=self,
            app_config=self.app_config,
        )
        # self.cv2_thread.finished.connect(self.close)
        self.cv2_thread.update_status.connect(self.setCv2Status)
        self.cv2_thread.update_frame.connect(self.setCv2Image)
        self.cv2_thread.update_state.connect(self.setCv2State)

    def cv2_btn_clicked(self):
        self.cv2_thread.toggle()

    @Slot(QImage)
    def setCv2Image(self, image):
        self.camera_label.setPixmap(QPixmap.fromImage(image))

    @Slot(dict)
    def setCv2State(self, state: dict):
        self.logs_window.state_label.setText(str(state["body"]))

    @Slot(dict)
    def setCv2Status(self, status: dict):
        if status["loading"]:
            self.cv2_btn.setText("Loading camera...")
            self.cv2_btn.setDisabled(True)
        else:
            self.cv2_btn.setDisabled(False)

            if self.cv2_thread.status:
                self.cv2_btn.setText("Stop camera")
            else:
                self.cv2_btn.setText("Start camera")

    def add_slider(self, slider: dict, layout: QBoxLayout):
        key = slider["key"]
        _type = slider["type"]
        _input = slider["input"]
        description = slider.get("description", None)

        row = QFormLayout()

        _slider = QSlider(Qt.Horizontal)
        _slider.setRange(slider["min"], slider["max"])
        _slider.setValue(slider["value"])
        _slider.setSingleStep(1)
        _slider.setFixedSize(200, 20)

        _slider.valueChanged.connect(
            lambda value: self.slider_value_changed(key, value, _type, _input)
        )

        label = QLabel(f"{slider['name']}: ")
        if description:
            label.setToolTip(description)

        row.addRow(label, _slider)
        layout.addLayout(row)

    def slider_value_changed(self, key: str, value, type: str, input):
        if "percentage" in input:
            value /= 100
        # print(key, value, type, input)
        if type == "mp":
            self.cv2_thread.mp_config[key] = value
            self.app_config.mp_config[key] = value
        elif type == "body":
            self.cv2_thread.body[key] = value
            self.app_config.body_config[key] = value
        elif type == "events":
            self.cv2_thread.body.events[key] = value
            self.app_config.events_config[key] = value

    def add_checkbox(self, checkbox: dict, layout: QBoxLayout):
        _checkbox = QCheckBox(checkbox["name"])
        key = checkbox["key"]
        _type = checkbox["type"]
        description = checkbox.get("description", None)

        checked = Qt.Unchecked
        if _type == "mp":
            checked = Qt.Checked if self.app_config.mp_config[key] else Qt.Unchecked
        elif _type == "body":
            checked = Qt.Checked if self.app_config.body_config[key] else Qt.Unchecked
        elif _type == "events":
            checked = Qt.Checked if self.app_config.events_config[key] else Qt.Unchecked
        _checkbox.setCheckState(checked)
        if description:
            _checkbox.setToolTip(description)

        _checkbox.stateChanged.connect(
            lambda value: self.checkbox_state_changed(key, value, _type)
        )
        layout.addWidget(_checkbox)

    def checkbox_state_changed(self, key, value, type):
        new_value = not not value
        if type == "mp":
            self.cv2_thread.mp_config[key] = new_value
            self.app_config.mp_config[key] = new_value
        elif type == "body":
            self.cv2_thread.body[key] = new_value
            self.app_config.body_config[key] = new_value
        elif type == "events":
            self.cv2_thread.body.events[key] = new_value
            self.app_config.events_config[key] = new_value

    def add_controls_camera_ports(self, layout: QBoxLayout):
        controls_row = QFormLayout()

        controls_combobox = QComboBox()
        controls_combobox.setFixedWidth(100)
        controls_combobox.addItems(list(map(str, self.camera_ports)))
        controls_combobox.currentIndexChanged.connect(self.camera_ports_combobox_change)

        controls_row.addRow("Select camera: ", controls_combobox)
        layout.addLayout(controls_row)

    def camera_ports_combobox_change(self, index: int):
        self.cv2_thread.camera_port = self.camera_ports[index]

        if self.cv2_thread.status:
            self.cv2_thread.toggle()
