import click
import sys
import time
import os

from cses.cli import cli
from cses.api import API
from cses.db import DB
from cses.commands.tasks import pass_course
from cses.commands.tasks import pass_task
from cses.tasks import detect_type, languages


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
    lang = detect_type(file)
    if lang == None:
        ctx.fail("Cound not detect the language")
    lang = lang.name
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
                click.echo("#{}: {}".format(ind+1, test["status"]))
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
    db.close()
    click.edit(filename=file)


@cli.command()
@click.pass_context
@pass_course
@pass_task
@click.option("--fail-fast", "-f", is_flag=True)
def test(ctx, course, task, fail_fast):
    "Test the task locally"
    db = ctx.ensure_object(DB)
    api = ctx.ensure_object(API)
    if not db.files or course not in db.files or task not in db.files[course]:
        ctx.fail("No file associated with that task")
    fname = db.files[course][task]
    type = detect_type(fname)
    if type == None:
        ctx.fail("Could not detect the type")
    type.test(fname, api.tests(db.username, db.password, task, course),
              fail_fast)


@cli.command()
@click.pass_context
@pass_course
@pass_task
def run(ctx, course, task):
    "Run the file"
    db = ctx.ensure_object(DB)
    api = ctx.ensure_object(API)
    if not db.files or course not in db.files or task not in db.files[course]:
        ctx.fail("No file associated with that task")
    fname = db.files[course][task]
    type = detect_type(fname)
    if type == None:
        ctx.fail("Could not detect the type")
    type.user_run(fname)


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
    click.echo(", ".join([x.name for x in languages]))
    while True:
        sel = click.prompt("The language", default="C++")
        sel = sel.lower()
        for lang in languages:
            if lang.name.lower().startswith(sel):
                fname = lang.file_extensions[0]
                fcontent = lang.template
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
    except OSError as e:
        if e.errno != 17:
            raise
        pass

    if os.path.isfile(path):
        if click.confirm(("There is already a file"
                          "with the name {} "
                          "associate it instead?").format(path), default=True):
            return ctx.invoke(associate, filename=path)

    with open(path, "w+") as fp:
        fp.write(fcontent)
        click.echo("Wrote {}".format(path))
    ctx.invoke(associate, filename=path)
