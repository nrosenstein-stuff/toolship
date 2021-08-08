
import argparse
import logging

from toolship.core.manager import Toolship
from .main import ToolshipGui
#from toolship.plugins.quit import QuitPlugin
from toolship.yubikey import YubikeyPlugin

ship = Toolship()
#ship.add_plugin('quit', QuitPlugin())
ship.add_plugin('yk', YubikeyPlugin())


def main():
  logging.basicConfig(level=logging.INFO)
  parser = argparse.ArgumentParser()
  parser.add_argument('-k', '--keep-open', action='store_true')
  parser.add_argument('-f', '--frameless', action='store_true')
  parser.add_argument('-H', '--hotkey', default='ctrl+alt+space')
  args = parser.parse_args()
  ToolshipGui.mainloop(ship, args.keep_open, args.frameless, args.hotkey)


if __name__ == '__main__':
  main()
