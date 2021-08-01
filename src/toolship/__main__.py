
import argparse
import logging

from toolship import Toolship
from toolship.gui import ToolshipGui
from toolship.plugins.quit import QuitPlugin
from toolship.plugins.yubikey import YubikeyPlugin

ship = Toolship()
ship.add_plugin('quit', QuitPlugin())
ship.add_plugin('yk', YubikeyPlugin())


def main():
  logging.basicConfig(level=logging.INFO)
  parser = argparse.ArgumentParser()
  parser.add_argument('-k', '--keep-open', action='store_true')
  parser.add_argument('-H', '--hotkey', default='control+alt+space')
  args = parser.parse_args()
  ToolshipGui.mainloop(ship, args.keep_open, args.hotkey)


if __name__ == '__main__':
  main()