from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget
from qtsymbols import *
import os, functools, uuid, threading, shutil, time
from traceback import print_exc
import gobject
from myutils.config import (
    savehook_new_list,
    savehook_new_data,
    savegametaged,
    uid2gamepath,
    extradatas,
    globalconfig,
)
from myutils.wrapper import Singleton_close
from myutils.utils import str2rgba, get_time_stamp, loopbackrecorder
from myutils.audioplayer import playonce
from gui.inputdialog import autoinitdialog
from gui.specialwidget import stackedlist, shrinkableitem
from gui.usefulwidget import (
    pixmapviewer,
    statusbutton,
    Prompt_dialog,
    getsimplecombobox,
    getspinbox,
    getcolorbutton,
    makesubtab_lazy,
    tabadd_lazy,
    getsimpleswitch,
    getspinbox,
    selectcolor,
    listediter,
)
from gui.dialog_savedgame_setting import (
    dialog_setting_game_internal,
)
from gui.dialog_savedgame_common import (
    getalistname,
    startgamecheck,
    getreflist,
    calculatetagidx,
    opendirforgameuid,
    getcachedimage,
    getpixfunction,
    dialog_syssetting,
    addgamesingle,
    addgamebatch,
)
from gui.dynalang import (
    LFormLayout,
    LPushButton,
    LDialog,
    LAction,
    LLabel,
)


@Singleton_close
class dialog_syssetting(LDialog):

    def __init__(self, parent, type_=1) -> None:
        super().__init__(parent, Qt.WindowType.WindowCloseButtonHint)
        self.setWindowTitle("其他设置")
        formLayout = LFormLayout(self)

        formLayout.addRow(
            "隐藏不存在的游戏",
            getsimpleswitch(globalconfig, "hide_not_exists"),
        )
        if type_ == 1:
            for key, name in [
                ("itemw", "宽度"),
                ("itemh", "高度"),
                # ("imgw", "图片宽度"),
                # ("imgh", "图片高度"),
                ("margin", "边距"),
                ("textH", "文字区高度"),
            ]:
                formLayout.addRow(
                    name,
                    getspinbox(0, 1000, globalconfig["dialog_savegame_layout"], key),
                )
        elif type_ == 2:
            for key, name in [
                ("listitemheight", "文字区高度"),
                ("listitemwidth", "高度"),
            ]:
                formLayout.addRow(
                    name,
                    getspinbox(0, 1000, globalconfig["dialog_savegame_layout"], key),
                )

        for key, key2, name in [
            ("backcolor1", "transparent", "颜色"),
            ("onselectcolor1", "transparentselect", "选中时颜色"),
            ("onfilenoexistscolor1", "transparentnotexits", "游戏不存在时颜色"),
        ]:
            formLayout.addRow(
                name,
                getcolorbutton(
                    globalconfig["dialog_savegame_layout"],
                    key,
                    callback=functools.partial(
                        selectcolor,
                        self,
                        globalconfig["dialog_savegame_layout"],
                        key,
                        None,
                        self,
                        key,
                    ),
                    name=key,
                    parent=self,
                ),
            )
            formLayout.addRow(
                name + "_" + "不透明度",
                getspinbox(0, 100, globalconfig["dialog_savegame_layout"], key2),
            )
        if type_ == 1:
            formLayout.addRow(
                "缩放",
                getsimplecombobox(
                    ["填充", "适应", "拉伸", "居中"],
                    globalconfig,
                    "imagewrapmode",
                ),
            )
        formLayout.addRow(
            "启动游戏不修改顺序",
            getsimpleswitch(globalconfig, "startgamenototop"),
        )

        if type_ == 1:
            formLayout.addRow(
                "显示标题",
                getsimpleswitch(globalconfig, "showgametitle"),
            )
        self.show()


