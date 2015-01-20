import click

from cses.cli import cli
from cses.api import API
from cses.db import DB

@cli.command()
@click.pass_context
def configure(ctx):
    "Used to set the username and password that you use with cses.fi"
    api = ctx.ensure_object(API)
    db = ctx.ensure_object(DB)
    username = db.username
    while 1:
        username = click.prompt("Username", default=username)
        password = click.prompt("Password", hide_input=True)
        resp = api.auth(username, password)
        if resp["success"] == "yes":
            break
        else:
            if not click.confirm("Auth faield, try again", default=True):
                ctx.fail("Could not authenticate")
    db.username = username
    db.password = password
