
import json
import sys
from argparse import Namespace

from janim.cli import get_all_timelines_from_module
from janim.gui.application import Application
from janim.utils.reload import reset_reloads_state
from PySide6.QtCore import QThread, Signal

from janim_stdio_interact.logger import log
from janim_stdio_interact.viewer import StdioAnimViewer

# TODO: i18n
_ = lambda x: x     # noqa: E731


def host(args: Namespace) -> None:
    log.info(_('Hosting JAnim GUI and interacting via stdio ...'))

    app = Application()
    app.setQuitOnLastWindowClosed(False)

    manager = AnimViewerManager()

    # 启动用于监听 stdin 的线程
    listener = StdinListener()
    listener.message_received.connect(manager.handle_message)
    listener.exited.connect(app.quit)
    listener.start()

    # 进入 Qt 的事件循环
    try:
        app.exec()
    except KeyboardInterrupt:
        pass

    log.debug('Qt event loop exited')

    # 因为 listener 先退出，所以这里直接 wait
    listener.wait()

    log.info(_('Main process exited'))


class AnimViewerManager:
    def __init__(self):
        self.viewers: dict[str, StdioAnimViewer] = {}

    def handle_message(self, msg: dict) -> None:
        log.debug('Received message from stdin: %r', msg)

        type = msg['type']

        match type:
            case 'execute':
                self.execute(msg['name'], msg['source'])

            case 'close':
                self.close(msg['name'])

    def execute(self, name: str, source: str) -> None:
        reset_reloads_state()
        get_all_timelines_from_module.cache_clear()
        # TODO

    def close(self, name: str) -> None:
        # TODO
        pass


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