class clickitem(QWidget):
    focuschanged = pyqtSignal(bool, str)
    doubleclicked = pyqtSignal(str)
    globallashfocus = None

    @classmethod
    def clearfocus(cls):
        try:  # 可能已被删除
            if clickitem.globallashfocus:
                clickitem.globallashfocus.focusOut()
        except:
            pass
        clickitem.globallashfocus = None

    def mouseDoubleClickEvent(self, e):
        self.doubleclicked.emit(self.uid)

    def click(self):
        try:
            self.bottommask.setStyleSheet(
                f'background-color: {str2rgba(globalconfig["dialog_savegame_layout"]["onselectcolor1"],globalconfig["dialog_savegame_layout"]["transparentselect"])};'
            )
            if self != clickitem.globallashfocus:
                clickitem.clearfocus()
            clickitem.globallashfocus = self
            self.focuschanged.emit(True, self.uid)
        except:
            print_exc()

    def mousePressEvent(self, ev) -> None:
        self.click()

    def focusOut(self):
        self.bottommask.setStyleSheet("background-color: rgba(255,255,255, 0);")
        self.focuschanged.emit(False, self.uid)

    def resizeEvent(self, a0: QResizeEvent) -> None:
        self.bottommask.resize(a0.size())
        self.maskshowfileexists.resize(a0.size())
        self.bottomline.resize(a0.size())

    def __init__(self, uid):
        super().__init__()

        self.uid = uid
        self.lay = QHBoxLayout()
        self.lay.setSpacing(0)
        self.lay.setContentsMargins(0, 0, 0, 0)

        self.maskshowfileexists = QLabel(self)

        c = globalconfig["dialog_savegame_layout"][
            ("onfilenoexistscolor1", "backcolor1")[os.path.exists(uid2gamepath[uid])]
        ]
        c = str2rgba(
            c,
            globalconfig["dialog_savegame_layout"][
                ("transparentnotexits", "transparent")[
                    os.path.exists(uid2gamepath[uid])
                ]
            ],
        )
        self.maskshowfileexists.setStyleSheet(f"background-color:{c};")
        self.bottommask = QLabel(self)
        self.bottommask.setStyleSheet("background-color: rgba(255,255,255, 0);")
        _ = QLabel(self)
        _.setStyleSheet(
            """background-color: rgba(255,255,255, 0);border-bottom: 1px solid gray;"""
        )
        self.bottomline = _
        size = globalconfig["dialog_savegame_layout"]["listitemheight"]
        _ = QLabel()
        _.setFixedSize(QSize(size, size))
        _.setScaledContents(True)
        _.setStyleSheet("background-color: rgba(255,255,255, 0);")
        icon = getpixfunction(
            uid, small=True
        )  # getExeIcon(uid2gamepath[uid], icon=False, cache=True)
        icon.setDevicePixelRatio(self.devicePixelRatioF())
        _.setPixmap(icon)
        self.lay.addWidget(_)
        _ = QLabel(savehook_new_data[uid]["title"])
        _.setWordWrap(True)
        _.setFixedHeight(size + 1)
        self.lay.addWidget(_)
        self.setLayout(self.lay)
        _.setStyleSheet("""background-color: rgba(255,255,255, 0);""")


class fadeoutlabel(QLabel):
    def __init__(self, p=None):
        super().__init__(p)

        effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(effect)

        self.setStyleSheet("""background-color: rgba(255,255,255, 0);""")
        self.animation = QPropertyAnimation(effect, b"opacity")
        self.animation.setDuration(4000)
        self.animation.setStartValue(1.0)
        self.animation.setEndValue(0.0)
        self.animation.setDirection(QPropertyAnimation.Direction.Forward)

    def setText(self, t):
        super().setText(t)
        self.animation.stop()
        self.animation.start()


class XQListWidget(QListWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

    def sethor(self, hor):
        if hor:
            self.setFlow(QListWidget.LeftToRight)
            self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            self.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
            self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        else:
            self.setFlow(QListWidget.TopToBottom)
            self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            self.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)


def getselectpos(parent, callback):
    __d = {"k": 0}
    __vis, __uid = ["下", "右", "上", "左"], [0, 1, 2, 3]

    def __wrap(callback, __d, __uid):
        if len(__uid) == 0:
            return

        uid = __uid[__d["k"]]
        callback(uid)

    if len(__uid) > 1:
        autoinitdialog(
            parent,
            "位置",
            600,
            [
                {
                    "type": "combo",
                    "name": "位置",
                    "d": __d,
                    "k": "k",
                    "list": __vis,
                },
                {
                    "type": "okcancel",
                    "callback": functools.partial(__wrap, callback, __d, __uid),
                },
            ],
        )
    else:
        callback(__uid[0])


