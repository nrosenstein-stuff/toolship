
import re
import logging
import typing as t

from pynput import keyboard
from pynput.keyboard import Key, KeyCode

_Callback = t.Callable[[], t.Any]
_KeySeq = t.Sequence[t.Union[Key, KeyCode]]
_KeySet = t.Set[t.Union[Key, KeyCode]]
log = logging.getLogger(__name__)


class KeyboardListener:

  def __init__(self) -> None:
    self._current: _KeySet = set()
    self._listeners: t.List[t.Tuple[_KeySet, _Callback]] = []
    self._thread: t.Optional[keyboard.Listener] = None

  def _on_down(self, key: t.Union[Key, KeyCode]) -> None:
    self._current.add(key)
    for keyseq, callback in self._listeners:
      if self._current == keyseq:
        try:
          callback()
        except Exception:
          log.exception('Unhandled exception in KeyboardListener callback for keyseq %s', keyseq)

  def _on_up(self, key: t.Union[Key, KeyCode]) -> None:
    try:
      self._current.remove(key)
    except KeyError:
      pass

  def start(self) -> None:
    self._thread = keyboard.Listener(on_press=self._on_down, on_release=self._on_up)
    self._thread.__enter__()

  def stop(self) -> None:
    if self._thread:
      self._thread.__exit__(None, None, None)
      self._thread.join()

  def register(self, keyseq: t.Union[str, _KeySeq], callback: _Callback) -> None:
    if isinstance(keyseq, str):
      keyseq = from_string(keyseq) 
    self._listeners.append((set(keyseq), callback))


def from_string(seq: str) -> _KeySet:
  result: _KeySet = set()
  parts = re.split(r'[\+\- ,]', seq)
  for part in parts:
    if hasattr(Key, part):
      result.add(getattr(Key, part))
    else:
      result.add(KeyCode(char=part))
  return result
