"""

"""

# SYSTEM IMPORTS

# STANDARD LIB IMPORTS
import sys

from PySide2 import QtGui
from PySide2 import QtWidgets
from PySide2 import QtCore
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
import pymel.core as pm
from shiboken2 import wrapInstance
import maya.OpenMayaUI as omui

# LOCAL APP IMPORTS
if sys.version_info.major == 3:
    from . import SkeletonConnectorFunctional
    from importlib import reload
else:
    import SkeletonConnectorFunctional
reload(SkeletonConnectorFunctional)

def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    if sys.version_info.major == 3:
        return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)
    else:
        return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)

class SkeletonConnectorUI(MayaQWidgetDockableMixin, QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super(SkeletonConnectorUI, self).__init__()
        self.create_widget()
        self.populate_constraint_list()

    def execte_skeleton_connect(self):
        reload(SkeletonConnectorFunctional)
        SkeletonConnectorFunctional.skeleton_attach(
            rig_ns=self.driver_textbox.text(),
            groom_ns=self.driven_textbox.text(),
            top_level_joint=self.tlj_textbox.text()
        )
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
        constraint_data = SkeletonConnectorFunctional.load_scene_constraint_data()
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
        self.connect_button.clicked.connect(self.execte_skeleton_connect)

        # TODO Save constrained skeletons per scene
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

        # final layout
        self.v_layout.addStretch()
        self.v_layout.addLayout(self.driver_h_layout)
        self.v_layout.addLayout(self.driven_h_layout)
        self.v_layout.addLayout(self.tlj_h_layout)
        self.v_layout.addWidget(self.connect_button)
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
