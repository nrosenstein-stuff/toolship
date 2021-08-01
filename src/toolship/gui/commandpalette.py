
import typing as t

from PySide2 import QtCore
from toolship import Toolship
from toolship import plugins

from toolship.plugins import Result


class CommandPaletteModel(QtCore.QAbstractListModel):
  """
  This model displays a list of #toolship.plugins.Command#s.
  """

  def __init__(self, toolship: Toolship) -> None:
    super().__init__()
    self._toolship = toolship
    self._results: t.List[t.Tuple[str, Result]] = []
    self._current_row: int = 0

  def currentRow(self) -> int:
    return self._current_row

  def setCurrentRow(self, idx: int) -> None:
    if self._results:
      self._current_row = idx % len(self._results)
    else:
      self._current_row = 0
    if self._current_row < 0:
      self._current_row += len(self._results)
    self.dataChanged.emit(self.index(idx), self.index(idx))

  def current(self) -> t.Optional[t.Tuple[str, Result]]:
    try:
      return self._results[self._current_row]
    except IndexError:
      return None

  def update(self, query: str) -> None:
    selected = self.current()
    self._results = self._toolship.get_commands(query)
    self.dataChanged.emit(self.index(0, 0), self.index(len(self._results) -1 , 0))
    self._current_row = 0
    if selected:
      for idx, (plugin_id, result) in enumerate(self._results):
        if plugin_id == selected[0]  and result.id == selected[1].id:
          self._current_row = idx
          break

  def rowCount(self, parent: QtCore.QModelIndex = None) -> int:
    return len(self._results)

  def columnCount(self, parent: QtCore.QModelIndex) -> int:
    return 1

  def data(self, index: QtCore.QModelIndex, role: int) -> t.Any:
    if role == QtCore.Qt.DisplayRole:
      return self._results[index.row()][1].name
    elif role == QtCore.Qt.DecorationRole:
      if index.row() == self._current_row:
        return QtCore.Qt.red
    return None

  def flags(self, index: QtCore.QModelIndex) -> QtCore.Qt.ItemFlags:
    return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemNeverHasChildren
