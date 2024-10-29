from invoke import task


@task
def autodoc(c):
    c.run(
        "typer rescuebox/main.py utils docs --name rescuebox --output docs/Reference.md"
    )


@task
def serve(c):
    c.run("poetry run python -m src.rb-api.rb.api.main")
