
import functools
import logging
import sys
import threading
import types

from PySide2 import QtCore

log = logging.getLogger(__name__)


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
