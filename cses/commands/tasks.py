import click
import sys
import time
import os
from functools import wraps

from cses.cli import cli
from cses.api import API
from cses.db import DB
from cses.filetype import FileType
from cses.shorthand_group import ShorthandGroup
from cses.commands.courses import pass_course


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
    selected = "(Selected)" if id is task["id"] else ""
    status = ""
    if "status" in task:
        status = " (" + task["status"].capitalize() + ")"
    click.echo("{}: {}{} [{}] {}".format(task["id"],
                                         task["name"],
                                         status,
                                         fname,
                                         selected))


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
            click.echo(coursename)
            click.echo("=" * len(coursename))
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
    show_tasks(tasks, id, db.get("files", {}).get(course, {}))

    while 1:
        id = click.prompt("Enter a task id", default=id, type=int)
        if id not in valid_ids:
            if not click.confirm("Invalid task id, try again", default=True):
                ctx.fail("Could not select a task")
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
            ctx.fail("Course has no tasks")
        show_task(tasks, 0, 0, db.files[course])
    else:
        pos = -1
        for i, task in enumerate(tasks):
            if task["id"] is id:
                pos = i
                break
        if pos == -1:
            ctx.fail("I don't know how you managed this")
        new = pos + dir
        if new < len(tasks) and new >= 0:
            id = tasks[pos + dir]["id"]
        else:
            ctx.fail("You are at the end of the available tasks")
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
@click.argument("filename",
                type=click.Path(exists=True,
                                dir_okay=False,
                                resolve_path=True))
def associate(ctx, course, task, filename):
    "Associates a file with the current task"
    db = ctx.ensure_object(DB)
    api = ctx.ensure_object(API)
    if not db.files:
        db.files = {}
    if course not in db.files:
        db.files[course] = {}
    db.files[course][task] = filename


@cli.command()
@click.pass_context
@pass_course
@pass_task
def submit(ctx, course, task):
    "Submits the current tasks code to the server"
    db = ctx.ensure_object(DB)
    api = ctx.ensure_object(API)

    if not db.files or course not in db.files or task not in db.files[course]:
        ctx.fail("No file associated with that task")

    file = db.files[course][task]
    lang = FileType.detect(file)
    code = ""
    with open(file, "r") as fp:
        code = fp.read()

    sendreq = api.send(db.username, db.password, task, course, lang, code)
    if sendreq["result"] == "error":
        ctx.fail(sendreq["message"])

    ticket = sendreq["ticket"]
    click.echo("Submission ID: {}, waiting for results...".format(ticket))

    old_status = ""
    lineclear = "\033[2K\033[80D"
    while True:
        resreq = api.result(db.username, db.password, ticket)
        if resreq["result"] == "error":
            sys.stdout.write(lineclear)
            sys.stdout.flush()
            ctx.fail(sendreq["message"])
        status = resreq["status"]

        if status == "COMPILE ERROR":
            sys.stdout.write("\n")
            ctx.fail("Compile error")

        elif status == "READY":
            click.echo("{}Test results".format(lineclear))
            click.echo("============")
            for ind, test in enumerate(resreq["test"]):
                click.echo("{}: {}".format(ind, test["status"]))
            click.echo("Score: {}".format(resreq["score"]))
            break

        if old_status != status:
            sys.stdout.write("{}Status: {}".format(lineclear, status))
            sys.stdout.flush()
            old_status = status

        time.sleep(1)


@cli.command()
@click.pass_context
@pass_course
@pass_task
def show(ctx, course, task):
    "Shows the tasks description in a browser"
    db = ctx.ensure_object(DB)
    api = ctx.ensure_object(API)

    courses = api.courses()
    name = ""
    for i in courses:
        if i["id"] == course:
            name = i["nick"]
            break
    else:
        ctx.fail("Could not field the course")

    click.launch("http://cses.fi/{}/task/{}/".format(name, task))


@cli.command()
@click.pass_context
@pass_course
@pass_task
def edit(ctx, course, task):
    "Edits the current tasks file"
    db = ctx.ensure_object(DB)

    if not db.files or course not in db.files or task not in db.files[course]:
        ctx.fail("No file associated with that task")

    file = db.files[course][task]
    click.edit(filename=file)


@cli.command()
@click.pass_context
@pass_course
@pass_task
def create(ctx, course, task):
    "Creates a file for the current task"
    db = ctx.ensure_object(DB)
    api = ctx.ensure_object(API)

    if task in db.files[course]:
        if not click.confirm("There is already a file, change the file"):
            return

    fname = ""
    fcontent = ""
    click.echo("Available languages:")
    click.echo(", ".join([x[0] for x in FileType.data]))
    while True:
        sel = click.prompt("The language", default="C++")
        sel = sel.lower()
        for lang in FileType.data:
            if lang[0].lower().startswith(sel):
                fname = lang[1][0]
                fcontent = lang[2]
                break
        else:
            if not click.confirm("Can't understand you, try again",
                                 default=True):
                ctx.fail("Could not select language")
            else:
                continue
        break

    tasks = api.tasks(course, db.username, db.password)
    for i in tasks:
        if i["id"] == task:
            fcontent = fcontent.format(i["name"])
            fname = i["name"].replace(" ", "_") + "." + fname
            break
    else:
        ctx.fail("Could not find the task")

    if course not in db.paths:
        ctx.fail("The course doesn't have a default path")

    path = os.path.join(db.paths[course], fname)
    try:
        os.makedirs(os.path.split(path)[0])
    except FileExistsError:
        pass

    if os.path.isfile(path):
        if click.confirm(("There is already a file"
                          "with the name {} "
                          "associate it instead?").format(path), default=True):
            return ctx.invoke(associate, filename=path)

    with open(path, "w") as fp:
        fp.write(fcontent)
    ctx.invoke(associate, filename=path)
