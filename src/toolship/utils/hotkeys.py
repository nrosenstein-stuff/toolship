
import os

if os.name == 'nt':
  from global_hotkeys import register_hotkeys, start_checking_hotkeys
else:
  def register_hotkeys(*a, **kw): pass
  def start_checking_hotkeys(*a, **kw): pass
