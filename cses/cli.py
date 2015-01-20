import click

from cses.shorthand_group import ShorthandGroup
from cses.db import DB
from cses.api import API

@click.command(cls=ShorthandGroup)
@click.version_option()
@click.pass_context
def cli(ctx):
    "Code Submission Evaluation System client"
    ctx.ensure_object(API)
    ctx.ensure_object(DB)
