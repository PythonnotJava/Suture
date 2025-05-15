# 软件主体

import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from qt_material import list_themes, apply_stylesheet

from MatToolBar import MapToolBar
from MapAttributeWidget import MapAttributeWidget
from MapScene import MapScene
from MapView import MapView
from MapInterfaceDlg import MapInterfaceDlg
from MapStatusBar import MapStatusBar

class AppCore(QMainWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.mapAttributeWidget = MapAttributeWidget()
        self.mapView = MapView()
        self.mapScene = MapScene(self.mapAttributeWidget, self.mapView.viewport())
        self.mapView.setScene(self.mapScene)
        self.mapToolBar = MapToolBar()
        self.mapStatusBar = MapStatusBar(self)

        self.setUI()

    def setUI(self) -> None:
        self.addToolBar(self.mapToolBar)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.mapAttributeWidget)
        self.setCentralWidget(self.mapView)
        self.setStatusBar(self.mapStatusBar)

        self.mapToolBar.send.connect(self.mapScene.handle_toolbar_scene)
        self.mapScene.interfaceRequest.connect(self.call_interface_dlg)
        self.mapScene.callStatus.connect(lambda t : self.mapStatusBar.showMessage(t, 2500))

    def contextMenuEvent(self, event : QContextMenuEvent):
        """禁用右键菜单"""
        event.ignore()  # 不显示任何菜单

    def call_interface_dlg(self) -> None:
        dlg = MapInterfaceDlg(self)
        dlg.exec_()

    def closeEvent(self, a0):
        super().closeEvent(a0)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setApplicationName('天然气管网供气可靠性仿真')
    app.setWindowIcon(QIcon('src/logo.png'))
    apply_stylesheet(app, theme=list_themes()[13])
    ui = AppCore()
    ui.setMinimumSize(800, 600)
    ui.show()
    sys.exit(app.exec())