
from argparse import ArgumentParser, Namespace

from janim_stdio_interact.locale.i18n import get_local_strings, set_lang

_ = get_local_strings('__main__')


def main() -> None:
    global _

    initial_parser = ArgumentParser(add_help=False)
    initial_parser.add_argument('--lang')
    initial_args = initial_parser.parse_known_args()[0]

    if initial_args.lang:
        set_lang(initial_args.lang)
        _ = get_local_strings('__main__')

    parser = ArgumentParser(description=_('A utility library for interacting with JAnim GUI via standard input/output'))
    parser.set_defaults(func=None)

    parser.add_argument(
        '--lang',
        help=_('Language code, e.g., en, zh_CN')
    )
    parser.add_argument(
        '-v', '--version',
        action='store_true'
    )
    parser.add_argument(
        '--loglevel', default='INFO', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        type=str.upper,
        help=_('Set the logging level (default: INFO)')
    )

    sp = parser.add_subparsers()
    host_parser(sp.add_parser('host', help=_('Host JAnim GUI and interact via stdio')))

    args = parser.parse_args()

    if args.version:
        from janim_stdio_interact import __version__
        print(f'janim-stdio-interact {__version__}')

    if args.func is None:
        if not args.version:
            parser.print_help()
        return

    from janim.logger import log
    log.setLevel(args.loglevel)

    args.func(args)


def host_parser(parser: ArgumentParser) -> None:
    parser.set_defaults(func=host)


def host(args: Namespace) -> None:
    from janim_stdio_interact.cli import host
    host(args)
