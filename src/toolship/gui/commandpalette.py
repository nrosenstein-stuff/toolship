
import typing as t

from PySide2 import QtCore, QtGui, QtWidgets
from toolship import Toolship
from toolship import plugins
from toolship.gui.utils import extend_or_trim

from toolship.plugins import Result


class CommandPaletteItem(QtWidgets.QWidget):
  clickedEvent = QtCore.Signal()
  _plugin_id: str
  _result: Result

  def __init__(self, parent: t.Any = None) -> None:
    super().__init__(parent)
    self._layout = QtWidgets.QVBoxLayout(self)
    self._layout.setAlignment(QtCore.Qt.AlignTop)
    self.setObjectName("root")
    self._active = False
    self._name = QtWidgets.QLabel('')
    self._name.setObjectName("name")
    self._description = QtWidgets.QLabel('')
    self._description.setObjectName("description")
    self.setAttribute(QtCore.Qt.WA_StyledBackground, True)
    self._layout.addWidget(self._name)
    self._layout.addWidget(self._description)
    self._layout.setContentsMargins(3, 4, 4, 4)
    self._update_style()

  def _update_style(self) -> None:
    background_color = 'rgba(255, 255, 255, 0.1)' if self._active else 'none'
    self.setStyleSheet(f"""
      #root {{ background-color: {background_color}; }}
      #description {{
        font-weight: normal;
        font-size: 12px;
      }}
    """)

  def setActive(self, active: bool) -> None:
    self.setResult(self._plugin_id, self._result, active)

  def setResult(self, plugin_id: str, result: Result, active: bool) -> 'CommandPaletteItem':
    self._plugin_id = plugin_id
    self._result = result
    self._active = active
    self._name.setText(f'{result.name} <sub>{plugin_id}</sub>')
    self._description.setText(result.description or result.error or '')
    self._description.setVisible(bool(active and (result.description or result.error)))
    self._update_style()
    return self

  def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
    self.clickedEvent.emit()
    event.accept()


class CommandPalette(QtWidgets.QScrollArea):
  selectedEvent = QtCore.Signal(str, Result, name='selectedEvent')

  def __init__(self, toolship: Toolship, parent: t.Any = None) -> None:
    super().__init__(parent)
    self.setWidgetResizable(True)
    self._container = QtWidgets.QWidget()
    self._container.setObjectName("container")
    self.setWidget(self._container)
    self._toolship = toolship
    self._layout = QtWidgets.QVBoxLayout(self._container)
    self._layout.setSpacing(0)
    self.setContentsMargins(0, 0, 0, 0)
    self._layout.setContentsMargins(0, 0, 0, 0)
    self._layout.setAlignment(QtCore.Qt.AlignTop)
    self._items: t.List[CommandPaletteItem] = []
    self._results: t.List[t.Tuple[str, Result]] = []
    self._current_row = 0

  def rowCount(self) -> int:
    return len(self._items)

  def currentRow(self) -> int:
    return self._current_row

  def setCurrentRow(self, idx: int) -> None:
    old_idx = self._current_row
    if self._items:
      self._current_row = idx % len(self._items)
    else:
      self._current_row = 0
    if self._current_row < 0:
      self._current_row += len(self._items)
    if old_idx != self._current_row:
      self._items[old_idx].setActive(False)
      self._items[self._current_row].setActive(True)
      self.ensureWidgetVisible(self._items[self._current_row])

  def current(self) -> t.Optional[t.Tuple[str, Result]]:
    try:
      return self._results[self._current_row]
    except IndexError:
      return None

  def update(self, query: str) -> None:
    selected = self.current()
    self._results = self._toolship.get_commands(query)

    # Find the same selected result again.
    self._current_row = 0
    if selected:
      for idx, (plugin_id, result) in enumerate(self._results):
        if plugin_id == selected[0]  and result.id == selected[1].id:
          self._current_row = idx
          break

    # Update the widgets.
    def _factory(idx: int, t: t.Tuple[str, Result]) -> CommandPalette:
      widget = CommandPaletteItem()
      def _clicked():
        if idx == self._current_row:
          self.selectedEvent.emit(t[0], t[1])
        else:
          self.setCurrentRow(idx)
      widget.clickedEvent.connect(_clicked)
      self._layout.addWidget(widget)
      return widget

    extend_or_trim(
      self._items,
      self._results,
      _factory,
      lambda idx, t, w: w.setResult(t[0], t[1], idx == self._current_row),
      lambda idx, w: (self._layout.removeWidget(w), w.setParent(None))
    )

    self.setVisible(bool(self._items))
