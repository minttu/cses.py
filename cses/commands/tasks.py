import click
from functools import wraps

from cses.cli import cli
from cses.api import API
from cses.db import DB
from cses.shorthand_group import ShorthandGroup
from cses.commands.courses import pass_course


@cli.group(cls=ShorthandGroup)
def tasks():
    "Stuff about tasks"


def pass_exercise(f):
    @wraps(f)
    def wrapper(*args, **kwds):
        ctx = args[0]
        db = ctx.ensure_object(DB)
        api = ctx.ensure_object(API)

        task = db.task
        if task is None:
            ctx.invoke(select)
            task = db.task

        args = args + (task,)
        return f(*args, **kwds)
    return wrapper


def show_task(tasks, id):
    click.echo("{}: {}".format(tasks[id]["id"],
                               tasks[id]["name"]))


def show_tasks(tasks, id=None):
    section = None
    for task in tasks:
        if task["section"] != section:
            coursename = "{} ({})".format(task["section"], task["deadline"])
            if section != None:
                click.echo()
            click.echo(coursename)
            click.echo("=" * len(coursename))
            section = task["section"]
        click.echo("{}: {} {}".format(task["id"],
                                      task["name"],
                                      "(Selected)" if id is int(task["id"]) else ""))


@tasks.command()
@click.pass_context
@pass_course
def show(ctx, course):
    "Lists the various tasks available in the course"
    db = ctx.ensure_object(DB)
    api = ctx.ensure_object(API)

    show_tasks(api.tasks(course), db.task)


@tasks.command()
@click.pass_context
@pass_course
def select(ctx, course):
    "Allows you to select the task"
    db = ctx.ensure_object(DB)
    api = ctx.ensure_object(API)

    tasks = api.tasks(course)
    id = db.task
    valid_ids = [int(x["id"]) for x in tasks]
    show_tasks(tasks, id)

    while 1:
        id = click.prompt("Enter a task id", default=id, type=int)
        if id not in valid_ids:
            if not click.confirm("Invalid task id, try again", default=True):
                ctx.fail("Could not select a task")
        else:
            break

    db.task = id


@tasks.command()
@click.pass_context
@pass_course
def next(ctx, course, dir=1):
    "Goes to the next task if one is available"
    db = ctx.ensure_object(DB)
    api = ctx.ensure_object(API)

    tasks = api.tasks(course)
    id = db.task
    if id == None:
        if len(tasks) > 0:
            id = int(tasks[0]["id"])
        else:
            ctx.fail("Course has no tasks")
        show_task(tasks, 0)
    else:
        pos = -1
        for i, task in enumerate(tasks):
            if int(task["id"]) is id:
                pos = i
                break
        if pos == -1:
            ctx.fail("I don't know how you managed this")
        new = pos + dir
        if new < len(tasks) and new >= 0:
            db.task = int(tasks[pos + dir]["id"])
        else:
            ctx.fail("You are at the end of the available tasks")
        show_task(tasks, new)


@tasks.command()
@click.pass_context
def previous(ctx):
    "Goes to the previous task"
    ctx.invoke(next, dir=-1)
