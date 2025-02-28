# Copyright (c) 2024-2025 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the LICENSE file.
# Initially written by Jeremy Schulman at https://github.com/jeremyschulman/aio-eapi
"""asynceapi module exceptions."""

from __future__ import annotations

from typing import TYPE_CHECKING

import httpx

from ._types import EapiCommandFormat

if TYPE_CHECKING:
    from ._types import EapiCommandResult, EapiComplexCommand, EapiJsonOutput, EapiSimpleCommand, EapiTextOutput, JsonRpcError


class EapiCommandError(RuntimeError):
    """Exception class for eAPI command errors.

    Attributes
    ----------
        failed: the failed command
        errmsg: a description of the failure reason
        errors: the command failure details
        passed: a list of command results of the commands that passed
        not_exec: a list of commands that were not executed
    """

    def __init__(
        self,
        failed: str,
        errors: list[str],
        errmsg: str,
        passed: list[EapiJsonOutput] | list[EapiTextOutput],
        not_exec: list[EapiSimpleCommand | EapiComplexCommand],
    ) -> None:
        """Initialize for the EapiCommandError exception."""
        self.failed = failed
        self.errmsg = errmsg
        self.errors = errors
        self.passed = passed
        self.not_exec = not_exec
        super().__init__()

    def __str__(self) -> str:
        """Return the error message associated with the exception."""
        return self.errmsg


class EapiMultipleCommandError(RuntimeError):
    """Exception class for multiple eAPI command errors when stopOnError is false."""

    def __init__(self, jsonrpc_error: JsonRpcError, commands: list[EapiSimpleCommand | EapiComplexCommand], ofmt: EapiCommandFormat) -> None:
        """Initialize the EapiMultipleCommandError exception."""
        self.code = jsonrpc_error["code"]
        self.message = jsonrpc_error["message"]
        self.data = jsonrpc_error["data"]
        self.commands = commands
        self.ofmt = ofmt
        self.results = self._process_results()
        super().__init__()

    def _process_results(self) -> dict[int, EapiCommandResult]:
        """Process and normalize the command results."""
        results = {}

        for i, (cmd, data) in enumerate(zip(self.commands, self.data)):
            result: EapiCommandResult = {
                "command": cmd,
                "output": None,
                "errors": [],
                "success": True,
            }

            # Handle different response formats and error cases
            if isinstance(data, dict):
                if "errors" in data:
                    result["errors"] = data["errors"]
                    result["success"] = False

                if self.ofmt == EapiCommandFormat.TEXT and "output" in data:
                    result["output"] = data["output"]
                else:
                    # For JSON format
                    result["output"] = data

            # Handle JSON string responses (serialized JSON)
            elif isinstance(data, str):
                try:
                    from json import JSONDecodeError, loads

                    result["output"] = loads(data)
                except (JSONDecodeError, TypeError):
                    # If it's not valid JSON, store as is
                    result["output"] = data

            results[i] = result

        return results

    def __str__(self) -> str:
        """Return the error message associated with the exception."""
        return self.message


# alias for exception during sending-receiving
EapiTransportError = httpx.HTTPStatusError
