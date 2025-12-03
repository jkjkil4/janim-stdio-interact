import importlib.util
import os
from functools import lru_cache


@lru_cache(maxsize=1)
def get_package_dir() -> str:
    '''
    得到 janim-stdio-interact 的路径
    '''
    return os.path.dirname(importlib.util.find_spec('janim_stdio_i').origin)
