import os
import click

from nornir import InitNornir

from nornir_dsl.runner import get_runner
from nornir_dsl.inventory import get_inventory

from rich.console import Console
from rich.pretty import Pretty
from rich.table import Table


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
@click.argument("filter_str")
@click.option("--vars", is_flag=True, help="Output all vars")
@click.pass_obj
def inv(nornir, filter_str, vars):
    """inv FILTER
    
    FILTER should be a Nornir Advanced filter\n

    Example:
    \"F(platform__any=['linux', 'windows'] & F(testbed='tb100')\"
    """
    filtered = get_inventory(nornir, filter_str)
    
    inv_table = Table()
    inv_table.add_column('Host')
    inv_table.add_column('Attrs')
    inv_table.add_column('Data')

    for host, host_data in filtered.inventory.hosts.items():
        host_attrs = {
            'hostname': host_data.hostname,
            'platform': host_data.platform,
            'password': host_data.password
        }

        inv_table.add_row(
            host,
            Pretty(host_attrs),
            Pretty(host_data.data)
        )

    Console().print(inv_table)