class previewimages(QWidget):
    changepixmappath = pyqtSignal(str)
    removepath = pyqtSignal(str)

    def sethor(self, hor):
        self.hor = hor
        self.list.sethor(hor)

        if self.hor:
            self.list.setIconSize(QSize(self.height(), self.height()))
        else:
            self.list.setIconSize(QSize(self.width(), self.width()))

    def sizeHint(self):
        return QSize(100, 100)

    def __init__(self, p) -> None:
        super().__init__(p)
        self.lay = QHBoxLayout()
        self.lay.setContentsMargins(0, 0, 0, 0)
        self.list = XQListWidget(self)
        self.list.currentRowChanged.connect(self._visidx)
        self.lay.addWidget(self.list)
        self.setLayout(self.lay)

    def tolastnext(self, dx):
        if self.list.count() == 0:
            return self.list.setCurrentRow(-1)
        self.list.setCurrentRow((self.list.currentRow() + dx) % self.list.count())

    def setpixmaps(self, paths, currentpath):
        self.list.setCurrentRow(-1)
        self.list.blockSignals(True)
        self.list.clear()
        pathx = []
        for path in paths:
            image = getcachedimage(path, True)
            if image is None:
                continue
            item = QListWidgetItem()
            item.imagepath = path
            pathx.append(path)
            item.setIcon(QIcon(image))

            self.list.addItem(item)
        self.list.blockSignals(False)
        pixmapi = 0
        if currentpath in pathx:
            pixmapi = pathx.index(currentpath)
        self.list.setCurrentRow(pixmapi)

    def _visidx(self, _):
        item = self.list.currentItem()
        if item is None:
            pixmap_ = None
        else:
            pixmap_ = item.imagepath
        self.changepixmappath.emit(pixmap_)

    def removecurrent(self, delfile):
        idx = self.list.currentRow()
        item = self.list.currentItem()
        if item is None:
            return
        path = item.imagepath
        self.removepath.emit(path)
        self.list.takeItem(idx)
        if delfile:
            try:
                os.remove(path)
            except:
                pass

    def resizeEvent(self, e: QResizeEvent):
        if self.hor:
            self.list.setIconSize(QSize(self.height(), self.height()))
        else:
            self.list.setIconSize(QSize(self.width(), self.width()))
        return super().resizeEvent(e)


class hoverbtn(LLabel):
    clicked = pyqtSignal()

    def mousePressEvent(self, a0: QMouseEvent) -> None:
        self.clicked.emit()
        return super().mousePressEvent(a0)

    def __init__(self, *argc):
        super().__init__(*argc)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def resizeEvent(self, e):
        style = r"""QLabel{
                background: transparent; 
                border-radius:0;
                font-size: %spx;
                color:transparent; 
            }
            QLabel:hover{
                background-color: rgba(255,255,255,0.5); 
                color:black;
            }""" % (
            min(self.height(), self.width()) // 3
        )
        self.setStyleSheet(style)
        super().resizeEvent(e)


