

import inspect
import os
import sys
import traceback
import types
from argparse import Namespace

from janim.anims.timeline import BuiltTimeline, Timeline
from janim.cli import get_all_timelines_from_module
from janim.exception import ExitException
from janim.gui.application import Application
from janim.utils.file_ops import STDIN_FILENAME
from janim.utils.reload import reset_reloads_state

from janim_stdio_i.listener import StdinListener
from janim_stdio_i.locale.i18n import get_local_strings
from janim_stdio_i.logger import log
from janim_stdio_i.viewer import StdioAnimViewer

_ = get_local_strings('cli')


def host(args: Namespace) -> None:
    log.info(_('Hosting JAnim GUI and interacting via stdio ...'))

    # 兼容相对于当前工作目录的导入
    sys.path.insert(0, os.getcwd())

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

        try:
            type = msg['type']

            match type:
                case 'execute':
                    self.execute(msg['key'], msg['source'])

                case 'close':
                    self.close(msg['key'])

                case _:
                    log.warning(_('Unrecognized message type: "%s"'), type)

        except Exception:
            log.exception(_('Error occurred while processing message %r'), msg)

    def execute(self, key: str, source: str) -> None:
        reset_reloads_state()

        viewer = self.viewers.get(key, None)

        # 创建 module / 复用已有 module
        if viewer is None:
            module_name = f'__janim_stdio_i_{key}__'
            module = types.ModuleType(module_name)
            module.__file__ = STDIN_FILENAME

            sys.modules[module_name] = module
        else:
            module = inspect.getmodule(viewer.built.timeline)

        # 编译代码
        code = compile(source, STDIN_FILENAME, 'exec')
        try:
            exec(code, module.__dict__)
        except Exception as e:
            if not isinstance(e, ExitException):
                traceback.print_exc()
            StdioAnimViewer.write_viewer_message(
                key,
                'execute',
                janim={
                    'type': 'error',
                    'reason': 'compile-failed'
                }
            )
            return

        get_all_timelines_from_module.cache_clear()
        timelines = get_all_timelines_from_module(module)
        if not timelines:
            StdioAnimViewer.write_viewer_message(
                key,
                'execute',
                janim={
                    'type': 'error',
                    'reason': 'no-timeline'
                }
            )
            return

        # 尝试找到和原来同名的 Timeline，如果没有就用列表中的第一个
        if viewer is None:
            timeline_cls = timelines[0]
        else:
            timeline_cls = getattr(module, viewer.built.timeline.__class__.__name__, None)
            if timeline_cls is None or not isinstance(timeline_cls, type) or not issubclass(timeline_cls, Timeline):
                timeline_cls = timelines[0]
        timeline_name = timeline_cls.__name__

        # 构建
        try:
            # TODO: args
            built: BuiltTimeline = timeline_cls().build()
        except Exception as e:
            if not isinstance(e, ExitException):
                traceback.print_exc()
            StdioAnimViewer.write_viewer_message(
                key,
                'execute',
                janim={
                    'type': 'error',
                    'reason': 'build-failed'
                }
            )
            return

        # 创建 viewer / 更新 viewer
        if viewer is None:
            log.debug('Creating viewer "%s"', key)

            # TODO: args
            available_timeline_names = [timeline.__name__ for timeline in timelines]
            viewer = StdioAnimViewer(self,
                                     key,
                                     built,
                                     available_timeline_names=available_timeline_names)
            self.viewers[key] = viewer
            viewer.show()

        else:
            log.debug('Reusing viewer "%s"', key)

            viewer.name_edit.blockSignals(True)
            viewer.name_edit.setText(timeline_name)
            viewer.name_edit.blockSignals(False)
            viewer.set_built_and_handle_states(module, built, timeline_cls.__name__)

        StdioAnimViewer.write_viewer_message(
            key,
            'execute',
            janim={
                'type': 'success'
            }
        )

    def close(self, key: str) -> None:
        viewer = self.viewers.get(key, None)

        if viewer is None:
            StdioAnimViewer.write_viewer_message(
                key,
                'close',
                janim={
                    'type': 'error',
                    'reason': 'not-found'
                }
            )
            return

        viewer.close()
        # self.remove(key)  # viewer 的 closeEvent 会完成这件事
        StdioAnimViewer.write_viewer_message(
            key,
            'close',
            janim={
                'type': 'success'
            }
        )

    def remove(self, key: str) -> None:
        viewer = self.viewers.pop(key)
        module = inspect.getmodule(viewer.built.timeline)
        module_name = module.__name__
        del sys.modules[module_name]

        log.debug('Removed viewer "%s" and related resources', key)
