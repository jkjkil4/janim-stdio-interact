import os
import sys
from janim_stdio_interact.locale import get_package_dir

includes = sys.argv[1:]


def is_included(file: str) -> bool:
    return any(file.endswith(include) for include in includes)


def main() -> None:
    for root, dirs, files in os.walk(get_package_dir()):
        for file in files:
            if not file.endswith('.py'):
                continue
            if includes and not is_included(file):
                continue
            dist = os.path.join(get_package_dir(), 'locale', 'source', file[:-3] + '.pot')
            source = os.path.relpath(os.path.join(root, file), os.path.join(get_package_dir(), '../..'))
            cmd = f'xgettext -o "{dist}" "{source}"'
            print(cmd)
            os.system(cmd)


if __name__ == '__main__':
    main()