class viewpixmap_x(QWidget):
    tolastnext = pyqtSignal(int)
    startgame = pyqtSignal()
    switchstop = pyqtSignal()

    def sizeHint(self):
        return QSize(400, 400)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.pixmapviewer = pixmapviewer(self)
        self.leftclick = hoverbtn("<-", self)
        self.rightclick = hoverbtn("->", self)
        self.maybehavecomment = hoverbtn(self)
        self.bottombtn = hoverbtn("开始游戏", self)
        self.bottombtn.clicked.connect(self.startgame)
        self.leftclick.clicked.connect(lambda: self.tolastnext.emit(-1))
        self.rightclick.clicked.connect(lambda: self.tolastnext.emit(1))
        self.maybehavecomment.clicked.connect(self.viscomment)
        self.commentedit = QPlainTextEdit(self)
        self.commentedit.textChanged.connect(self.changecommit)
        self.timenothide = QLabel(self)
        self.timenothide.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pathandopen = QPushButton(self)
        self.pathandopen.clicked.connect(
            lambda: (
                os.startfile(os.path.abspath(self.currentimage))
                if self.currentimage
                else ""
            )
        )
        self.centerwidget = QWidget(self)
        self.centerwidgetlayout = QVBoxLayout()
        audio = QHBoxLayout()
        self.recordbtn = statusbutton(
            icons=["fa.microphone", "fa.stop"], colors=["", ""]
        )
        self.recordbtn.statuschanged.connect(self.startorendrecord)
        self.centerwidget.setLayout(self.centerwidgetlayout)
        self.centerwidgetlayout.addWidget(self.timenothide)
        self.centerwidgetlayout.addWidget(self.pathandopen)
        self.centerwidgetlayout.addWidget(self.commentedit)
        self.centerwidgetlayout.addLayout(audio)
        audio.addWidget(self.recordbtn)
        self.btnplay = statusbutton(icons=["fa.play", "fa.stop"], colors=["", ""])
        audio.addWidget(self.btnplay)
        self.btnplay.statuschanged.connect(self.playorstop)
        gobject.baseobject.hualang_recordbtn = self.recordbtn
        self.centerwidget.setVisible(False)
        self.pathview = fadeoutlabel(self)
        self.infoview = fadeoutlabel(self)
        self.infoview.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.currentimage = None
        self.play_context = None
        self.recorder = None
        self.switchstop.connect(self.switchstop_f)

    def switchstop_f(self):
        if self.play_context:
            self.btnplay.click()

    def checkplayable(self):
        if not self.currentimage:
            return False
        mp3 = extradatas.get("imagerefmp3", {}).get(self.currentimage, None)
        if mp3 is None:
            return False
        if not os.path.exists(mp3):
            return False
        return True

    def playorstop(self, idx):
        if not self.checkplayable():
            return
        mp3 = extradatas["imagerefmp3"][self.currentimage]
        if idx == 1:
            self.play_context = playonce(mp3, globalconfig["ttscommon"]["volume"])
            self.sigtime = time.time()

            def __(tm):
                while self.play_context and self.play_context.isplaying:
                    time.sleep(1)
                if self.sigtime == tm:
                    self.switchstop.emit()

            threading.Thread(target=__, args=(self.sigtime,)).start()
        else:
            if not self.play_context:
                return
            self.play_context = None

    def startorendrecord(self, idx):
        if idx == 1:
            if self.play_context:
                self.btnplay.click()
            self.btnplay.setEnabled(False)
            self.recorder = loopbackrecorder()
        else:
            self.btnplay.setEnabled(False)

            def _cb(image, path):
                if not image:
                    return
                tgt = image + os.path.splitext(path)[1]
                shutil.copy(path, tgt)
                if "imagerefmp3" not in extradatas:
                    extradatas["imagerefmp3"] = {}
                extradatas["imagerefmp3"][image] = tgt

                self.btnplay.setEnabled(self.checkplayable())

            if not self.recorder:
                return
            self.recorder.end(callback=functools.partial(_cb, self.currentimage))
            self.recorder = None

    def changecommit(self):
        if "imagecomment" not in extradatas:
            extradatas["imagecomment"] = {}
        extradatas["imagecomment"][self.currentimage] = self.commentedit.toPlainText()

    def viscomment(self):
        self.centerwidget.setVisible(not self.centerwidget.isVisible())

    def resizeEvent(self, e: QResizeEvent):
        self.pixmapviewer.resize(e.size())
        self.pathview.resize(e.size().width(), self.pathview.height())
        self.infoview.resize(e.size().width(), self.infoview.height())
        self.leftclick.setGeometry(
            0, e.size().height() // 5, e.size().width() // 5, 3 * e.size().height() // 5
        )
        self.bottombtn.setGeometry(
            e.size().width() // 5,
            4 * e.size().height() // 5,
            3 * e.size().width() // 5,
            e.size().height() // 5,
        )
        self.rightclick.setGeometry(
            4 * e.size().width() // 5,
            e.size().height() // 5,
            e.size().width() // 5,
            3 * e.size().height() // 5,
        )
        self.maybehavecomment.setGeometry(
            e.size().width() // 5, 0, 3 * e.size().width() // 5, e.size().height() // 5
        )
        self.centerwidget.setGeometry(
            e.size().width() // 5,
            e.size().height() // 5,
            3 * e.size().width() // 5,
            3 * e.size().height() // 5,
        )
        super().resizeEvent(e)

    def changepixmappath(self, path):
        if self.recorder:
            self.recordbtn.click()
        if self.play_context:
            self.btnplay.click()

        self.currentimage = path
        self.centerwidget.setVisible(False)
        self.pathandopen.setText(path)
        self.pathview.setText(path)
        try:
            timestamp = get_time_stamp(ct=os.path.getctime(path), ms=False)
        except:
            timestamp = None
        self.infoview.setText(timestamp)
        self.commentedit.setPlainText(extradatas.get("imagecomment", {}).get(path, ""))
        self.timenothide.setText(timestamp)
        if not path:
            pixmap = QPixmap()
        else:
            pixmap = QPixmap.fromImage(QImage(path))
            if pixmap is None or pixmap.isNull():
                pixmap = QPixmap()
        self.pixmapviewer.showpixmap(pixmap)
        self.btnplay.setEnabled(self.checkplayable())


