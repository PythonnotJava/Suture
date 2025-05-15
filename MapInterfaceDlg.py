import sys
from io import StringIO
from textwrap import dedent

from traceback import format_exc
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

# from qutepart import Qutepart

class _CodeRunnerThread(QThread):
    output_signal = pyqtSignal(str)

    def __init__(self, code : str, base : QWidget | None):
        super().__init__()
        self.code = code
        self.base = base  # 注入底层UI控件，进行交互

    def run(self):
        try:
            stdout_capture = StringIO()
            sys.stdout = stdout_capture  # 重定向标准输出

            local_vars = {"_base": self.base}  # 让代码可以访问 UI 控件
            exec(self.code, globals(), local_vars)  # 执行用户代码

            # 获取 print() 输出的内容
            output = stdout_capture.getvalue()
            result = f"{output}\n代码执行完成"
        except:
            result = f"执行错误:\n{format_exc()}"
        self.output_signal.emit(f"{result}\n=========================================================")  # 发送信号，通知主线程

class _SimpleShell(QTextEdit):
    def __init__(self):
        super().__init__()
        self.setReadOnly(True)

    def contextMenuEvent(self, event : QContextMenuEvent):
        # 获取默认的右键菜单
        menu = self.createStandardContextMenu()

        # 创建新的菜单项
        clearAll = QAction("清屏", self)
        clearAll.triggered.connect(lambda : self.clear())
        menu.addAction(clearAll)

        # 显示菜单
        menu.exec_(event.globalPos())

class MapInterfaceDlg(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.editor = QTextEdit()
        self.simpleShell = _SimpleShell()
        self.splitter = QSplitter()
        self.group = QGroupBox()

        self.thread : _CodeRunnerThread | None = None
        self.base : QWidget | None = parent  # 绑定的可访问的底层控件

        self.setUI()
    def setUI(self) -> None:
        self.setWindowTitle('调试器')
        self.setMinimumSize(400, 600)
        self.editor.setContextMenuPolicy(Qt.CustomContextMenu)
        self.editor.customContextMenuRequested.connect(self.customMenu)

        lay = QVBoxLayout()
        lay.addWidget(self.splitter)
        self.setLayout(lay)
        self.splitter.addWidget(self.editor)
        self.splitter.addWidget(self.group)
        self.splitter.setOrientation(Qt.Vertical)
        self.splitter.setSizes([300, 100])
        self.group.setTitle('输出端')
        inLay = QHBoxLayout()
        inLay.addWidget(self.simpleShell, alignment=Qt.Alignment())
        inLay.setContentsMargins(0, 0, 0, 0)
        self.group.setLayout(inLay)

    def customMenu(self) -> None:
        menu = QMenu(self)
        loadAct = QAction('导入Python文件')
        runAct = QAction('运行')

        loadAct.triggered.connect(self.load_func)
        runAct.triggered.connect(self.run_func)
        menu.addActions([loadAct, runAct])

        menu.exec_(QCursor().pos())

    def load_func(self) -> None:...

    def run_func(self) -> None:
        self.thread = _CodeRunnerThread(self.editor.toPlainText(), self.base)
        self.thread.output_signal.connect(lambda t: self.simpleShell.append(str(t)))
        self.thread.start()
        self.thread.finished.connect(lambda : setattr(self, 'thread', None))

    def register(self, base : QWidget) -> None:
        self.base = base

    def exportWhatsThis(self):
        content = dedent("""\
            *************************调试说明***************************
            内置变量：
                - _base ：默认是控制主界面的控件 AppCore 的实例，注入接 口
            语言支持：
                - Python >= 3.10
            示例（让底层控件动态的抛出一个对话框）：
                ```
                from PyQt5.QtWidgets import QDialog
                
                qw = QDialog(_base)
                qw.setMinimumSize(400, 400)
                qw.setStyleSheet("background-color:red")
                qw.exec_()
                ```
            ***********************************************************
           """)
        self.simpleShell.append(content)
        return True

    def event(self, event : QEvent):
        if event.type() == QEvent.Type.EnterWhatsThisMode:
            return self.exportWhatsThis()
        return super().event(event)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = MapInterfaceDlg()
    ui.show()
    sys.exit(app.exec())