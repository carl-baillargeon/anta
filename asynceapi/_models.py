# Copyright (c) 2024-2025 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the LICENSE file.
"""Models for the asynceapi package."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Literal
from uuid import uuid4

from asynceapi._types import EapiCommandFormat, EapiComplexCommand, EapiJsonOutput, EapiSimpleCommand, EapiTextOutput, JsonRpc, JsonRpcResponse
from asynceapi.errors import EapiReponseError

if TYPE_CHECKING:
    from collections.abc import Iterator


@dataclass(frozen=True)
class EapiRequest:
    """Model for an eAPI request."""

    commands: list[EapiSimpleCommand | EapiComplexCommand]
    version: int | Literal["latest"] = "latest"
    format: EapiCommandFormat = EapiCommandFormat.JSON
    timestamps: bool = False
    auto_complete: bool = False
    expand_aliases: bool = False
    stop_on_error: bool = True
    id: str = field(default_factory=lambda: uuid4().hex)

    def to_jsonrpc(self) -> JsonRpc:
        """Return the JSON-RPC payload for the request."""
        return {
            "jsonrpc": "2.0",
            "method": "runCmds",
            "params": {
                "version": self.version,
                "cmds": self.commands,
                "format": self.format,
                "timestamps": self.timestamps,
                "autoComplete": self.auto_complete,
                "expandAliases": self.expand_aliases,
                "stopOnError": self.stop_on_error,
            },
            "id": self.id,
        }


@dataclass(frozen=True)
class EapiResponse:
    """Model for an eAPI response."""

    request_id: str
    _executed_count: int
    _results: dict[int, EapiCommandResult] = field(default_factory=dict)
    error_code: int | None = None
    error_message: str | None = None

    @property
    def success(self) -> bool:
        """Return True if the response has no errors."""
        return self.error_code is None

    @property
    def results(self) -> list[EapiCommandResult]:
        """Get all results as a list, orgered by command index."""
        return [self._results[i] for i in sorted(self._results.keys())]

    @property
    def executed_indexes(self) -> list[int]:
        """Return a list of indexes of commands that were executed."""
        return list(range(self._executed_count))

    @property
    def not_executed_indexes(self) -> list[int]:
        """Return a list of indexes of commands that were not executed."""
        return [i for i in self._results if i >= self._executed_count]

    @property
    def first_failed_index(self) -> int | None:
        """Return the index of the first failed command, or None if all succeeded."""
        for i in sorted(self._results.keys()):
            if not self._results[i].success:
                return i
        return None

    @property
    def failed_indexes(self) -> list[int]:
        """Return a list of indexes of failed commands."""
        return [i for i, result in self._results.items() if not result.success]

    @property
    def passed_indexes(self) -> list[int]:
        """Return a list of indexes of passed commands."""
        return [i for i, result in self._results.items() if result.success]

    def __len__(self) -> int:
        """Return the number of results."""
        return len(self._results)

    def __iter__(self) -> Iterator[tuple[int, EapiCommandResult]]:
        """Enable iteration over index, result pairs."""
        for index in sorted(self._results.keys()):
            yield index, self._results[index]

    def get_result(self, index: int) -> EapiCommandResult | None:
        """Get the result for a command by its index in the original request."""
        return self._results.get(index)

    def get_output(self, index: int) -> EapiJsonOutput | EapiTextOutput | None:
        """Get the output for a command by its index in the original request."""
        result = self.get_result(index)
        return result.output if result else None

    def get_errors(self, index: int) -> list[str] | None:
        """Get the errors for a command by its index in the original request."""
        result = self.get_result(index)
        return result.errors if result else None

    def was_executed(self, index: int) -> bool:
        """Check if a command was executed."""
        return index < self._executed_count

    @classmethod
    def from_jsonrpc(cls, response: JsonRpcResponse, request: EapiRequest, *, raise_on_error: bool = False) -> EapiResponse:
        """Build an EapiResponse from a JSON-RPC response."""
        has_error = "error" in response
        response_data = response["error"]["data"] if has_error else response["result"]

        # Handle case where we have fewer results than commands (stop_on_error=True)
        executed_count = min(len(response_data), len(request.commands))

        # Process the results we have
        results = {}
        for i in range(executed_count):
            cmd = request.commands[i]
            cmd_str = cmd["cmd"] if isinstance(cmd, dict) else cmd
            data = response_data[i]

            output = None
            errors = []
            success = True
            start_time = None
            duration = None

            # Parse the output based on the data type, no output when errors are present
            if isinstance(data, dict):
                if "errors" in data:
                    errors = data["errors"]
                    success = False
                else:
                    output = data["output"] if request.format == EapiCommandFormat.TEXT and "output" in data else data

                # Add timestamps if available
                if request.timestamps and "_meta" in data:
                    meta = data.pop("_meta")
                    start_time = meta["execStartTime"]
                    duration = meta["execDuration"]

            elif isinstance(data, str):
                # Handle JSON string responses (serialized JSON)
                try:
                    from json import JSONDecodeError, loads

                    output = loads(data)
                except (JSONDecodeError, TypeError):
                    # If it's not valid JSON, store as is
                    output = data

            results[i] = EapiCommandResult(
                command=cmd_str,
                output=output,
                errors=errors,
                success=success,
                start_time=start_time,
                duration=duration,
            )

        # If stop_on_error is True and we have an error, indicate commands not executed
        if has_error and request.stop_on_error and executed_count < len(request.commands):
            for i in range(executed_count, len(request.commands)):
                cmd = request.commands[i]
                cmd_str = cmd["cmd"] if isinstance(cmd, dict) else cmd
                results[i] = EapiCommandResult(
                    command=cmd_str, output=None, errors=["Command not executed due to previous error"], success=False, was_executed=False
                )

        response_obj = cls(
            request_id=response["id"],
            _results=results,
            _executed_count=executed_count,
            error_code=response["error"]["code"] if has_error else None,
            error_message=response["error"]["message"] if has_error else None,
        )

        if raise_on_error and has_error:
            raise EapiReponseError(response_obj)

        return response_obj


@dataclass(frozen=True)
class EapiCommandResult:
    """Model for an eAPI command result."""

    command: str
    output: EapiJsonOutput | EapiTextOutput | None
    errors: list[str] = field(default_factory=list)
    success: bool = True
    was_executed: bool = True
    start_time: float | None = None
    duration: float | None = None
