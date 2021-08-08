
__author__ = 'Niklas Rosenstein <rosensteinniklas@gmail.com>'
__version__ = '0.0.0'


import argparse
import typing as t
from yubikit.core.smartcard import SmartCardConnection

from yubikit.oath import Credential, OathSession
from ykman.device import connect_to_device

from toolship.core.plugins import ArgparsingPlugin, IsClipboardValueProducer, IsRunnable, Result, PluginMatchError


class YubikeyPlugin(ArgparsingPlugin):

  def __init__(self) -> None:
    self._conn: t.Optional[SmartCardConnection] = None
    self._session: t.Optional[OathSession] = None
    self._error: t.Optional[str] = None

  def on_unload(self) -> None:
    self._error = None
    self._close()

  def _close(self) -> None:
    if self._conn:
      self._conn.close()
      self._conn = None
      self._session = None

  def _get_session(self, reload: bool = False) -> OathSession:
    if not reload and self._session:
      return self._session
    if self._error is not None:
      return None
    self._close()
    try:
      self._conn = connect_to_device(connection_types=[SmartCardConnection])[0]
      self._session = OathSession(self._conn)
    except Exception as exc:
      self._error = str(exc)
    return self._session

  def get_prefix(self) -> str:
    return 'yk'

  def get_parser(self) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument('query', nargs='?')
    return parser

  def match_arguments(self, args: argparse.Namespace) -> t.List['Result']:
    session = self._get_session()
    if not session:
      return [Result('#error', 'Error', None, self._error)]
    results: t.List[Result] = []
    for cred in session.list_credentials():
      if not args.query or args.query.strip().lower() in cred.issuer.lower():
        results.append(OathCommand(session, cred))
    results.sort(key=lambda r: r.name)
    return results


class OathCommand(Result, IsClipboardValueProducer):

  def __init__(self, session: OathSession, cred: Credential) -> None:
    self.id = cred.id.decode('utf8')
    self.name = cred.issuer
    self.description = f'Copy {cred.issuer} {cred.oath_type.name} code for <i>{cred.name}</i> to clipboard.'
    self._session = session
    self._cred = cred

  def get_value(self) -> str:
    return self._session.calculate_code(self._cred).value
