
from argparse import Namespace

from janim.examples import HelloJAnimExample
from janim.gui.application import Application

from janim_stdio_interact.controller import AnimViewerController
from janim_stdio_interact.logger import log


def host(args: Namespace) -> None:
    log.info('Hosting JAnim GUI and interacting via stdio ...')

    app = Application()

    # TODO: create an instance for listening to stdin

    app.exec()
