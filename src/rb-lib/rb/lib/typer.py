import inspect
import typing

import typer
from anytree import Node, RenderTree
from loguru import logger


def get_inputs_from_signature(signature: inspect.Signature) -> list[dict]:
    result = []
    for param in signature.parameters.values():
        data = {
            "name": param.name,
        }
        if typing.get_origin(param.annotation) == typing.Annotated:
            data["type"] = typing.get_args(param.annotation)[0].__name__
            data["help"] = typing.get_args(param.annotation)[1].help
        else:
            data["type"] = param.annotation.__name__

        if isinstance(param.default, typer.models.OptionInfo):
            data["default"] = param.default.default
            data["help"] = param.default.help
        elif isinstance(param.default, typer.models.ArgumentInfo):
            data["help"] = param.default.help
        elif param.default is not inspect.Parameter.empty:
            data["default"] = param.default
        else:
            data["default"] = None
        result.append(data)
    return result


def typer_app_to_tree(app: typer.Typer) -> dict:
    # Create root node
    root = Node("rescuebox", command=None, is_group=True)

    def add_commands_to_node(typer_app: typer.Typer, parent_node: Node):
        # Add groups recursively
        for group in getattr(typer_app, "registered_groups", []):
            group_node = Node(
                group.name,
                parent=parent_node,
                command=None,
                is_group=True,
            )
            # Recursively add any nested groups/commands
            add_commands_to_node(group.typer_instance, group_node)

        # Add commands at this level
        for command in getattr(typer_app, "registered_commands", []):
            command_name = getattr(command, "name", None) or command.callback.__name__

            Node(
                command_name,
                parent=parent_node,
                command=command,
                is_group=False,
                signature=inspect.signature(command.callback),
            )

    # Build the full tree structure
    add_commands_to_node(app, root)

    # Debug print the tree
    for pre, fill, node in RenderTree(root):
        logger.debug("%s%s" % (pre, node.name))

    def node_to_dict(node: Node) -> dict:
        result = {"name": node.name, "is_group": node.is_group, "help": None}
        if not node.is_group:
            # the endpoint is the path without the rescuebox root
            result["endpoint"] = "/" + "/".join([_.name for _ in node.path][1:])
            result["inputs"] = get_inputs_from_signature(node.signature)
            result["help"] = node.command.callback.__doc__
        if node.children:
            result["children"] = [node_to_dict(child) for child in node.children]
        return result

    # Convert the entire tree to dictionary format
    tree_dict = node_to_dict(root)
    return tree_dict
