
import functools
import logging
import sys
import threading
import types
import typing as t

from PySide2 import QtCore

log = logging.getLogger(__name__)
T = t.TypeVar('T')
U = t.TypeVar('U')


def qt_threadsafe_method(method: types.FunctionType) -> types.FunctionType:
  """
  Decorates a method in a Qt class to use a signal if the method is not called from
  the main thread. Note that the return type of that function must be None.
  """

  signal_name = method.__name__ + '_signal'
  frame = sys._getframe(1)
  connected = False
  try:
    frame.f_locals[signal_name] = QtCore.Signal(name=signal_name)
    @functools.wraps(method)
    def _wrapper(self, *args) -> None:
      nonlocal connected
      if threading.current_thread() is not threading.main_thread():
        getattr(self, signal_name).emit(*args)
      else:
        method(self, *args)
    _wrapper.__qt_signal__ = signal_name
    return _wrapper
  finally:
    del frame


def qt_threadsafe_connect(obj) -> None:
  for key in dir(obj):
    value = getattr(obj, key)
    if hasattr(value, '__qt_signal__'):
      getattr(obj, value.__qt_signal__).connect(value)


def extend_or_trim(
  target: t.List[T],
  reference: t.List[U],
  factory: t.Callable[[int, U], T],
  update: t.Callable[[int, U ,T], None],
  delete: t.Optional[t.Callable[[int, T], None]] = None
) -> None:

  for idx, val in enumerate(reference):
    if idx >= len(target):
      target.append(factory(idx, val))
    update(idx, val, target[idx])

  if delete:
    for idx in range(len(reference), len(target)):
      delete(idx, target.pop())
  else:
    target[:] = target[:len(reference)]
