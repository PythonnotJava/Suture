# 工具栏

import sys

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from qtawesome import icon as QAwesomeIcon

class MapToolBar(QToolBar):

    send = pyqtSignal(str)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.setUI()

    def setUI(self) -> None:
        self.setAllowedAreas(Qt.LeftToolBarArea | Qt.RightToolBarArea | Qt.TopToolBarArea)

        load_map = QAction(QAwesomeIcon('ei.folder-open'), '导入地图', self)
        export_map = QAction(QAwesomeIcon('fa5s.file-export'), '导出地图', self)
        gas_source = QAction(QAwesomeIcon('fa5s.gas-pump'), '添加气源', self)
        user_agent = QAction(QAwesomeIcon('fa5.user-circle'), '添加用户', self)
        pipe_link = QAction(QAwesomeIcon('mdi6.pipe'), '供应管线', self)
        clear_all = QAction(QAwesomeIcon('mdi6.map-marker-remove-outline'), '清场', self)
        inject_api = QAction(QAwesomeIcon('fa5s.syringe'), '注入', self)
        update_scene = QAction(QAwesomeIcon('mdi6.update'), '刷新', self)
        develop_act = QAction(QAwesomeIcon('fa5b.connectdevelop'), '开发', self)

        # 先不考虑点了gas又点user的锁冲突问题
        gas_source.triggered.connect(lambda : self.send.emit('gas'))
        user_agent.triggered.connect(lambda : self.send.emit('user'))
        pipe_link.triggered.connect(lambda : self.send.emit('pipe'))
        load_map.triggered.connect(lambda : self.send.emit('load'))
        export_map.triggered.connect(lambda : self.send.emit('export'))
        inject_api.triggered.connect(lambda : self.send.emit('inject'))
        clear_all.triggered.connect(lambda : self.send.emit('clear'))
        update_scene.triggered.connect(lambda : self.send.emit('update'))
        develop_act.triggered.connect(lambda : self.send.emit('dev'))

        self.addActions([load_map, export_map, gas_source, user_agent, pipe_link, clear_all, update_scene, inject_api, develop_act])

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = MapToolBar()
    ui.show()
    sys.exit(app.exec())