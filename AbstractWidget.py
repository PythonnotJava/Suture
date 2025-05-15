
# 定义setAccessibleDescription()
#
# 定义setAccessibleName()

# 定义setAutoFillBackground()
#
# 定义setBackgroundRole()
#
# 定义setContentsMargins()
#
# 定义setContextMenuPolicy()
#
# 定义setFocus()
#
# 定义setFocusPolicy()
#
# 定义setFocusProxy()
#
# 定义setForegroundRole()
#
# 定义setInputMethodHints()
#
# 定义setLayoutDirection()

# 定义setMouseTracking()
#
# 定义setPalette()
#
# 定义setScreen()
#
# 定义setShortcutAutoRepeat()
#
# 定义setShortcutEnabled()
#
# 定义setSizeIncrement()
#
# 定义setSizePolicy()
#
# 定义setStatusTip()
#
# 定义setStyle()
#
# 定义setTabletTracking()
#
# 定义setToolTipDuration()
#
# 定义setUpdatesEnabled()
#
# 定义setWhatsThis()
#
# 定义setWindowFilePath()

# 定义setWindowModality()
#
# 定义setWindowRole()
#
# 定义setWindowState()
from dataclasses import dataclass
from typing import Optional, Iterable, Callable, Union, Literal

from PyQt5.QtCore import QLocale, QObject, Qt, QMargins
from PyQt5.QtGui import QIcon, QFont, QBitmap, QRegion, QCursor, QPixmap, QGuiApplication
from PyQt5.QtWidgets import QWidget, QLayout, QGraphicsEffect, QHBoxLayout, QVBoxLayout, QApplication

# 用于抽象基类的声明布局
@dataclass
class WidgetOrLayoutType:
    dtype: Literal[0, 1]
    obj: Union[QLayout, QWidget]
    align: Qt.Alignment | Qt.AlignmentFlag = Qt.Alignment()

