
import logging
import re
import signal
import sys
import threading
import typing as t

from global_hotkeys import register_hotkeys, start_checking_hotkeys
from nr.optional import Optional
from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2.QtGui import QKeyEvent
from PySide2.QtWidgets import QApplication, QMainWindow

from toolship import Toolship
from toolship.gui.utils import qt_threadsafe_connect, qt_threadsafe_method
from toolship.plugins import IsQuitCommand, IsRunnable, IsClipboardValueProducer
from toolship.gui.commandpalette import CommandPalette

log = logging.getLogger(__name__)


class ToolshipGui(QMainWindow):

  border_radius: int = 5
  padding: int = 10
  text_color: str = 'white'
  background_color: str = '#334'

  def __init__(self, toolship: Toolship, minimize: bool, frameless: bool = True) -> None:
    super().__init__()
    qt_threadsafe_connect(self)
    self._toolship = toolship
    self._minimize = minimize
    self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
    if frameless:
      self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
      self.setWindowFlag(QtCore.Qt.Tool)
      self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
    self.setupUi()

  def setupUi(self):
    self.frame = QtWidgets.QFrame()
    self.frame.setStyleSheet(f"""
      * {{
        color: {self.text_color};
        font: bold large "Segoe UI";
        font-size: 16px;
      }}
      #searchQueryInput, #searchResults, #searchResults #container {{
        border-radius: {self.border_radius}px;
      }}
      #searchQueryInput, #searchResults {{
        padding: {self.padding}px;
        width: 600px;
        background-color: {self.background_color};
      }}
      #searchResults QScrollBar {{
        background: rgba(0, 0, 0, 0.2);
        width: 4px;
      }}
    """)
    self.setCentralWidget(self.frame)
    layout = QtWidgets.QVBoxLayout(self.frame)
    layout.setContentsMargins(*(self.padding,)*4)
    layout.setAlignment(QtCore.Qt.AlignTop)

    self.searchQueryInput = QtWidgets.QLineEdit()
    self.searchQueryInput.setObjectName("searchQueryInput")
    self.searchQueryInput.setPlaceholderText('Enter query ...')
    self.searchQueryInput.textChanged.connect(self._searchQueryInput_textChanged)
    layout.addWidget(self.searchQueryInput)

    self.searchResults = CommandPalette(self._toolship)
    self.searchResults.setObjectName("searchResults")
    self.searchResults.setMinimumHeight(400)
    self.searchResults.selectedEvent.connect(lambda a, b: self._dispatchCommand())
    layout.addWidget(self.searchResults)

  def keyPressEvent(self, event: QKeyEvent) -> None:
    if event.key() == QtCore.Qt.Key_Escape:
      self.close()
    elif event.key() == QtCore.Qt.Key_Down:
      self._moveSelection(1)
    elif event.key() == QtCore.Qt.Key_Up:
      self._moveSelection(-1)
    elif event.key() == QtCore.Qt.Key_Return:
      self._dispatchCommand()
    event.accept()

  @qt_threadsafe_method
  def close(self, force: bool = False) -> None:
    if not self._minimize or force:
      super().close()
      sys.exit()
    else:
      self.hide()

  @qt_threadsafe_method
  def show(self) -> None:
    super().show()
    self.activateWindow()
    self.raise_()
    self.searchQueryInput.setText('')
    self.searchQueryInput.setFocus(QtCore.Qt.ActiveWindowFocusReason)

  def _dispatchCommand(self) -> None:
    result = Optional(self.searchResults.current()).map(lambda r: r[1]).or_else(None)
    try:
      if isinstance(result, IsQuitCommand):
        self.close(True)
      elif isinstance(result, IsClipboardValueProducer):
        value = result.get_value()
        QApplication.clipboard().setText(value)
        self.close()
      elif isinstance(result, IsRunnable):
        result.run()
        self.close()
    except Exception:
      log.exception("Unhandled exception while invoking %s", result)

  def _moveSelection(self, amount: int) -> None:
    idx = self.searchResults.currentRow() + amount
    idx = min(max(idx, 0), self.searchResults.rowCount() - 1)
    self.searchResults.setCurrentRow(idx)

  def _searchQueryInput_textChanged(self, query: str) -> None:
    self.searchResults.update(query)

  def _onFocusChanged(self, current: t.Optional[QtWidgets.QWidget], next: t.Optional[QtWidgets.QWidget]) -> None:
    if next is None:
      self.close()

  @staticmethod
  def mainloop(toolship: Toolship, minimize: bool, frameless: bool, hotkey: t.Optional[str] = None) -> None:
    app = QApplication()
    wnd = ToolshipGui(toolship, minimize, frameless)
    wnd.show()
    app.focusChanged.connect(wnd._onFocusChanged)

    signal.signal(signal.SIGINT, lambda *a: wnd.close(True))

    if hotkey:
      keystroke = re.split(r'[\+\- ,]', hotkey)
      register_hotkeys([(keystroke, None, wnd.show)])
      start_checking_hotkeys()

    app.exec_()
