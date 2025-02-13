import inspect
import time
import logging
from typing import Callable, Generator, Optional, Any
from pydantic import BaseModel

import typer
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from makefun import with_signature
from rb.lib.stdout import Capturing  # type: ignore
from rb.lib.stdout import capture_stdout_as_generator
from rb.api.models import ResponseBody, TextResponse

from rescuebox.main import app as rescuebox_app

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

cli_router = APIRouter()


def static_endpoint(callback: Callable, *args, **kwargs) -> ResponseBody:
    """Execute a CLI command and return the result synchronously"""
    with Capturing() as stdout:
        try:
            logger.debug(f"Executing CLI command: {callback.__name__} with args={args}, kwargs={kwargs}")
            result = callback(*args, **kwargs)  # Ensure this returns a valid Pydantic model
            logger.debug(f"CLI command output: {result}")

            if isinstance(result, BaseModel):  # Ensure it's a valid Pydantic model
                return ResponseBody(root=result)
            raise ValueError(f"Invalid return type from Typer command: {type(result)}")
        except Exception as e:
            logger.error(f"Error executing CLI command: {e}")
            raise HTTPException(
                status_code=400,
                detail={"error": f"Typer CLI aborted {e}", "stdout": stdout[-10:]},
            )


def streaming_endpoint(callback: Callable, *args, **kwargs) -> Generator:
    """Execute a CLI command and stream the results"""

    logger.debug(f"🚀 Streaming started for command: {callback.__name__} with args={args}, kwargs={kwargs}")

    for line in capture_stdout_as_generator(callback, *args, **kwargs):
        response = ResponseBody(root=TextResponse(value=line)).model_dump_json()
        
        logger.debug(f"Streaming output: {response}")  # Debug log for each response

        yield response  # Ensure it's yielding responses
        time.sleep(0.01)



def command_callback(command: typer.models.CommandInfo):
    """Create a FastAPI endpoint handler for a Typer CLI command with `ResponseBody`"""

    original_signature = inspect.signature(command.callback)
    new_params = []

    # Convert Typer CLI arguments to FastAPI-compatible query/body parameters
    for param in original_signature.parameters.values():
        if param.default is inspect.Parameter.empty:  # Required argument
            param = param.replace(default=Query(..., description=f"Required parameter {param.name}"))
        elif param.default is Ellipsis:  # Typer required argument
            param = param.replace(default=Query(..., description=f"Required parameter {param.name}"))
        new_params.append(param)

    streaming_param = inspect.Parameter(
        "streaming",
        inspect.Parameter.KEYWORD_ONLY,
        default=False,
        annotation=Optional[bool],
    )
    new_params.append(streaming_param)

    new_signature = original_signature.replace(parameters=new_params)

    @with_signature(new_signature)
    def wrapper(*args, **kwargs) -> ResponseBody:
        logger.debug(f"FastAPI wrapper called for {command.callback.__name__} with args={args}, kwargs={kwargs}")

        streaming = kwargs.pop("streaming", False)
        if streaming:
            return StreamingResponse(
                streaming_endpoint(command.callback, *args, **kwargs)
            )

        return static_endpoint(command.callback, *args, **kwargs)

    wrapper.__name__ = command.callback.__name__
    wrapper.__doc__ = command.callback.__doc__

    return wrapper


# Register routes for each plugin command
for plugin in rescuebox_app.registered_groups:
    router = APIRouter()

    for command in plugin.typer_instance.registered_commands:
        logger.debug(f"Registering FastAPI route for CLI command: {command.callback.__name__}")
        
        router.add_api_route(
            f"/{command.callback.__name__}",
            endpoint=command_callback(command),
            methods=["POST"],
            name=command.callback.__name__,
            response_model=ResponseBody,
        )

    cli_router.include_router(router, prefix=f"/{plugin.name}", tags=[plugin.name])
