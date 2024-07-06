# Copyright (c) 2023-2024 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the LICENSE file.
"""ANTA runner function."""

from __future__ import annotations

import asyncio
import logging
import os
import resource
from dataclasses import dataclass, field
from itertools import chain
from multiprocessing import Pool, cpu_count
from typing import TYPE_CHECKING

from more_itertools import distribute

from anta import GITHUB_SUGGESTION
from anta.device import AsyncEOSDevice
from anta.logger import anta_log_exception, exc_to_str
from anta.models import AntaTest
from anta.tools import Catchtime, cprofile

if TYPE_CHECKING:

    from anta.catalog import AntaCatalog, AntaTestDefinition
    from anta.device import AntaDevice
    from anta.inventory import AntaInventory
    from anta.result_manager import ResultManager
    from anta.result_manager.models import TestResult

logger = logging.getLogger(__name__)

DEFAULT_NOFILE = 16384


def adjust_rlimit_nofile() -> tuple[int, int]:
    """Adjust the maximum number of open file descriptors for the ANTA process.

    The limit is set to the lower of the current hard limit and the value of the ANTA_NOFILE environment variable.

    If the `ANTA_NOFILE` environment variable is not set or is invalid, `DEFAULT_NOFILE` is used.

    Returns
    -------
        tuple[int, int]: The new soft and hard limits for open file descriptors.
    """
    try:
        nofile = int(os.environ.get("ANTA_NOFILE", DEFAULT_NOFILE))
    except ValueError as exception:
        logger.warning("The ANTA_NOFILE environment variable value is invalid: %s\nDefault to %s.", exc_to_str(exception), DEFAULT_NOFILE)
        nofile = DEFAULT_NOFILE

    limits = resource.getrlimit(resource.RLIMIT_NOFILE)
    logger.debug("Initial limit numbers for open file descriptors for the current ANTA process: Soft Limit: %s | Hard Limit: %s", limits[0], limits[1])
    nofile = min(limits[1], nofile)
    logger.debug("Setting soft limit for open file descriptors for the current ANTA process to %s", nofile)
    resource.setrlimit(resource.RLIMIT_NOFILE, (nofile, limits[1]))
    return resource.getrlimit(resource.RLIMIT_NOFILE)


def log_cache_statistics(devices: list[AntaDevice]) -> None:
    """Log cache statistics for each device in the inventory.

    Parameters
    ----------
        devices: List of devices in the inventory.
    """
    for device in devices:
        if device.cache_statistics is not None:
            msg = (
                f"Cache statistics for '{device.name}': "
                f"{device.cache_statistics['cache_hits']} hits / {device.cache_statistics['total_commands_sent']} "
                f"command(s) ({device.cache_statistics['cache_hit_ratio']})"
            )
            logger.info(msg)
        else:
            logger.info("Caching is not enabled on %s", device.name)


async def setup_inventory(inventory: AntaInventory, tags: set[str] | None, devices: set[str] | None, *, established_only: bool) -> AntaInventory | None:
    """Set up the inventory for the ANTA run.

    Parameters
    ----------
        inventory: AntaInventory object that includes the device(s).
        tags: Tags to filter devices from the inventory.
        devices: Devices on which to run tests. None means all devices.

    Returns
    -------
        AntaInventory | None: The filtered inventory or None if there are no devices to run tests on.
    """
    if len(inventory) == 0:
        logger.info("The inventory is empty, exiting")
        return None

    # Filter the inventory based on the CLI provided tags and devices if any
    selected_inventory = inventory.get_inventory(tags=tags, devices=devices) if tags or devices else inventory

    with Catchtime(logger=logger, message="Connecting to devices"):
        # Connect to the devices
        await selected_inventory.connect_inventory()

    # Remove devices that are unreachable
    selected_inventory = selected_inventory.get_inventory(established_only=established_only)

    # If there are no devices in the inventory after filtering, exit
    if not selected_inventory.devices:
        msg = f'No reachable device {f"matching the tags {tags} " if tags else ""}was found.{f" Selected devices: {devices} " if devices is not None else ""}'
        logger.warning(msg)
        return None

    return selected_inventory

@dataclass
class AntaDeviceHolder:
    """Dataclass to hold the device information and the tests to run on it.

    This is used to transport the device information and the tests to run on it to the worker processes.

    FIXME: This should probably be in AntaDevice
    """

    name: str
    hw_model: str
    tags: list[str]
    is_online: bool
    established: bool
    host: str
    username: str
    password: str
    enable: bool
    enable_password: str
    port: int
    ssh_port: int
    timeout: float
    insecure: bool
    disable_cache: bool
    tests: set[AntaTestDefinition] = field(default_factory=set)


def prepare_tests(
        inventory: AntaInventory,
        catalog: AntaCatalog,
        tests: set[str] | None,
        tags: set[str] | None,
) -> list[AntaDeviceHolder] | None:
    """Prepare the tests to run.

    Parameters
    ----------
        inventory: AntaInventory object that includes the device(s).
        catalog: AntaCatalog object that includes the list of tests.
        tests: Tests to run against devices. None means all tests.
        tags: Tags to filter devices from the inventory.

    Returns
    -------
        A list of AntaDeviceHolder objects that include the device information and the tests to run on it.
    """
    # Build indexes for the catalog. If `tests` is set, filter the indexes based on these tests
    catalog.build_indexes(filtered_tests=tests)

    # Creating a list of groups to divide the devices into
    device_holders = []

    for device in inventory.devices:
        serialized_device = device.serialize()
        device_holder = AntaDeviceHolder(**serialized_device)
        if tags:
            # If there are CLI tags, only execute tests with matching tags
            device_holder.tests.update(catalog.get_tests_by_tags(tags))
        else:
            # If there is no CLI tags, execute all tests that do not have any tags
            device_holder.tests.update(catalog.tag_to_tests[None])

            # Then add the tests with matching tags from device tags
            device_holder.tests.update(catalog.get_tests_by_tags(device.tags))

        device_holders.append(device_holder)

        catalog.final_tests_count += len(device_holder.tests)

    if catalog.final_tests_count == 0:
        msg = (
            f"There are no tests{f' matching the tags {tags} ' if tags else ' '}to run in the current test catalog and device inventory, please verify your inputs."
        )
        logger.warning(msg)
        return None

    return device_holders

