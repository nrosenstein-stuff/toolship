
import typing as t

from toolship.plugins import Plugin, QuitResult, Result


class QuitPlugin(Plugin):

  def match_search_query(self, query: str) -> t.List['Result']:
    if query and 'quit'.startswith(query.lower()):
      return [QuitResult()]
    return []
