from invoke import task


@task
def autodoc(c):
    c.run(
        "typer rescuebox/main.py utils docs --name rescuebox --output docs/Reference.md"
    )


@task
def serve(c):
    c.run("poetry run python -m src.rb-api.rb.api.main")


# TODO: Fix app bundling
@task
def bundle_api(c):
    c.run(
        "cd src/rb-api && poetry run pyinstaller --onefile --add-data 'rb/api/static:static' --add-data 'rb/api/templates:templates' --add-data 'rb/api/static/favicon.ico:static' rb/api/main.py"
    )


@task
def run_bundled_api(c):
    c.run("cd src/rb-api && ./dist/main")