def run_tests(device_holders: list[AntaDeviceHolder]) -> list[TestResult]:
    """Run the tests of all provided devices.

    Parameters
    ----------
        device_holders: A list of AntaDeviceHolder objects that include the device information and the tests to run on it.

    Returns
    -------
        The list of test results.
    """
    coros = []
    for device_holder in device_holders:
        # FIXME: Support other AntaDevice child classes
        device = AsyncEOSDevice(
            host=device_holder.host,
            username=device_holder.username,
            password=device_holder.password,
            name=device_holder.name,
            enable_password=device_holder.enable_password,
            port=device_holder.port,
            ssh_port=device_holder.ssh_port,
            tags=set(device_holder.tags),
            timeout=device_holder.timeout,
            enable=device_holder.enable,
            insecure=device_holder.insecure,
            disable_cache=device_holder.disable_cache,
        )
        # FIXME: Find a better way of handling this
        device.hw_model = device_holder.hw_model
        device.is_online = device_holder.is_online
        device.established = device_holder.established

        for test in device_holder.tests:
            try:
                test_instance = test.test(device=device, inputs=test.inputs)
                coros.append(test_instance.test())
            except Exception as e:  # noqa: PERF203, pylint: disable=broad-exception-caught
                # An AntaTest instance is potentially user-defined code.
                # We need to catch everything and exit gracefully with an error message.
                message = "\n".join(
                    [
                        f"There is an error when creating test {test.test.module}.{test.test.__name__}.",
                        f"If this is not a custom test implementation: {GITHUB_SUGGESTION}",
                    ],
                )
                anta_log_exception(e, message, logger)

    logger.warning("Running %s tests in process id %s", len(coros), os.getpid())

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    results = loop.run_until_complete(asyncio.gather(*coros))

    return results


@cprofile()
async def main(  # noqa: PLR0913
    manager: ResultManager,
    inventory: AntaInventory,
    catalog: AntaCatalog,
    devices: set[str] | None = None,
    tests: set[str] | None = None,
    tags: set[str] | None = None,
    *,
    established_only: bool = True,
    dry_run: bool = False,
) -> None:
    # pylint: disable=too-many-arguments
    """Run ANTA.

    Use this as an entrypoint to the test framework in your script.
    ResultManager object gets updated with the test results.

    Parameters
    ----------
        manager: ResultManager object to populate with the test results.
        inventory: AntaInventory object that includes the device(s).
        catalog: AntaCatalog object that includes the list of tests.
        devices: Devices on which to run tests. None means all devices. These may come from the `--device / -d` CLI option in NRFU.
        tests: Tests to run against devices. None means all tests. These may come from the `--test / -t` CLI option in NRFU.
        tags: Tags to filter devices from the inventory. These may come from the `--tags` CLI option in NRFU.
        established_only: Include only established device(s).
        dry_run: Build the list of coroutine to run and stop before test execution.
    """
    # Adjust the maximum number of open file descriptors for the ANTA process
    limits = adjust_rlimit_nofile()
    num_cpus = cpu_count()

    if not catalog.tests:
        logger.info("The list of tests is empty, exiting")
        return

    with Catchtime(logger=logger, message="Preparing ANTA NRFU Run"):
        # Setup the inventory
        selected_inventory = inventory if dry_run else await setup_inventory(inventory, tags, devices, established_only=established_only)
        if selected_inventory is None:
            return

        with Catchtime(logger=logger, message="Preparing the tests"):
            device_holders = prepare_tests(selected_inventory, catalog, tests, tags)
            if device_holders is None:
                return

        run_info = (
            "--- ANTA NRFU Run Information ---\n"
            f"Number of devices: {len(inventory)} ({len(selected_inventory)} established)\n"
            f"Total number of selected tests: {catalog.final_tests_count}\n"
            f"Maximum number of open file descriptors for the current ANTA process: {limits[0]}\n"
            "---------------------------------"
        )

        logger.info(run_info)

        if catalog.final_tests_count > limits[0]:
            logger.warning(
                "The number of concurrent tests is higher than the open file descriptors limit for this ANTA process.\n"
                "Errors may occur while running the tests.\n"
                "Please consult the ANTA FAQ."
            )


    # FIXME: This is broken with multiprocessing
    if AntaTest.progress is not None:
        AntaTest.nrfu_task = AntaTest.progress.add_task("Running NRFU Tests...", total=catalog.final_tests_count)


    with Catchtime(logger=logger, message="Running ANTA tests"), Pool(processes=num_cpus) as pool:
        results = pool.map(run_tests, distribute(num_cpus, device_holders))

        all_results = chain.from_iterable(results)
        for result in all_results:
            manager.add(result)

    log_cache_statistics(selected_inventory.devices)
