"""

"""

# SYSTEM IMPORTS

# STANDARD LIB IMPORTS

# LOCAL APP IMPORTS
from importlib import reload

import maya.OpenMayaUI as omui
import pymel.core as pm
from PySide2 import QtCore
from PySide2 import QtWidgets
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
from shiboken2 import wrapInstance

from . import SkeletonConnectorFunctional

reload(SkeletonConnectorFunctional)

def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)

class SkeletonConnectorUI(MayaQWidgetDockableMixin, QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super(SkeletonConnectorUI, self).__init__()
        self.SkeletonConnectorFunctional = SkeletonConnectorFunctional.Skeleton_Connector_Functional()
        self.create_widget()
        self.populate_constraint_list()

    def execute_skeleton_connect(self):
        self.SkeletonConnectorFunctional.skeleton_attach(
            rig_ns=self.driver_textbox.text(),
            driven_ns=self.driven_textbox.text(),
            top_level_joint=self.tlj_textbox.text(),
            connect_type=self.connect_type_dropdown.currentText()
        )
        self.populate_constraint_list()

    def execute_skeleton_detach(self):
        selected_items = self.existing_constraints.selectedItems()
        for item in selected_items:
            text = item.text()
            rig_ns = text.split("<--")[0][:-2]
            groom_ns = text.split("<--")[1][2:].split("(tlj")[0][:-2]
            top_level_joint = text.split("tlj:")[1][:-1]
            print(rig_ns, groom_ns, top_level_joint)
            self.SkeletonConnectorFunctional.skeleton_detach(rig_ns=rig_ns,
                                                        driven_ns=groom_ns,
                                                        top_level_joint=top_level_joint)
        self.populate_constraint_list()

    def driver_ns_pickwhip(self):
        selection = pm.selected()[0]
        driver_ns = selection.name().split(":")[0]
        self.driver_textbox.setText(driver_ns)

    def driven_ns_pickwhip(self):
        selection = pm.selected()[0]
        driven_ns = selection.name().split(":")[0]
        self.driven_textbox.setText(driven_ns)

    def tlj_name_pickwhip(self):
        selection = pm.selected()[0]
        tlj_name = selection.name().split(":")[1]
        self.tlj_textbox.setText(tlj_name)

    def populate_constraint_list(self):
        # Read data from functional
        # Update list widget
        constraint_data = self.SkeletonConnectorFunctional.load_scene_constraint_data()
        self.existing_constraints.clear()
        list_item = QtWidgets.QListWidgetItem(self.existing_constraints)
        for index, data in enumerate(constraint_data):
            list_item.setText(f"{data}")
            list_item = QtWidgets.QListWidgetItem(self.existing_constraints)
            list_item.setSelected(True)

    def create_widget(self):
        self.setWindowFlags(QtCore.Qt.Tool)

        self.setParent(maya_main_window())
        self.setWindowFlags(QtCore.Qt.Window)

        # Set the object name
        self.setObjectName('SkeletonConnectorUI_UniqueId')
        self.setWindowTitle('Skeleton Connector Tool')
        self.setMinimumSize(600, 200)
        # self.setMaximumSize(600, 200)

        self.driver_label = QtWidgets.QLabel(self, text="Driver Namespace")
        self.driver_label.setFixedWidth(120)
        self.driver_textbox = QtWidgets.QLineEdit(self)
        self.driver_textbox.setPlaceholderText("Driver namespace")
        self.driver_pickwhip = QtWidgets.QPushButton(self, text="Get from selection")
        self.driver_pickwhip.clicked.connect(self.driver_ns_pickwhip)

        self.driven_label = QtWidgets.QLabel(self, text="Driven Namespace")
        self.driven_label.setFixedWidth(120)
        self.driven_textbox = QtWidgets.QLineEdit(self)
        self.driven_textbox.setPlaceholderText("Driven namespace")
        self.driven_pickwhip = QtWidgets.QPushButton(self, text="Get from selection")
        self.driven_pickwhip.clicked.connect(self.driven_ns_pickwhip)

        self.tlj_label = QtWidgets.QLabel(self, text="Top Level Joint")
        self.tlj_label.setFixedWidth(120)
        self.tlj_textbox = QtWidgets.QLineEdit(self)
        self.tlj_textbox.setPlaceholderText("Top Level Joint Name")
        self.tlj_pickwhip = QtWidgets.QPushButton(self, text="Get from selection")
        self.tlj_pickwhip.clicked.connect(self.tlj_name_pickwhip)


        self.connect_button = QtWidgets.QPushButton(self, text="Connect Skeletons")
        self.connect_button.clicked.connect(self.execute_skeleton_connect)
        self.connect_type_dropdown = QtWidgets.QComboBox(self)
        self.connect_type_dropdown.addItems(["Direct TransRotScale", "Parent Constraint"])

        self.detach_button = QtWidgets.QPushButton(self, text="Detach Skeletons")
        self.detach_button.clicked.connect(self.execute_skeleton_detach)

        # Existing constraint networks panel
        self.existing_constraints = QtWidgets.QListWidget(self)
        self.existing_constraints_label = QtWidgets.QLabel(self, text="Existing Constraint Setups: ")
        # self.existing_constraints.setFixedSize(280, 400)  # Width, Height

        # LAYOUTS
        self.h_layout = QtWidgets.QHBoxLayout()
        self.v_layout = QtWidgets.QVBoxLayout()
        self.existing_constraints_layout = QtWidgets.QVBoxLayout()
        self.container_layout = QtWidgets.QVBoxLayout()

        # textbox layouts
        self.driver_h_layout = QtWidgets.QHBoxLayout()
        self.driver_h_layout.addWidget(self.driver_label)
        self.driver_h_layout.addWidget(self.driver_textbox)
        self.driver_h_layout.addWidget(self.driver_pickwhip)

        self.driven_h_layout = QtWidgets.QHBoxLayout()
        self.driven_h_layout.addWidget(self.driven_label)
        self.driven_h_layout.addWidget(self.driven_textbox)
        self.driven_h_layout.addWidget(self.driven_pickwhip)

        self.tlj_h_layout    = QtWidgets.QHBoxLayout()
        self.tlj_h_layout.addWidget(self.tlj_label)
        self.tlj_h_layout.addWidget(self.tlj_textbox)
        self.tlj_h_layout.addWidget(self.tlj_pickwhip)

        # existing constraints panel
        self.existing_constraints_layout.addWidget(self.existing_constraints_label)
        self.existing_constraints_layout.addWidget(self.existing_constraints)

        self.connect_layout = QtWidgets.QHBoxLayout()
        self.connect_layout.addWidget(self.connect_button)
        self.connect_layout.addWidget(self.connect_type_dropdown)

        # final layout
        self.v_layout.addStretch()
        self.v_layout.addLayout(self.driver_h_layout)
        self.v_layout.addLayout(self.driven_h_layout)
        self.v_layout.addLayout(self.tlj_h_layout)
        self.v_layout.addLayout(self.connect_layout)
        self.v_layout.addWidget(self.detach_button)
        self.v_layout.addStretch()

        self.h_layout.addLayout(self.v_layout)

        self.container_layout.addLayout(self.h_layout)
        self.container_layout.addLayout(self.existing_constraints_layout)

        self.setLayout(self.container_layout)


def run():
    try:
        pass
        #ui.deleteLater()
    except NameError as e:
        pass

    if pm.window("SkeletonConnectorUI_UniqueIdWorkspaceControl", exists=True):
        pm.deleteUI("SkeletonConnectorUI_UniqueIdWorkspaceControl")

    ui = SkeletonConnectorUI()
    ui.show(dockable=True)