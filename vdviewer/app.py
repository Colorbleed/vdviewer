__author__ = "aardschok"

import sys

from maya import cmds

from vendor.Qt import QtWidgets, QtCore

import version
import lib

module = sys.modules[__name__]
module.window = None


class App(QtWidgets.QWidget):
    """Simple view to control content and select VRay Displacement sets"""

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.setWindowTitle("VD Viewer | version %s" % version.current)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

        layout = QtWidgets.QVBoxLayout()

        refresh_button = QtWidgets.QPushButton("Refresh")

        view = QtWidgets.QListWidget()
        view.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        view.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

        layout.addWidget(refresh_button)
        layout.addWidget(view)

        self.view = view
        self.refresh_button = refresh_button

        self.setLayout(layout)
        self.setFixedWidth(300)
        self.setFixedHeight(450)

        self.connections()

        self.refresh()

    def connections(self):
        self.view.doubleClicked.connect(self.on_double_clicked)
        self.view.customContextMenuRequested.connect(self.show_rmb_menu)
        self.refresh_button.clicked.connect(self.refresh)

    def refresh(self):
        self.view.clear()
        self.populate()

    def populate(self):

        # TODO: make pipeline friendly
        data = self.look_up()
        for i, d in enumerate(data):
            # Create item
            item = QtWidgets.QListWidgetItem(d)
            item.setData(i, d)
            self.view.addItem(item)

    def look_up(self):
        return cmds.ls(type="VRayDisplacement")

    def get_indices(self):
        """Get the selected rows"""
        selection_model = self.view.selectionModel()
        return selection_model.selectedRows()

    def build_rmb_menu(self):

        menu = QtWidgets.QMenu(self)

        add_items_action = QtWidgets.QAction("Add Selected", menu)
        add_items_action.triggered.connect(self.on_add_select_item)

        remove_items_action = QtWidgets.QAction("Remove Selected", menu)
        remove_items_action.triggered.connect(self.on_remove_select_item)

        select_contained_action = QtWidgets.QAction("Select Contained", menu)
        select_contained_action.triggered.connect(self.on_select_contained)

        menu.addAction(add_items_action)
        menu.addAction(remove_items_action)
        menu.addSeparator()
        menu.addAction(select_contained_action)

        return menu

    def show_rmb_menu(self, pos):

        idx = self.view.currentIndex()
        if not idx.isValid():
            return

        globalpos = self.view.viewport().mapToGlobal(pos)

        menu = self.build_rmb_menu()
        menu.exec_(globalpos)

    def on_double_clicked(self):
        idx = self.view.currentIndex()
        cmds.select(idx.data(), noExpand=True)

    def on_add_select_item(self):
        idx = self.view.currentIndex()
        vd_node = idx.data()

        cmds.sets(cmds.ls(selection=True), include=vd_node)

    def on_remove_select_item(self):
        idx = self.view.currentIndex()
        vd_node = idx.data()

        cmds.sets(cmds.ls(selection=True), remove=vd_node)

    def on_select_contained(self):
        idx = self.view.currentIndex()
        vd_node = idx.data()

        cmds.select(vd_node)


def show(parent=None):
    try:
        module.window.close()
        del module.window
    except (RuntimeError, AttributeError):
        pass

    with lib.application():
        window = App(parent)
        window.show()

        module.window = window
