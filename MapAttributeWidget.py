import sys

from PyQt5.QtCore import *
from PyQt5.QtWidgets import  *
from PyQt5.QtGui import *

from MapProxyItemWidget import NodeAttr
from MapPipeProxy import PipeAttr

class MapAttributeWidget(QDockWidget):
    def __init__(self, **kwargs):
        super().__init__("属性面板", **kwargs)

        self.treeWidget = QTreeWidget()

        self.setUI()

    def setUI(self) -> None:
        self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.setWidget(self.treeWidget)

        self.treeWidget.setHeaderLabels(["属性", "值"])
        self.treeWidget.addTopLevelItem(QTreeWidgetItem(['未知', '']))

    def setCurrentNodeAttr(self, nodeAttr : NodeAttr) -> None:
        self.treeWidget.clear()
        match nodeAttr.category:
            case 'Unknow':
                self.treeWidget.addTopLevelItem(QTreeWidgetItem(['类型', 'Unknow']))
            case 'Gas':
                self.treeWidget.addTopLevelItems([
                    QTreeWidgetItem(['类型', '气源']),
                    QTreeWidgetItem(['X', str(nodeAttr.x)]),
                    QTreeWidgetItem(['Y', str(nodeAttr.y)]),
                    QTreeWidgetItem(['储藏量', str(nodeAttr.currentGasSource)]),
                    QTreeWidgetItem(['失效率', str(nodeAttr.errorp)])
                ])
            case 'User':
                self.treeWidget.addTopLevelItems([
                    QTreeWidgetItem(['类型', '用户']),
                    QTreeWidgetItem(['X', str(nodeAttr.x)]),
                    QTreeWidgetItem(['Y', str(nodeAttr.y)]),
                    QTreeWidgetItem(['储藏量', str(nodeAttr.currentGasUser)]),
                ])

    def setCurrentPipeAttr(self, pipeAttr : PipeAttr) -> None:
        self.treeWidget.clear()
        self.treeWidget.addTopLevelItems([
            QTreeWidgetItem(['类型', '管道']),
            QTreeWidgetItem(['端点A', f'({pipeAttr.ax}, {pipeAttr.ay})']),
            QTreeWidgetItem(['端点B', f'({pipeAttr.bx}, {pipeAttr.by})']),
            QTreeWidgetItem(['距离', str(pipeAttr.distance)]),
            QTreeWidgetItem(['失效率', str(pipeAttr.errorp)]),
        ])

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = MapAttributeWidget()
    ui.show()
    sys.exit(app.exec())