# 抽象基类
class AbstractWidget(QWidget):
    def __init__(self,
                 *,
                 parent: Optional[QWidget] = None,
                 mainLay: Optional[QLayout] = None,
                 objectName : Optional[str] = None,
                 x: Optional[int] = 0,
                 y: Optional[int] = 0,
                 w: Optional[int] = 0,
                 h: Optional[int] = 0,
                 fixSize: Optional[Iterable] = None,
                 rect: Optional[Iterable] = None,
                 minw: Optional[int] = 0,
                 minh: Optional[int] = 0,
                 maxw: Optional[int] = 0,
                 maxh: Optional[int] = 0,
                 font: Optional[QFont] = None,
                 tips: Optional[str] = None,
                 cursor: str | Qt.CursorShape = None,
                 winIcon : str | QIcon = None,
                 iconText : Optional[str] = None,
                 winTitle : Optional[str] = None,
                 attribute : Optional[Qt.WidgetAttribute] = None,
                 mask : QBitmap | QRegion = None,
                 flags : Union[Qt.WindowFlags, Qt.WindowType, None] = None,
                 opacity : float = 1.0,
                 locale : Optional[QLocale] = None,
                 acceptDrops : bool = False,
                 effect : Optional[QGraphicsEffect] = None,
                 qss : Optional[str] = None
                 ):
        super().__init__(parent=parent)

        self.setWindowOpacity(opacity)
        self.setAcceptDrops(acceptDrops)

        if mainLay:
            self.setLayout(mainLay)

        if objectName:
            self.setObjectName(objectName)

        if x and y:
            self.move(x, y)

        if h and w:
            self.resize(w, h)

        if fixSize:
            self.setFixedSize(*fixSize)

        if rect:
            self.setGeometry(*rect)

        if minw:
            self.setMinimumWidth(minw)

        if maxw:
            self.setMaximumWidth(maxw)

        if minh:
            self.setMinimumHeight(minh)

        if maxh:
            self.setMaximumHeight(maxh)

        if font:
            self.setFont(font)

        if tips:
            self.setToolTip(tips)

        if cursor:
            self.setCursor(QCursor(QPixmap(cursor)) if isinstance(cursor, str) else cursor)

        if winIcon:
            self.setWindowIcon(winIcon if isinstance(winIcon, QIcon) else QIcon(winIcon))

        if iconText:
            self.setWindowIconText(iconText)

        if winTitle:
            self.setWindowTitle(winTitle)

        if attribute:
            self.setAttribute(attribute)

        if mask:
            self.setMask(mask)

        if flags:
            self.setWindowFlags(flags)

        if locale:
            self.setLocale(locale)

        if effect:
            self.setGraphicsEffect(effect)

        if qss:
            self.setStyleSheet(qss)

    @classmethod
    def factoryConstructor(cls, **kwargs): return cls(**kwargs)

    @classmethod
    def layoutConstructor(cls,
                          widgets_lays : Iterable[WidgetOrLayoutType],
                          hbox: bool = True,
                          stretch : int = 1,
                          **kwargs):
        if hbox:
            Box = QHBoxLayout()
        else:
            Box = QVBoxLayout()
        for wl in widgets_lays:
            if wl.dtype == 0:  # 0表示布局、1表示控件
                Box.addLayout(wl.obj, stretch)
            elif wl.dtype == 1:
                Box.addWidget(wl.obj, stretch, alignment=wl.align if wl.align is not None else Qt.Alignment())
            else:
                pass

        return cls(mainLay=Box, **kwargs)

    def selfLayoutConstructor(self,
                              widgets_lays : Iterable[WidgetOrLayoutType],
                              hbox: bool = True,
                              stretch : int = 1
                              ) -> 'AbstractWidget':
        if hbox:
            Box = QHBoxLayout()
        else:
            Box = QVBoxLayout()
        for wl in widgets_lays:
            if wl.dtype == 0:  # 0表示布局、1表示控件
                Box.addLayout(wl.obj, stretch)
            elif wl.dtype == 1:
                Box.addWidget(wl.obj, stretch, alignment=wl.align if wl.align is not None else Qt.Alignment())
            else:
                pass
        self.setLayout(Box)

        return self

    def setUniqueWidget(
            self,
            widget : QObject,
            hbox : bool = True,
            align : Union[Qt.Alignment, Qt.AlignmentFlag] = Qt.Alignment(),
            contentMargins : Optional[Union[QMargins, Iterable]] = None,
            stretch : int = 1
    ) -> None:
        Box = QHBoxLayout() if hbox else QVBoxLayout()
        Box.addWidget(widget, stretch, align)
        if contentMargins:
            Box.setContentsMargins(
                contentMargins if isinstance(contentMargins, QMargins) else QMargins(*contentMargins)
            )
        self.setLayout(Box)

    # 更新自己
    def updateSelf(self, **kwargs) -> 'AbstractWidget':
        if 'opacity' in kwargs:
            self.setWindowOpacity(kwargs['opacity'])
        if 'acceptDrops' in kwargs:
            self.setAcceptDrops(kwargs['acceptDrops'])
        if 'mainLay' in kwargs:
            self.setLayout(kwargs['mainLay'])
        if 'objectName' in kwargs:
            self.setObjectName(kwargs['objectName'])
        if 'x' in kwargs and 'y' in kwargs:
            self.move(kwargs['x'], kwargs['y'])
        if 'w' in kwargs and 'h' in kwargs:
            self.resize(kwargs['w'], kwargs['h'])
        if 'fixSize' in kwargs:
            self.setFixedSize(*kwargs['fixSize'])
        if 'rect' in kwargs:
            self.setGeometry(*kwargs['rect'])
        if 'minw' in kwargs:
            self.setMinimumWidth(kwargs['minw'])
        if 'maxw' in kwargs:
            self.setMaximumWidth(kwargs['maxw'])
        if 'minh' in kwargs:
            self.setMinimumHeight(kwargs['minh'])
        if 'maxh' in kwargs:
            self.setMaximumHeight(kwargs['maxh'])
        if 'font' in kwargs:
            self.setFont(kwargs['font'])
        if 'tips' in kwargs:
            self.setToolTip(kwargs['tips'])
        if 'cursor' in kwargs:
            cursor = kwargs['cursor']
            self.setCursor(QCursor(QPixmap(cursor)) if isinstance(cursor, str) else cursor)
        if 'winIcon' in kwargs:
            winIcon = kwargs['winIcon']
            self.setWindowIcon(winIcon if isinstance(winIcon, QIcon) else QIcon(winIcon))
        if 'iconText' in kwargs:
            self.setWindowIconText(kwargs['iconText'])
        if 'winTitle' in kwargs:
            self.setWindowTitle(kwargs['winTitle'])
        if 'attribute' in kwargs:
            self.setAttribute(kwargs['attribute'])
        if 'mask' in kwargs:
            self.setMask(kwargs['mask'])
        if 'flags' in kwargs:
            self.setWindowFlags(kwargs['flags'])
        if 'locale' in kwargs:
            self.setLocale(kwargs['locale'])
        if 'effect' in kwargs:
            self.setGraphicsEffect(kwargs['effect'])
        if 'qss' in kwargs:
            self.setStyleSheet(kwargs['qss'])

        return self

    # 自返回的实现
    def __call__(self, funcLike : Union[Callable, str], *args, **kwargs) -> 'AbstractWidget':
        # funcLike可以是直接函数，也可以是类域内的函数，需要传入函数名字去寻找，默认是有这个函数的，不做判断
        func: Callable = getattr(self, funcLike) if isinstance(funcLike, str) else funcLike
        value = func(*args, **kwargs)
        # @better 有返回值就打印，这里完全可以再传入一个函数参数，用于操作这个value
        print(value)
        return self

