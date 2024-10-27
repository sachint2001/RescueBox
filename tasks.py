from invoke import task


@task
def autodoc(c):
    c.run("typer rescuebox/main.py utils docs --name rescuebox --output docs/Reference.md")
