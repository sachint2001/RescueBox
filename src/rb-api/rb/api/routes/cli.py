import inspect
import time
import json
import logging
from typing import Callable, Generator, Optional, Any
from pydantic import BaseModel

import typer
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from makefun import with_signature
from rb.lib.stdout import Capturing  # type: ignore
from rb.lib.stdout import capture_stdout_as_generator
from rb.api.models import (
    ResponseBody,
    FileResponse,
    DirectoryResponse,
    MarkdownResponse,
    TextResponse,
    BatchFileResponse,
    BatchTextResponse,
    BatchDirectoryResponse,
)

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
    """Execute a CLI command and stream the results with proper response handling"""

    logger.debug(f"🚀 Streaming started for command: {callback.__name__} with args={args}, kwargs={kwargs}")

    for line in capture_stdout_as_generator(callback, *args, **kwargs):
        try:
            # Attempt to parse the output if it's JSON-like
            parsed_line = json.loads(line) if isinstance(line, str) and line.lstrip().startswith("{") else line

            response_body = None

            # Dynamically determine the response type
            if isinstance(parsed_line, dict):
                if "texts" in parsed_line:  # Matches BatchTextResponse structure
                    response_body = ResponseBody(root=BatchTextResponse(**parsed_line))
                elif "files" in parsed_line:  # Matches BatchFileResponse structure
                    response_body = ResponseBody(root=BatchFileResponse(**parsed_line))
                elif "directories" in parsed_line:  # Matches BatchDirectoryResponse
                    response_body = ResponseBody(root=BatchDirectoryResponse(**parsed_line))
                elif "path" in parsed_line:  # Matches FileResponse or DirectoryResponse
                    response_body = ResponseBody(
                        root=DirectoryResponse(**parsed_line) if parsed_line.get("is_directory") else FileResponse(**parsed_line)
                    )
                elif "markdown" in parsed_line:  # Matches MarkdownResponse
                    response_body = ResponseBody(root=MarkdownResponse(**parsed_line))
                else:
                    response_body = ResponseBody(root=TextResponse(value=str(parsed_line)))

            elif isinstance(parsed_line, list):
                response_body = ResponseBody(root=BatchTextResponse(texts=[TextResponse(value=str(item)) for item in parsed_line]))

            else:
                # Default to TextResponse if it's a simple string
                response_body = ResponseBody(root=TextResponse(value=str(parsed_line)))

            response_json = response_body.model_dump_json()
            logger.debug(f"Streaming output: {response_json}")
            yield response_json  # Yield properly formatted JSON response

        except Exception as e:
            logger.error(f"Error processing streaming output: {e}")
            yield ResponseBody(root=TextResponse(value=f"Error: {str(e)}")).model_dump_json()

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
