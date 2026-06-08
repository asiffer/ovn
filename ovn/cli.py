import click

from ovn.client import OVNClient
from ovn.models.base import Model


@click.group("ovn")
def entrypoint():
    pass


@entrypoint.command()
def shell():
    """Start an interactive shell with preloaded imports."""
    banner = """\033[1;32m
 ██████╗ ██╗   ██╗███╗   ██╗
██╔═══██╗██║   ██║████╗  ██║
██║   ██║██║   ██║██╔██╗ ██║
██║   ██║╚██╗ ██╔╝██║╚██╗██║
╚██████╔╝ ╚████╔╝ ██║ ╚████║
 ╚═════╝   ╚═══╝  ╚═╝  ╚═══╝
\033[0m"""
    namespace = {c.__name__: c for c in Model.__subclasses__()}

    try:
        from IPython import start_ipython
        from traitlets.config import Config

        config = Config()
        config.TerminalInteractiveShell.banner1 = banner
        config.TerminalInteractiveShell.enable_tip = False
        start_ipython(argv=[], user_ns=namespace, config=config)
    except ImportError:
        import code

        code.interact(banner=banner, local=namespace)


@entrypoint.command()
def schema():
    """Print the OVN schema."""
    print(OVNClient().import_schema().model_dump_json(indent=2))
