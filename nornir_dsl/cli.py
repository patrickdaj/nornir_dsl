import click

from nornir import InitNornir

from nornir_dsl.runner import get_runner
from nornir_dsl.inventory import get_inventory


@click.group()
@click.option(
    "--config",
    default=lambda: os.environ.get("NORNIR_CONFIG", ""),
    type=click.Path(exists=True, file_okay=True),
    help="Path to Nornir config file",
)
@click.pass_context
def cli(ctx, config):
    ctx.obj = InitNornir(config_file=config)


@cli.command()
@click.argument(
    "playbook",
    type=click.File("r"),
)
@click.option("--step", is_flag=True, help="Step through playbook")
@click.pass_obj
def run(nornir, playbook, step):
    """Run PLAYBOOK"""
    get_runner(nornir, playbook, step)


@cli.command()
@click.pass_obj
def inv(ctx):
    get_inventory(nornir)
