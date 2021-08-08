
"""
A small wrapper around #pynput to provide an easy-to-use API to listen to keyboard shortcuts
globally.

Example:

```python
def _on_hotkey_down():
  print('Open Toolship!')

from toolship.core.hotkeys import HotkeyListener

listener = HotkeyListener()
listener.add('ctrl+alt+space', _on_hotkey_down)
listener.start()

```
"""

import re
import logging
import time
import typing as t

from pynput import keyboard
from pynput.keyboard import Key, KeyCode

_Callback = t.Callable[[], t.Any]
_KeySeq = t.Sequence[t.Union[Key, KeyCode]]
_KeySet = t.Set[t.Union[Key, KeyCode]]
log = logging.getLogger(__name__)

MODIFIERS = {
  Key.ctrl:  Key.ctrl,  Key.ctrl_l:  Key.ctrl,  Key.ctrl_r:  Key.ctrl,
  Key.alt:   Key.alt,   Key.alt_l:   Key.alt,   Key.alt_r:   Key.alt,
  Key.cmd:   Key.cmd,   Key.cmd_l:   Key.cmd,   Key.cmd_r:   Key.cmd,
  Key.shift: Key.shift, Key.shift_l: Key.shift, Key.shift_r: Key.shift,
}


def keyset_match(reference: _KeySet, current: _KeySet) -> bool:
  """
  Check's if the *current* keyset matches the *reference* keyset. This is more than just a
  direct comparison because keys in *current* are also translated via the #MODIFIERS mapping.
  mapping.
  """

  if len(reference) != len(current):
    return False

  for key in current:
    if not (key in reference or MODIFIERS.get(key) in reference):
      return False

  return True


class HotkeyListener:
  """
  A smaller wrapper around #pynput to make listening to hotkeys globally easy.
  """

  #: The maximum number of seconds since the previous key-down event to still consider
  #: it part of the same keystroke. If you type fast, #pynput may not catch all key-up
  #: events which would cause the #HotkeyListener to keep zombie keys in the set that
  #: represents the active keystroke. (at least on Windows 10).
  consistent_keystroke_threshold: float

  def __init__(self, consistent_keystroke_threshold: float = 1.0) -> None:
    self.consistent_keystroke_threshold = consistent_keystroke_threshold
    self._current: _KeySet = set()
    self._last_modified = time.time()
    self._listeners: t.List[t.Tuple[_KeySet, _Callback]] = []
    self._listener: t.Optional[keyboard.Listener] = None

  def _on_down(self, key: t.Union[Key, KeyCode]) -> None:
    if (time.time() - self._last_modified) > self.consistent_keystroke_threshold:
      self._current.clear()
    self._current.add(key)
    self._last_modified = time.time()
    for keyseq, callback in self._listeners:
      if keyset_match(keyseq, self._current):
        try:
          callback()
        except Exception:
          log.exception('Unhandled exception in HotkeyListener callback for keyseq %s', keyseq)

  def _on_up(self, key: t.Union[Key, KeyCode]) -> None:
    try:
      self._current.remove(key)
    except KeyError:
      pass

  def start(self) -> None:
    """
    Start the #pynput listener. You should call #stop() before exiting your application.
    """

    self._listener = keyboard.Listener(on_press=self._on_down, on_release=self._on_up)
    self._listener.__enter__()

  def stop(self) -> None:
    """
    Stop the #pynput listener and wait for it to complete. This should be called before
    exiting the application.
    """

    if self._listener:
      self._listener.__exit__(None, None, None)
      self._listener.join()

  def add(self, keyseq: t.Union[str, _KeySeq], callback: _Callback) -> None:
    """
    Register a callback to be invoked when a given sequence of keys is active at the same time.

    # Arguments
    keyseq: A list of #Key#s and #KeyCode#s or a string representing the keystroke. Examples:
      `ctrl+alt+space`, `cmd+t+0`.
    callback: The function to call if the global keystroke is matched. The function does not
      accept arguments and the return value is ignored.
    """

    if isinstance(keyseq, str):
      keyseq = from_string(keyseq)
    self._listeners.append((set(keyseq), callback))


def from_string(seq: str) -> _KeySet:
  """
  Converts a string representing a key sequence to a set of #Key#s and #KeyCode#s.

  Example:

  ```python
  >>> from_string('ctrl+alt+space')
  ```
  """

  result: _KeySet = set()
  parts = re.split(r'[\+\- ,]', seq)
  for part in parts:
    if hasattr(Key, part):
      result.add(getattr(Key, part))
    else:
      result.add(KeyCode(char=part))
  return result
