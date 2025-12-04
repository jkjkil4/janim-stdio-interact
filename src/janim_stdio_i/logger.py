import logging

from rich.console import Console
from rich.logging import RichHandler

log = logging.getLogger('janim-stdio-i')
log.propagate = False
if not log.hasHandlers():
    fmt = logging.Formatter("%(message)s", datefmt="[%X]")
    rich_handler = RichHandler(console=Console(stderr=True))    # RichHandler 默认输出到 stdout，需要手动改为 stderr
    rich_handler.setFormatter(fmt)
    log.addHandler(rich_handler)
log.setLevel('INFO')
