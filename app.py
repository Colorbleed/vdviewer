__author__ = "aardschok"

from maya import cmds

from avalon.vendor.Qt import QtWidgets, QtCore

import version


class App(QtWidgets.QWidget):
    """Simple view to control content and select VRay Displacement sets"""

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.setWindowTitle("VD Viewer | version %s" % version.current)
        layout = QtWidgets.QVBoxLayout()

        view = QtWidgets.QListWidget()
        view.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        view.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

        layout.addWidget(view)

        self.view = view

        self.setLayout(layout)
        self.resize(300, 450)

        self.connections()

        self.refresh()

    def connections(self):
        self.view.doubleClicked.connect(self.on_double_clicked)
        self.view.customContextMenuRequested.connect(self.show_rmb_menu)

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

        menu.addAction(add_items_action)
        menu.addAction(remove_items_action)

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