class pixwrapper(QWidget):
    startgame = pyqtSignal()

    def setrank(self, rank):
        if rank:
            self.spliter.addWidget(self.pixview)
            self.spliter.addWidget(self.previewimages)
        else:
            self.spliter.addWidget(self.previewimages)
            self.spliter.addWidget(self.pixview)

    def sethor(self, hor):
        if hor:

            self.spliter.setOrientation(Qt.Orientation.Vertical)
        else:

            self.spliter.setOrientation(Qt.Orientation.Horizontal)
        self.previewimages.sethor(hor)

    def __init__(self) -> None:
        super().__init__()
        rank = (globalconfig["viewlistpos"] // 2) == 0
        hor = (globalconfig["viewlistpos"] % 2) == 0

        self.previewimages = previewimages(self)
        self.vlayout = QVBoxLayout(self)
        self.vlayout.setContentsMargins(0, 0, 0, 0)
        self.pixview = viewpixmap_x(self)
        self.pixview.startgame.connect(self.startgame)
        self.spliter = QSplitter(self)
        self.vlayout.addWidget(self.spliter)
        self.setrank(rank)
        self.sethor(hor)
        self.pixview.tolastnext.connect(self.previewimages.tolastnext)
        self.setLayout(self.vlayout)
        self.previewimages.changepixmappath.connect(self.changepixmappath)
        self.previewimages.removepath.connect(self.removepath)
        self.k = None
        self.removecurrent = self.previewimages.removecurrent

        self.previewimages.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.previewimages.customContextMenuRequested.connect(
            functools.partial(self.menu, True)
        )
        self.pixview.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.pixview.customContextMenuRequested.connect(
            functools.partial(self.menu, False)
        )

    def menu(self, _1, _):
        menu = QMenu(self)

        setimage = LAction(("设为封面"))
        deleteimage = LAction(("删除图片"))
        deleteimage_x = LAction(("删除图片文件"))
        hualang = LAction(("画廊"))
        pos = LAction(("位置"))

        menu.addAction(setimage)
        menu.addAction(deleteimage)
        menu.addAction(deleteimage_x)
        menu.addAction(hualang)
        if _1:
            menu.addSeparator()
            menu.addAction(pos)
        action = menu.exec(QCursor.pos())
        if action == deleteimage:
            self.removecurrent(False)
        elif action == deleteimage_x:
            self.removecurrent(True)
        elif action == pos:
            getselectpos(self, self.switchpos)

        elif action == hualang:
            listediter(
                self,
                ("画廊"),
                ("画廊"),
                savehook_new_data[self.k]["imagepath_all"],
                closecallback=lambda: self.setpix(self.k),
                ispathsedit=dict(),
            )
        elif action == setimage:
            curr = savehook_new_data[self.k]["currentvisimage"]
            savehook_new_data[self.k]["currentmainimage"] = curr

    def switchpos(self, pos):
        globalconfig["viewlistpos"] = pos
        rank = (globalconfig["viewlistpos"] // 2) == 0
        hor = (globalconfig["viewlistpos"] % 2) == 0
        self.setrank(rank)
        self.sethor(hor)

    def removepath(self, path):
        lst = savehook_new_data[self.k]["imagepath_all"]
        lst.pop(lst.index(path))

    def changepixmappath(self, path):
        if path:
            savehook_new_data[self.k]["currentvisimage"] = path
        self.pixview.changepixmappath(path)

    def setpix(self, k):
        self.k = k
        pixmaps = savehook_new_data[k]["imagepath_all"].copy()
        self.previewimages.setpixmaps(pixmaps, savehook_new_data[k]["currentvisimage"])


class dialog_savedgame_v3(QWidget):
    def viewitem(self, k):
        try:
            self.pixview.setpix(k)
            self.currentfocusuid = k
            currvis = self.righttop.currentIndex()
            if self.righttop.count() > 1:
                self.righttop.removeTab(1)
            tabadd_lazy(
                self.righttop,
                savehook_new_data[k]["title"],
                lambda v: v.addWidget(dialog_setting_game_internal(self, k)),
            )
            self.righttop.setCurrentIndex(currvis)
        except:
            print_exc()

    def itemfocuschanged(self, reftagid, b, k):

        self.reftagid = reftagid
        if b:
            self.currentfocusuid = k
        else:
            self.currentfocusuid = None

        for _btn, exists in self.savebutton:
            _able1 = b and (
                (not exists)
                or (self.currentfocusuid)
                and (os.path.exists(uid2gamepath[self.currentfocusuid]))
            )
            _btn.setEnabled(_able1)
        if self.currentfocusuid:
            self.viewitem(k)

    def delayitemcreater(self, k, select, reftagid):

        item = clickitem(k)
        item.doubleclicked.connect(functools.partial(startgamecheck, self))
        item.focuschanged.connect(functools.partial(self.itemfocuschanged, reftagid))
        if select:
            item.click()
        return item

    def newline(self, res):
        self.reallist[self.reftagid].insert(0, res)
        self.stack.w(calculatetagidx(self.reftagid)).insertw(
            0,
            functools.partial(
                self.delayitemcreater,
                res,
                True,
                self.reftagid,
            ),
            1 + globalconfig["dialog_savegame_layout"]["listitemheight"],
        )
        self.stack.directshow()

    def stack_showmenu(self, p):
        menu = QMenu(self)

        addlist = LAction(("创建列表"))
        startgame = LAction(("开始游戏"))
        delgame = LAction(("删除游戏"))
        opendir = LAction(("打开目录"))
        addtolist = LAction(("添加到列表"))
        if not self.currentfocusuid:

            menu.addAction(addlist)
        else:
            exists = os.path.exists(uid2gamepath[self.currentfocusuid])
            if exists:
                menu.addAction(startgame)
                menu.addAction(delgame)

                menu.addAction(opendir)

                menu.addSeparator()
                menu.addAction(addtolist)
            else:

                menu.addAction(addtolist)
                menu.addSeparator()
                menu.addAction(delgame)

        action = menu.exec(QCursor.pos())
        if action == startgame:
            startgamecheck(self, self.currentfocusuid)
        elif addlist == action:
            _dia = Prompt_dialog(
                self,
                "创建列表",
                "",
                [
                    ["名称", ""],
                ],
            )

            if _dia.exec():

                title = _dia.text[0].text()
                if title != "":
                    i = calculatetagidx(None)
                    if action == addlist:
                        tag = {
                            "title": title,
                            "games": [],
                            "uid": str(uuid.uuid4()),
                            "opened": True,
                        }
                        savegametaged.insert(i, tag)
                        group0 = self.createtaglist(self.stack, title, tag["uid"], True)
                        self.stack.insertw(i, group0)

        elif action == delgame:
            self.shanchuyouxi()
        elif action == opendir:
            self.clicked4()
        elif action == addtolist:
            self.addtolist()

    def addtolistcallback(self, uid, gameuid):

        __save = self.reftagid
        self.reftagid = uid

        if gameuid not in getreflist(self.reftagid):
            getreflist(self.reftagid).insert(0, gameuid)
            self.newline(gameuid)
        else:
            idx = getreflist(self.reftagid).index(gameuid)
            getreflist(self.reftagid).insert(0, getreflist(self.reftagid).pop(idx))
            self.stack.w(calculatetagidx(self.reftagid)).torank1(idx)
        self.reftagid = __save

    def addtolist(self):
        getalistname(
            self,
            lambda x: self.addtolistcallback(x, self.currentfocusuid),
            True,
            self.reftagid,
        )

    def directshow(self):
        self.stack.directshow()

    def __init__(self, parent) -> None:
        super().__init__(parent)
        self.currentfocusuid = None
        self.reftagid = None
        self.reallist = {}
        self.stack = stackedlist()
        self.stack.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.stack.customContextMenuRequested.connect(self.stack_showmenu)
        self.stack.setFixedWidth(
            globalconfig["dialog_savegame_layout"]["listitemwidth"]
        )
        self.stack.bgclicked.connect(clickitem.clearfocus)
        lay = QHBoxLayout()
        self.setLayout(lay)
        lay.addWidget(self.stack)
        lay.setSpacing(0)
        self.righttop = makesubtab_lazy()
        self.pixview = pixwrapper()
        self.pixview.startgame.connect(
            lambda: startgamecheck(self, self.currentfocusuid)
        )
        _w = QWidget()
        rightlay = QVBoxLayout()
        rightlay.setContentsMargins(0, 0, 0, 0)
        _w.setLayout(rightlay)
        self.righttop.addTab(_w, "画廊")
        lay.addWidget(self.righttop)
        rightlay.addWidget(self.pixview)
        self.buttonlayout = QHBoxLayout()
        self.savebutton = []
        rightlay.addLayout(self.buttonlayout)

        self.simplebutton(
            "开始游戏", True, lambda: startgamecheck(self, self.currentfocusuid), True
        )
        self.simplebutton("删除游戏", True, self.shanchuyouxi, False)
        self.simplebutton("打开目录", True, self.clicked4, True)
        self.simplebutton("添加到列表", True, self.addtolist, False)
        if globalconfig["startgamenototop"]:
            self.simplebutton("上移", True, functools.partial(self.moverank, -1), False)
            self.simplebutton("下移", True, functools.partial(self.moverank, 1), False)
        self.simplebutton("添加游戏", False, self.clicked3, 1)
        self.simplebutton("批量添加", False, self.clicked3_batch, 1)
        self.simplebutton(
            "其他设置", False, lambda: dialog_syssetting(self, type_=2), False
        )
        isfirst = True
        for i, tag in enumerate(savegametaged):
            # None
            # {
            #     "title":xxx
            #     "games":[]
            # }
            if tag is None:
                title = "GLOBAL"
                lst = savehook_new_list
                tagid = None
                opened = globalconfig["global_list_opened"]
            else:
                lst = tag["games"]
                title = tag["title"]
                tagid = tag["uid"]
                opened = tag.get("opened", True)
            group0 = self.createtaglist(self.stack, title, tagid, opened)
            self.stack.insertw(i, group0)
            rowreal = 0
            for row, k in enumerate(lst):
                if globalconfig["hide_not_exists"] and not os.path.exists(
                    uid2gamepath[k]
                ):
                    continue
                self.reallist[tagid].append(k)
                if opened and isfirst and (rowreal == 0):
                    vis = True
                    isfirst = False
                else:
                    vis = False
                group0.insertw(
                    rowreal,
                    functools.partial(self.delayitemcreater, k, vis, tagid),
                    1 + globalconfig["dialog_savegame_layout"]["listitemheight"],
                )

                rowreal += 1

    def taglistrerank(self, tagid, dx):
        idx1 = calculatetagidx(tagid)

        idx2 = (idx1 + dx) % len(savegametaged)
        savegametaged.insert(idx2, savegametaged.pop(idx1))
        self.stack.switchidx(idx1, idx2)

    def tagbuttonmenu(self, tagid):
        self.currentfocusuid = None
        self.reftagid = tagid
        menu = QMenu(self)
        editname = LAction(("修改列表名称"))
        addlist = LAction(("创建列表"))
        dellist = LAction(("删除列表"))
        Upaction = LAction("上移")
        Downaction = LAction("下移")
        addgame = LAction(("添加游戏"))
        batchadd = LAction(("批量添加"))
        menu.addAction(Upaction)
        menu.addAction(Downaction)
        menu.addSeparator()
        if tagid:
            menu.addAction(editname)
        menu.addAction(addlist)
        if tagid:
            menu.addAction(dellist)
        menu.addSeparator()
        menu.addAction(addgame)
        menu.addAction(batchadd)

        action = menu.exec(QCursor.pos())
        if action == addgame:
            self.clicked3()
        elif action == batchadd:
            self.clicked3_batch()
        elif action == Upaction:
            self.taglistrerank(tagid, -1)
        elif action == Downaction:
            self.taglistrerank(tagid, 1)
        elif action == editname or action == addlist:
            _dia = Prompt_dialog(
                self,
                "修改列表名称" if action == editname else "创建列表",
                "",
                [
                    [
                        "名称",
                        (
                            savegametaged[calculatetagidx(tagid)]["title"]
                            if action == editname
                            else ""
                        ),
                    ],
                ],
            )

            if _dia.exec():

                title = _dia.text[0].text()
                if title != "":
                    i = calculatetagidx(tagid)
                    if action == addlist:
                        tag = {
                            "title": title,
                            "games": [],
                            "uid": str(uuid.uuid4()),
                            "opened": True,
                        }
                        savegametaged.insert(i, tag)
                        group0 = self.createtaglist(self.stack, title, tag["uid"], True)
                        self.stack.insertw(i, group0)
                    elif action == editname:
                        self.stack.w(i).settitle(title)
                        savegametaged[i]["title"] = title

        elif action == dellist:
            i = calculatetagidx(tagid)
            savegametaged.pop(i)
            self.stack.popw(i)
            self.reallist.pop(tagid)

    def createtaglist(self, p, title, tagid, opened):

        self.reallist[tagid] = []
        _btn = QPushButton(title)
        _btn.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        _btn.clicked.connect(functools.partial(self._revertoepn, tagid))
        _btn.customContextMenuRequested.connect(
            functools.partial(self.tagbuttonmenu, tagid)
        )
        return shrinkableitem(p, _btn, opened)

    def _revertoepn(self, tagid):
        item = savegametaged[calculatetagidx(tagid)]
        if item is None:
            globalconfig["global_list_opened"] = not globalconfig["global_list_opened"]
        else:
            savegametaged[calculatetagidx(tagid)]["opened"] = not savegametaged[
                calculatetagidx(tagid)
            ]["opened"]

    def moverank(self, dx):
        uid = self.currentfocusuid
        idx1 = self.reallist[self.reftagid].index(uid)
        idx2 = (idx1 + dx) % len(self.reallist[self.reftagid])
        uid2 = self.reallist[self.reftagid][idx2]
        self.reallist[self.reftagid].insert(
            idx2, self.reallist[self.reftagid].pop(idx1)
        )

        self.stack.w(calculatetagidx(self.reftagid)).switchidx(idx1, idx2)
        idx1 = getreflist(self.reftagid).index(uid)
        idx2 = getreflist(self.reftagid).index(uid2)
        getreflist(self.reftagid).insert(idx2, getreflist(self.reftagid).pop(idx1))

    def shanchuyouxi(self):
        if not self.currentfocusuid:
            return

        try:
            uid = self.currentfocusuid
            idx2 = getreflist(self.reftagid).index(uid)
            getreflist(self.reftagid).pop(idx2)

            idx2 = self.reallist[self.reftagid].index(uid)
            self.reallist[self.reftagid].pop(idx2)
            clickitem.clearfocus()
            group0 = self.stack.w(calculatetagidx(self.reftagid))
            group0.popw(idx2)
            try:
                group0.w(idx2).click()
            except:
                group0.w(idx2 - 1).click()
        except:
            print_exc()

    def clicked4(self):
        opendirforgameuid(self.currentfocusuid)

    def addgame(self, uid):
        if uid not in self.reallist[self.reftagid]:
            self.newline(uid)
        else:
            idx = self.reallist[self.reftagid].index(uid)
            self.reallist[self.reftagid].pop(idx)
            self.reallist[self.reftagid].insert(0, uid)
            self.stack.w(calculatetagidx(self.reftagid)).torank1(idx)

    def clicked3_batch(self):
        addgamebatch(self.addgame, getreflist(self.reftagid))

    def clicked3(self):
        addgamesingle(self, self.addgame, getreflist(self.reftagid))

    def clicked(self):
        startgamecheck(self, self.currentfocusuid)

    def simplebutton(self, text, save, callback, exists):
        button5 = LPushButton(text)
        button5.setMinimumWidth(10)
        if save:
            self.savebutton.append((button5, exists))
        button5.clicked.connect(callback)
        button5.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.buttonlayout.addWidget(button5)
        return button5
