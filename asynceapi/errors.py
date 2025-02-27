# Copyright (c) 2024-2025 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the LICENSE file.
# Initially written by Jeremy Schulman at https://github.com/jeremyschulman/aio-eapi
"""asynceapi module exceptions."""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal

import httpx

if TYPE_CHECKING:
    from ._types import EapiComplexCommand, EapiJsonOutput, EapiSimpleCommand, EapiTextOutput


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
        """Initialize the EapiCommandError exception."""
        self.failed = failed
        self.errmsg = errmsg
        self.errors = errors
        self.passed = passed
        self.not_exec = not_exec
        super().__init__()

    def __str__(self) -> str:
        """Return the error message associated with the exception."""
        return self.errmsg

class EapiCommandsError(RuntimeError):
    """Exception class for eAPI command execution errors with multiple commands using the `stopOnError: false` parameter."""

    def __init__(self, response: dict[str, Any], commands: list[str | dict[str, Any]], ofmt: Literal["text", "json"] = "json") -> None:
        """Initialize the EapiCommandsError exception."""
        self.jsonrpc_error_message = response["error"]["message"]
        self.data = response["error"]["data"]
        self.commands = commands
        self.ofmt = ofmt

        # Store processed results for each command
        self.results = self._process_results()

        super().__init__(self.jsonrpc_error_message)

    def _process_results(self) -> dict[int, dict[str, Any]]:
        """Process and normalize the command results."""
        results = {}

        for i, (cmd, data) in enumerate(zip(self.commands, self.data, strict=True)):
            result = {
                "command": cmd,
                "output": None,
                "errors": [],
                "success": True,
            }

            # Handle different response formats and error cases
            if isinstance(data, dict):
                # Command returned structured data or error
                if "errors" in data:
                    result["errors"] = data["errors"]
                    result["success"] = False

                if self.ofmt == "text" and "output" in data:
                    result["output"] = data["output"]
                else:
                    # For JSON format or any other dict response
                    result["output"] = data

            # TODO: Check with eAPI team if this is normal to have a string response on certain commands
            elif isinstance(data, str):
                # Handle string responses (serialized JSON)
                try:
                    from json import JSONDecodeError, loads
                    result["output"] = loads(data)
                except (JSONDecodeError, TypeError):
                    # If it's not valid JSON, store as is
                    result["output"] = data

            results[i] = result

        return results

    def get_result(self, index: int) -> dict[str, Any]:
        """Get the processed result for a command by its index."""
        if index in self.results:
            return self.results[index]
        msg = f"Command index {index} is out of range"
        raise IndexError(msg)

    def __str__(self) -> str:
        """Return a string representation of the exception."""
        parts = [f"EapiCommandsError: {self.jsonrpc_error_message}"]

        for i, result in self.results.items():
            status = "✓" if result["success"] else "✗"
            parts.append(f"  [{i}] {status} {result['command']}")
            parts.extend([f"      Error: {err}" for err in result["errors"] if not result["success"]])
        return "\n".join(parts)

# alias for exception during sending-receiving
EapiTransportError = httpx.HTTPStatusError
