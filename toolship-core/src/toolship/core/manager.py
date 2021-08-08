
__author__ = 'Niklas Rosenstein <rosensteinniklas@gmail.com>'
__version__ = '0.0.0'

import logging
import typing as t

from .plugins import Plugin, Result, PluginMatchError

log = logging.getLogger(__name__)


class Toolship:

  def __init__(self) -> None:
    self._plugins: t.Dict[str, Plugin] = {}

  def add_plugin(self, plugin_id: str, plugin: Plugin) -> None:
    self._plugins[plugin_id] = plugin

  def on_load(self) -> None:
    for plugin_id, plugin in self._plugins.items():
      try:
        plugin.on_load()
      except:
        log.exception('Unhandled error in Plugin.on_load: %s', plugin_id)

  def on_unload(self) -> None:
    for plugin_id, plugin in self._plugins.items():
      try:
        plugin.on_unload()
      except:
        log.exception('Unhandled error in Plugin.on_load: %s', plugin_id)

  def get_commands(self, query: str) -> t.List[t.Tuple[str, Result]]:
    commands: t.List[t.Tuple[str, Result]] = []
    for plugin_id, plugin in self._plugins.items():
      try:
        for result in plugin.match_search_query(query):
          commands.append((plugin_id, result))
      except PluginMatchError as exc:
        commands.append((plugin_id, Result('#error', 'Error', None, str(exc))))
      except:
        log.exception('Unhandled error in Plugin.match_search_query: %s', plugin_id)
    return commands
