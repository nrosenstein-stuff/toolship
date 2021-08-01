
import abc
import argparse
import dataclasses
import shlex
import typing as t


class PluginMatchError(Exception):
  ...


class Plugin(abc.ABC):

  def on_load(self) -> None: pass

  def on_unload(self) -> None: pass

  @abc.abstractmethod
  def match_search_query(self, query: str) -> t.List['Result']: ...


@dataclasses.dataclass
class Result:
  """
  Represents a result returned from a #Plugin.
  """

  id: str
  name: str
  description: t.Optional[str] = None
  error: t.Optional[str] = None


class IsQuitCommand(abc.ABC):
  pass


class QuitResult(Result, IsQuitCommand):

  def __init__(self) -> None:
    super().__init__('#quit', 'Quit', 'Quit toolship.')


class IsRunnable(abc.ABC):
  """
  Can be implemented by #Result#s to make them runnable when the result is selected.
  """

  @abc.abstractmethod
  def run(self) -> None: ...


class IsClipboardValueProducer(abc.ABC):
  """
  Can be implemented by #Result#s to provide a value to be copied to the clipboard when
  the result is selected.
  """

  @abc.abstractmethod
  def get_value(self) -> str: ...


class ArgparsingPlugin(Plugin):

  @abc.abstractmethod
  def get_prefix(self) -> str: ...

  @abc.abstractmethod
  def get_parser(self) -> argparse.ArgumentParser: ...

  @abc.abstractmethod
  def match_arguments(self, args: argparse.Namespace) -> t.List['Result']: ...

  _parser: t.Optional[argparse.ArgumentParser] = None

  def match_search_query(self, query: str) -> t.List['Result']:
    args = shlex.split(query)
    if not args or args[0] != self.get_prefix():
      return []

    if self._parser is None:
      self._parser = self.get_parser()

    args, unknowns = self._parser.parse_known_args(args[1:])
    if unknowns:
      raise PluginMatchError('unknown arguments: ' + str(unknowns))

    return self.match_arguments(args)
