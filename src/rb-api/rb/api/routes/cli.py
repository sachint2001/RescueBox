import inspect
from typing import Callable, Optional

import typer
from fastapi import APIRouter, HTTPException
from makefun import with_signature
from rb.api.models import CommandResult
from rb.lib.stdout import Capturing  # type: ignore

from rescuebox.main import app as rescuebox_app

cli_router = APIRouter()


def static_endpoint(callback: Callable, *args, **kwargs) -> CommandResult:
    with Capturing() as stdout:
        try:
            result = callback(*args, **kwargs)
            success = True
            error = None
        except Exception as e:
            result = None
            success = False
            error = f"Typer CLI aborted {e}"
    return CommandResult(result=result, stdout=stdout, success=success, error=error)


def command_callback(command: typer.models.CommandInfo):
    # Get the original callback signature
    original_signature = inspect.signature(command.callback)

    # Modify the signature to include `streaming` and `help` parameters
    new_params = list(original_signature.parameters.values())
    new_params.append(
        inspect.Parameter(
            "streaming",
            inspect.Parameter.KEYWORD_ONLY,
            default=False,
            annotation=Optional[bool],
        )
    )
    new_params.append(
        inspect.Parameter(
            "help",
            inspect.Parameter.KEYWORD_ONLY,
            default=False,
            annotation=Optional[bool],
        )
    )
    new_signature = original_signature.replace(parameters=new_params)

    # Create a new function with the modified signature
    @with_signature(new_signature)
    def wrapper(*args, **kwargs):
        # Extract additional parameters
        help = kwargs.pop("help", False)

        if help:
            return CommandResult(
                result=command.callback.__doc__, stdout=[], success=True, error=None
            )

        # Call the static endpoint with the wrapped callback and arguments
        result = static_endpoint(command.callback, *args, **kwargs)
        if not result.success:
            # Return the last 10 lines of stdout if there's an error
            raise HTTPException(
                status_code=400,
                detail={"error": result.error, "stdout": result.stdout[-10:]},
            )
        return result

    wrapper.__name__ = command.callback.__name__
    wrapper.__doc__ = command.callback.__doc__

    return wrapper


for plugin in rescuebox_app.registered_groups:
    router = APIRouter()
    for command in plugin.typer_instance.registered_commands:
        router.add_api_route(
            f"/{command.callback.__name__}/",
            endpoint=command_callback(command),
            methods=["POST"],
            name=command.callback.__name__,
            response_model=CommandResult,
        )
    cli_router.include_router(router, prefix=f"/{plugin.name}", tags=[plugin.name])
