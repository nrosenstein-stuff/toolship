
import argparse
import typing as t
from yubikit.core.smartcard import SmartCardConnection

from yubikit.oath import Credential, OathSession
from ykman.device import connect_to_device

from toolship.plugins import ArgparsingPlugin, IsClipboardValueProducer, IsRunnable, Result, PluginMatchError


class YubikeyPlugin(ArgparsingPlugin):

  def __init__(self) -> None:
    self._conn: t.Optional[SmartCardConnection] = None
    self._session: t.Optional[OathSession] = None

  def _close(self) -> None:
    if self._conn:
      self._conn.close()
      self._conn = None
      self._session = None

  def _get_session(self, reload: bool = False) -> OathSession:
    if not reload and self._session:
      return self._session
    self._close()
    self._conn = connect_to_device(connection_types=[SmartCardConnection])[0]
    self._session = OathSession(self._conn)
    return self._session

  def get_prefix(self) -> str:
    return 'yk'

  def get_parser(self) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument('query', nargs='?')
    parser.add_argument('-r', '--reload', action='store_true')
    return parser

  def match_arguments(self, args: argparse.Namespace) -> t.List['Result']:
    if args.reload and args.query:
      raise PluginMatchError('query and -r,--reload cannot be combined')
    if args.reload:
      return [ReloadCommand(self)]
    session = self._get_session()
    results: t.List[Result] = []
    for cred in session.list_credentials():
      if not args.query or args.query.strip().lower() in cred.issuer.lower():
        results.append(OathCommand(session, cred))
    results.sort(key=lambda r: r.name)
    return results


class ReloadCommand(Result, IsRunnable):

  id = '#reload'
  name = 'Reload YubiKey SmartCard connection(s)'

  def __init__(self, plugin: YubikeyPlugin) -> None:
    self._plugin = plugin

  def run(self) -> None:
    self._plugin._get_session(reload=True)


class OathCommand(Result, IsClipboardValueProducer):

  def __init__(self, session: OathSession, cred: Credential) -> None:
    self.id = cred.id
    self.name = cred.issuer
    self.description = f'Copy {cred.oath_type.name} code for {cred.issuer} to clipboard.'
    self._session = session
    self._cred = cred

  def get_value(self) -> str:
    return self._session.calculate_code(self._cred).value
