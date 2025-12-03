import json
import sys

from PySide6.QtCore import QThread, Signal

from janim_stdio_i.locale.i18n import get_local_strings
from janim_stdio_i.logger import log

_ = get_local_strings('listener')


class StdinListener(QThread):
    message_received = Signal(dict)
    exited = Signal()

    def run(self) -> None:
        log.debug('StdinListener started')

        try:
            while True:
                line = sys.stdin.readline()
                if not line:
                    log.debug('StdinListener EOF reached, exiting ...')
                    break
                line = line.strip()
                if not line:
                    continue

                try:
                    msg = json.loads(line)
                except Exception:
                    log.error(_('Failed to parse JSON from stdin: %r'), line)
                    continue

                self.message_received.emit(msg)

        finally:
            log.debug('StdinListener exited')
            self.exited.emit()
