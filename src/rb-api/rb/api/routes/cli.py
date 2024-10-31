"""
This router contains dynamic routes only! Do not add static routes here.
"""

import inspect
import time
from typing import Callable, Generator, Optional

import typer
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from makefun import with_signature
from rb.api.models import CommandResult
from rb.lib.stdout import Capturing  # type: ignore
from rb.lib.stdout import capture_stdout_as_generator

from rescuebox.main import app as rescuebox_app

cli_router = APIRouter()


def static_endpoint(callback: Callable, *args, **kwargs) -> CommandResult:
    """Execute a CLI command and return the result synchronously"""
    with Capturing() as stdout:
        try:
            result = callback(*args, **kwargs)
            return CommandResult(result=result, stdout=stdout, success=True, error=None)
        except Exception as e:
            return CommandResult(
                result=None,
                stdout=stdout,
                success=False,
                error=f"Typer CLI aborted {e}",
            )


def streaming_endpoint(callback: Callable, *args, **kwargs) -> Generator:
    """Execute a CLI command and stream the results"""
    line_buffer = ""
    for line in capture_stdout_as_generator(callback, *args, **kwargs):
        line_buffer += line
        result = CommandResult(
            result=line, stdout=line_buffer, success=True, error=None
        )
        yield result.model_dump_json()
        time.sleep(0.01)  # Sleep to prevent flooding the stream


def command_callback(command: typer.models.CommandInfo):
    """Create a FastAPI endpoint handler for a Typer CLI command"""
    # Get the original callback signature
    original_signature = inspect.signature(command.callback)
    # Add streaming parameter to signature
    new_params = list(original_signature.parameters.values())
    streaming_param = inspect.Parameter(
        "streaming",
        inspect.Parameter.KEYWORD_ONLY,
        default=False,
        annotation=Optional[bool],
    )
    new_params.append(streaming_param)
    new_signature = original_signature.replace(parameters=new_params)

    @with_signature(new_signature)
    def wrapper(*args, **kwargs):
        streaming = kwargs.pop("streaming", False)
        print(streaming)
        if streaming:
            return StreamingResponse(
                streaming_endpoint(command.callback, *args, **kwargs)
            )

        result = static_endpoint(command.callback, *args, **kwargs)
        if not result.success:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": result.error,
                    "stdout": result.stdout[-10:],  # Last 10 lines of output
                },
            )
        return result

    # Preserve original function metadata
    wrapper.__name__ = command.callback.__name__
    wrapper.__doc__ = command.callback.__doc__

    return wrapper


# Register routes for each plugin command
for plugin in rescuebox_app.registered_groups:
    router = APIRouter()

    for command in plugin.typer_instance.registered_commands:
        router.add_api_route(
            f"/{command.callback.__name__}",
            endpoint=command_callback(command),
            methods=["POST"],
            name=command.callback.__name__,
            response_model=CommandResult,
        )

    cli_router.include_router(router, prefix=f"/{plugin.name}", tags=[plugin.name])
