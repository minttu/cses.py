import builtins
import click
import sys
import time
import os
from functools import wraps

from cses.cli import cli
from cses.api import API
from cses.db import DB
from cses.shorthand_group import ShorthandGroup
from cses.commands.courses import pass_course
from cses.tasks import detect_type, languages
from cses.ui import clr


@cli.group(cls=ShorthandGroup)
def tasks():
    "Stuff about tasks"


def pass_task(f):
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


def show_task(tasks, pos, id=None, files={}):
    task = tasks[pos]
    fname = ""
    if task["id"] in files:
        fname = files[task["id"]]
    status = []
    if id is task["id"]:
        status.append("\033[4mSelected\033[0m")
    if "status" in task:
        task_status = task["status"].capitalize()
        col = 3
        if task_status[0] == "S":
            col = 2
        elif task_status[0] == "A":
            col = 1
        task_status = "\033[3{}m{}\033[0m".format(col, task_status)
        status.append(task_status)
    status = ", ".join(status)
    click.echo("{0}: {1} ({3}) [{2}]".format(task["id"],
                                           task["name"],
                                           fname,
                                           status))


def show_tasks(tasks, id=None, files={}):
    section = None
    if "result" in tasks:
        click.echo(tasks["message"])
        return
    for ind, task in enumerate(tasks):
        if task["section"] != section:
            coursename = "{} ({})".format(task["section"], task["deadline"])
            if section != None:
                click.echo()
            click.echo(clr(coursename))
            section = task["section"]
        show_task(tasks, ind, id, files)


@tasks.command()
@click.pass_context
@pass_course
def show(ctx, course):
    "Lists the various tasks available in the course"
    db = ctx.ensure_object(DB)
    api = ctx.ensure_object(API)

    show_tasks(api.tasks(course,
                         db.username,
                         db.password), db.task, db.files[course])


@tasks.command()
@click.pass_context
@pass_course
def select(ctx, course):
    "Allows you to select the task"
    db = ctx.ensure_object(DB)
    api = ctx.ensure_object(API)

    tasks = api.tasks(course, db.username, db.password)
    id = db.task
    valid_ids = [x["id"] for x in tasks]
    show_tasks(tasks, id, db.files.get(course, {}))

    while 1:
        id = click.prompt(clr("Enter a task id"), default=id, type=int)
        if id not in valid_ids:
            if not click.confirm(clr("Invalid task id, try again"), default=True):
                ctx.fail(clr("Could not select a task"))
        else:
            break

    db.task = id


@cli.command()
@click.pass_context
@pass_course
def next(ctx, course, dir=1):
    "Goes to the next task if one is available"
    db = ctx.ensure_object(DB)
    api = ctx.ensure_object(API)

    tasks = api.tasks(course, db.username, db.password)
    id = db.task
    if id == None:
        if len(tasks) > 0:
            id = tasks[0]["id"]
        else:
            ctx.fail(clr("Course has no tasks"))
        show_task(tasks, 0, 0, db.files[course])
    else:
        pos = -1
        for i, task in enumerate(tasks):
            if task["id"] is id:
                pos = i
                break
        if pos == -1:
            ctx.fail(clr("I don't know how you managed this"))
        new = pos + dir
        if new < len(tasks) and new >= 0:
            id = tasks[pos + dir]["id"]
        else:
            ctx.fail(clr("You are at the end of the available tasks"))
        show_task(tasks, new, id, db.files[course])
    db.task = id


@cli.command()
@click.pass_context
def previous(ctx):
    "Goes to the previous task"
    ctx.invoke(next, dir=-1)


@cli.command()
@click.pass_context
@pass_course
@pass_task
def current(ctx, course, task):
    "Shows the current task"
    db = ctx.ensure_object(DB)
    api = ctx.ensure_object(API)

    tasks = api.tasks(course,
                      db.username,
                      db.password)

    pos = 0
    for ind, tsk in enumerate(tasks):
        if tsk["id"] == task:
            pos = ind
            break

    show_task(tasks,
              pos,
              db.task,
              db.files[course])
