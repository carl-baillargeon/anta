# Copyright (c) 2023-2024 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the LICENSE file.
"""Utils functions to use with anta.cli.debug module."""

from __future__ import annotations

import functools
import logging
from typing import TYPE_CHECKING, Any, Callable

import click

from anta.cli.utils import ExitCode, inventory_options

if TYPE_CHECKING:
    from anta.inventory import AntaInventory

logger = logging.getLogger(__name__)


def debug_options(f: Callable[..., Any]) -> Callable[..., Any]:
    """Click common options required to execute a command on a specific device."""

    @inventory_options
    @click.option(
        "--ofmt",
        type=click.Choice(["json", "text"]),
        default="json",
        help="EOS eAPI format to use. can be text or json",
    )
    @click.option(
        "--version",
        "-v",
        type=click.Choice(["1", "latest"]),
        default="latest",
        help="EOS eAPI version",
    )
    @click.option("--revision", "-r", type=int, help="eAPI command revision", required=False)
    @click.option("--device", "-d", type=str, required=True, help="Device from inventory to use")
    @click.pass_context
    @functools.wraps(f)
    def wrapper(
        ctx: click.Context,
        *args: tuple[Any],
        inventory: AntaInventory,
        tags: set[str] | None,
        device: str,
        **kwargs: Any,
    ) -> Any:
        # TODO: @gmuloc - tags come from context https://github.com/arista-netdevops-community/anta/issues/584
        # pylint: disable=unused-argument
        # ruff: noqa: ARG001
        try:
            d = inventory[device]
        except KeyError as e:
            message = f"Device {device} does not exist in Inventory"
            logger.error(e, message)
            ctx.exit(ExitCode.USAGE_ERROR)
        return f(*args, device=d, **kwargs)

    return wrapper
