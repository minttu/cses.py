import click

class ShorthandGroup(click.Group):
    def get_command(self, ctx, cmd_name):
        real = click.Group.get_command(self, ctx, cmd_name)
        if real is not None:
            return real
        matches = [x for x in self.list_commands(ctx)
                   if x.lower().startswith(cmd_name.lower())]
        if not matches:
            return None
        elif len(matches) == 1:
            return click.Group.get_command(self, ctx, matches[0])
        ctx.fail("Too many matches {}".format(", ".join(matches)))
