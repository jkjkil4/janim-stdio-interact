
import json
import sys

from janim.anims.timeline import BuiltTimeline
from janim.gui.anim_viewer import AnimViewer


class StdioAnimViewer(AnimViewer):
    def __init__(
        self,
        name: str,
        built: BuiltTimeline,
        **kwargs
    ):
        self.name = name
        super().__init__(built, interact=False, **kwargs)

    def has_connection(self) -> bool:
        return True

    def send_json(self, msg: dict) -> None:
        json.dump({
            'viewer': self.name,
            **msg
        }, fp=sys.stdout)
        sys.stdout.flush()
