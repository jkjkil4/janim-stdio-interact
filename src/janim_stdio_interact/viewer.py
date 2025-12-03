from __future__ import annotations

import json
import sys
from typing import TYPE_CHECKING

from janim.anims.timeline import BuiltTimeline
from janim.gui.anim_viewer import AnimViewer

if TYPE_CHECKING:
    from janim_stdio_interact.cli import AnimViewerManager


class StdioAnimViewer(AnimViewer):
    def __init__(
        self,
        manager: AnimViewerManager,
        key: str,
        built: BuiltTimeline,
        **kwargs
    ):
        self.manager = manager
        self.key = key
        super().__init__(built, interact=False, **kwargs)

        self.write_viewer_message(
            key,
            'gui',
            janim={
                'type': 'created'
            }
        )

    def has_connection(self) -> bool:
        return True

    def send_json(self, msg: dict) -> None:
        self.write_viewer_message(self.key, 'gui', **msg)

    @staticmethod
    def write_viewer_message(key: str, from_scope: str, **msg) -> None:
        json.dump(
            {
                'type': 'viewer-msg',
                'viewer': key,
                'from': from_scope,
                **msg
            },
            fp=sys.stdout,
            ensure_ascii=False
        )
        sys.stdout.write('\n')
        sys.stdout.flush()

    def closeEvent(self, event):
        super().closeEvent(event)

        self.manager.remove(self.key)
