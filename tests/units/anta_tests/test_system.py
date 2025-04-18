# Copyright (c) 2023-2025 Arista Networks, Inc.
# Use of this source code is governed by the Apache License 2.0
# that can be found in the LICENSE file.
"""Test inputs for anta.tests.system."""

from __future__ import annotations

from typing import Any

from anta.tests.system import (
    VerifyAgentLogs,
    VerifyCoredump,
    VerifyCPUUtilization,
    VerifyFileSystemUtilization,
    VerifyMaintenance,
    VerifyMemoryUtilization,
    VerifyNTP,
    VerifyNTPAssociations,
    VerifyReloadCause,
    VerifyUptime,
)
from tests.units.anta_tests import test

DATA: list[dict[str, Any]] = [
    {
        "name": "success",
        "test": VerifyUptime,
        "eos_data": [{"upTime": 1186689.15, "loadAvg": [0.13, 0.12, 0.09], "users": 1, "currentTime": 1683186659.139859}],
        "inputs": {"minimum": 666},
        "expected": {"result": "success"},
    },
    {
        "name": "failure",
        "test": VerifyUptime,
        "eos_data": [{"upTime": 665.15, "loadAvg": [0.13, 0.12, 0.09], "users": 1, "currentTime": 1683186659.139859}],
        "inputs": {"minimum": 666},
        "expected": {"result": "failure", "messages": ["Device uptime is incorrect - Expected: 666s Actual: 665.15s"]},
    },
    {
        "name": "success-no-reload",
        "test": VerifyReloadCause,
        "eos_data": [{"kernelCrashData": [], "resetCauses": [], "full": False}],
        "inputs": None,
        "expected": {"result": "success"},
    },
    {
        "name": "success-valid-cause-user",
        "test": VerifyReloadCause,
        "eos_data": [
            {
                "resetCauses": [
                    {
                        "recommendedAction": "No action necessary.",
                        "description": "Reload requested by the user.",
                        "timestamp": 1683186892.0,
                        "debugInfoIsDir": False,
                    },
                ],
                "full": False,
            },
        ],
        "inputs": None,
        "expected": {"result": "success"},
    },
    {
        "name": "success-valid-reload-cause-ztp",
        "test": VerifyReloadCause,
        "eos_data": [
            {
                "resetCauses": [
                    {
                        "description": "System reloaded due to Zero Touch Provisioning",
                        "timestamp": 1729856740.0,
                        "recommendedAction": "No action necessary.",
                        "debugInfoIsDir": False,
                    }
                ],
                "full": False,
            }
        ],
        "inputs": {"allowed_causes": ["ZTP"]},
        "expected": {"result": "success"},
    },
    {
        "name": "success-valid-reload-cause-fpga",
        "test": VerifyReloadCause,
        "eos_data": [
            {
                "resetCauses": [
                    {
                        "description": "Reload requested after FPGA upgrade",
                        "timestamp": 1729856740.0,
                        "recommendedAction": "No action necessary.",
                        "debugInfoIsDir": False,
                    }
                ],
                "full": False,
            }
        ],
        "inputs": {"allowed_causes": ["fpga"]},
        "expected": {"result": "success"},
    },
    {
        "name": "failure-invalid-reload-cause",
        "test": VerifyReloadCause,
        "eos_data": [
            {
                "resetCauses": [
                    {
                        "description": "Reload requested after FPGA upgrade",
                        "timestamp": 1729856740.0,
                        "recommendedAction": "No action necessary.",
                        "debugInfoIsDir": False,
                    }
                ],
                "full": False,
            }
        ],
        "inputs": {"allowed_causes": ["ZTP"]},
        "expected": {
            "result": "failure",
            "messages": ["Invalid reload cause -  Expected: 'System reloaded due to Zero Touch Provisioning' Actual: 'Reload requested after FPGA upgrade'"],
        },
    },
    {
        "name": "failure",
        "test": VerifyReloadCause,
        # The failure cause is made up
        "eos_data": [
            {
                "resetCauses": [
                    {"recommendedAction": "No action necessary.", "description": "Reload after crash.", "timestamp": 1683186892.0, "debugInfoIsDir": False},
                ],
                "full": False,
            },
        ],
        "inputs": None,
        "expected": {
            "result": "failure",
            "messages": ["Invalid reload cause -  Expected: 'Reload requested by the user.', 'Reload requested after FPGA upgrade' Actual: 'Reload after crash.'"],
        },
    },
    {
        "name": "success-without-minidump",
        "test": VerifyCoredump,
        "eos_data": [{"mode": "compressedDeferred", "coreFiles": []}],
        "inputs": None,
        "expected": {"result": "success"},
    },
    {
        "name": "success-with-minidump",
        "test": VerifyCoredump,
        "eos_data": [{"mode": "compressedDeferred", "coreFiles": ["minidump"]}],
        "inputs": None,
        "expected": {"result": "success"},
    },
    {
        "name": "failure-without-minidump",
        "test": VerifyCoredump,
        "eos_data": [{"mode": "compressedDeferred", "coreFiles": ["core.2344.1584483862.Mlag.gz", "core.23101.1584483867.Mlag.gz"]}],
        "inputs": None,
        "expected": {"result": "failure", "messages": ["Core dump(s) have been found: core.2344.1584483862.Mlag.gz, core.23101.1584483867.Mlag.gz"]},
    },
    {
        "name": "failure-with-minidump",
        "test": VerifyCoredump,
        "eos_data": [{"mode": "compressedDeferred", "coreFiles": ["minidump", "core.2344.1584483862.Mlag.gz", "core.23101.1584483867.Mlag.gz"]}],
        "inputs": None,
        "expected": {"result": "failure", "messages": ["Core dump(s) have been found: core.2344.1584483862.Mlag.gz, core.23101.1584483867.Mlag.gz"]},
    },
    {
        "name": "success",
        "test": VerifyAgentLogs,
        "eos_data": [""],
        "inputs": None,
        "expected": {"result": "success"},
    },
    {
        "name": "failure",
        "test": VerifyAgentLogs,
        "eos_data": [
            """===> /var/log/agents/Test-666 Thu May  4 09:57:02 2023 <===
CLI Exception: Exception
CLI Exception: Backtrace
===> /var/log/agents/Aaa-855 Fri Jul  7 15:07:00 2023 <===
===== Output from /usr/bin/Aaa [] (PID=855) started Jul  7 15:06:11.606414 ===
EntityManager::doBackoff waiting for remote sysdb version ....ok

===> /var/log/agents/Acl-830 Fri Jul  7 15:07:00 2023 <===
===== Output from /usr/bin/Acl [] (PID=830) started Jul  7 15:06:10.871700 ===
EntityManager::doBackoff waiting for remote sysdb version ...................ok
""",
        ],
        "inputs": None,
        "expected": {
            "result": "failure",
            "messages": [
                "Device has reported agent crashes:\n"
                " * /var/log/agents/Test-666 Thu May  4 09:57:02 2023\n"
                " * /var/log/agents/Aaa-855 Fri Jul  7 15:07:00 2023\n"
                " * /var/log/agents/Acl-830 Fri Jul  7 15:07:00 2023",
            ],
        },
    },
    {
        "name": "success",
        "test": VerifyCPUUtilization,
        "eos_data": [
            {
                "cpuInfo": {"%Cpu(s)": {"idle": 88.2, "stolen": 0.0, "user": 5.9, "swIrq": 0.0, "ioWait": 0.0, "system": 0.0, "hwIrq": 5.9, "nice": 0.0}},
                "processes": {
                    "1": {
                        "userName": "root",
                        "status": "S",
                        "memPct": 0.3,
                        "niceValue": 0,
                        "cpuPct": 0.0,
                        "cpuPctType": "{:.1f}",
                        "cmd": "systemd",
                        "residentMem": "5096",
                        "priority": "20",
                        "activeTime": 360,
                        "virtMem": "6644",
                        "sharedMem": "3996",
                    },
                },
            },
        ],
        "inputs": None,
        "expected": {"result": "success"},
    },
    {
        "name": "failure",
        "test": VerifyCPUUtilization,
        "eos_data": [
            {
                "cpuInfo": {"%Cpu(s)": {"idle": 24.8, "stolen": 0.0, "user": 5.9, "swIrq": 0.0, "ioWait": 0.0, "system": 0.0, "hwIrq": 5.9, "nice": 0.0}},
                "processes": {
                    "1": {
                        "userName": "root",
                        "status": "S",
                        "memPct": 0.3,
                        "niceValue": 0,
                        "cpuPct": 0.0,
                        "cpuPctType": "{:.1f}",
                        "cmd": "systemd",
                        "residentMem": "5096",
                        "priority": "20",
                        "activeTime": 360,
                        "virtMem": "6644",
                        "sharedMem": "3996",
                    },
                },
            },
        ],
        "inputs": None,
        "expected": {"result": "failure", "messages": ["Device has reported a high CPU utilization -  Expected: < 75% Actual: 75.2%"]},
    },
    {
        "name": "success",
        "test": VerifyMemoryUtilization,
        "eos_data": [
            {
                "uptime": 1994.67,
                "modelName": "vEOS-lab",
                "internalVersion": "4.27.3F-26379303.4273F",
                "memTotal": 2004568,
                "memFree": 879004,
                "version": "4.27.3F",
            },
        ],
        "inputs": None,
        "expected": {"result": "success"},
    },
    {
        "name": "failure",
        "test": VerifyMemoryUtilization,
        "eos_data": [
            {
                "uptime": 1994.67,
                "modelName": "vEOS-lab",
                "internalVersion": "4.27.3F-26379303.4273F",
                "memTotal": 2004568,
                "memFree": 89004,
                "version": "4.27.3F",
            },
        ],
        "inputs": None,
        "expected": {"result": "failure", "messages": ["Device has reported a high memory usage - Expected: < 75% Actual: 95.56%"]},
    },
    {
        "name": "success",
        "test": VerifyFileSystemUtilization,
        "eos_data": [
            """Filesystem      Size  Used Avail Use% Mounted on
/dev/sda2       3.9G  988M  2.9G  26% /mnt/flash
none            294M   78M  217M  27% /
none            294M   78M  217M  27% /.overlay
/dev/loop0      461M  461M     0 100% /rootfs-i386
""",
        ],
        "inputs": None,
        "expected": {"result": "success"},
    },
    {
        "name": "failure",
        "test": VerifyFileSystemUtilization,
        "eos_data": [
            """Filesystem      Size  Used Avail Use% Mounted on
/dev/sda2       3.9G  988M  2.9G  84% /mnt/flash
none            294M   78M  217M  27% /
none            294M   78M  217M  84% /.overlay
/dev/loop0      461M  461M     0 100% /rootfs-i386
""",
        ],
        "inputs": None,
        "expected": {
            "result": "failure",
            "messages": [
                "Mount point: /dev/sda2       3.9G  988M  2.9G  84% /mnt/flash - Higher disk space utilization - Expected: 75% Actual: 84%",
                "Mount point: none            294M   78M  217M  84% /.overlay - Higher disk space utilization - Expected: 75% Actual: 84%",
            ],
        },
    },
    {
        "name": "success",
        "test": VerifyNTP,
        "eos_data": [
            """synchronised
poll interval unknown
""",
        ],
        "inputs": None,
        "expected": {"result": "success"},
    },
    {
        "name": "failure",
        "test": VerifyNTP,
        "eos_data": [
            """unsynchronised
poll interval unknown
""",
        ],
        "inputs": None,
        "expected": {"result": "failure", "messages": ["NTP status mismatch - Expected: synchronised Actual: unsynchronised"]},
    },
    {
        "name": "success",
        "test": VerifyNTPAssociations,
        "eos_data": [
            {
                "peers": {
                    "1.1.1.1": {
                        "condition": "sys.peer",
                        "peerIpAddr": "1.1.1.1",
                        "stratumLevel": 1,
                    },
                    "2.2.2.2": {
                        "condition": "candidate",
                        "peerIpAddr": "2.2.2.2",
                        "stratumLevel": 2,
                    },
                    "3.3.3.3": {
                        "condition": "candidate",
                        "peerIpAddr": "3.3.3.3",
                        "stratumLevel": 2,
                    },
                }
            }
        ],
        "inputs": {
            "ntp_servers": [
                {"server_address": "1.1.1.1", "preferred": True, "stratum": 1},
                {"server_address": "2.2.2.2", "stratum": 2},
                {"server_address": "3.3.3.3", "stratum": 2},
            ]
        },
        "expected": {"result": "success"},
    },
    {
        "name": "success-pool-name",
        "test": VerifyNTPAssociations,
        "eos_data": [
            {
                "peers": {
                    "1.ntp.networks.com": {
                        "condition": "sys.peer",
                        "peerIpAddr": "1.1.1.1",
                        "stratumLevel": 1,
                    },
                    "2.ntp.networks.com": {
                        "condition": "candidate",
                        "peerIpAddr": "2.2.2.2",
                        "stratumLevel": 2,
                    },
                    "3.ntp.networks.com": {
                        "condition": "candidate",
                        "peerIpAddr": "3.3.3.3",
                        "stratumLevel": 2,
                    },
                }
            }
        ],
        "inputs": {
            "ntp_servers": [
                {"server_address": "1.ntp.networks.com", "preferred": True, "stratum": 1},
                {"server_address": "2.ntp.networks.com", "stratum": 2},
                {"server_address": "3.ntp.networks.com", "stratum": 2},
            ]
        },
        "expected": {"result": "success"},
    },
    {
        "name": "success-ntp-pool-as-input",
        "test": VerifyNTPAssociations,
        "eos_data": [
            {
                "peers": {
                    "1.1.1.1": {
                        "condition": "sys.peer",
                        "peerIpAddr": "1.1.1.1",
                        "stratumLevel": 1,
                    },
                    "2.2.2.2": {
                        "condition": "candidate",
                        "peerIpAddr": "2.2.2.2",
                        "stratumLevel": 2,
                    },
                    "3.3.3.3": {
                        "condition": "candidate",
                        "peerIpAddr": "3.3.3.3",
                        "stratumLevel": 2,
                    },
                }
            }
        ],
        "inputs": {"ntp_pool": {"server_addresses": ["1.1.1.1", "2.2.2.2", "3.3.3.3"], "preferred_stratum_range": [1, 2]}},
        "expected": {"result": "success"},
    },
    {
        "name": "success-ntp-pool-hostname",
        "test": VerifyNTPAssociations,
        "eos_data": [
            {
                "peers": {
                    "itsys-ntp010p.aristanetworks.com": {
                        "condition": "sys.peer",
                        "peerIpAddr": "1.1.1.1",
                        "stratumLevel": 1,
                    },
                    "itsys-ntp011p.aristanetworks.com": {
                        "condition": "candidate",
                        "peerIpAddr": "2.2.2.2",
                        "stratumLevel": 2,
                    },
                    "itsys-ntp012p.aristanetworks.com": {
                        "condition": "candidate",
                        "peerIpAddr": "3.3.3.3",
                        "stratumLevel": 2,
                    },
                }
            }
        ],
        "inputs": {
            "ntp_pool": {
                "server_addresses": ["itsys-ntp010p.aristanetworks.com", "itsys-ntp011p.aristanetworks.com", "itsys-ntp012p.aristanetworks.com"],
                "preferred_stratum_range": [1, 2],
            }
        },
        "expected": {"result": "success"},
    },
    {
        "name": "success-ip-dns",
        "test": VerifyNTPAssociations,
        "eos_data": [
            {
                "peers": {
                    "1.1.1.1 (1.ntp.networks.com)": {
                        "condition": "sys.peer",
                        "peerIpAddr": "1.1.1.1",
                        "stratumLevel": 1,
                    },
                    "2.2.2.2 (2.ntp.networks.com)": {
                        "condition": "candidate",
                        "peerIpAddr": "2.2.2.2",
                        "stratumLevel": 2,
                    },
                    "3.3.3.3 (3.ntp.networks.com)": {
                        "condition": "candidate",
                        "peerIpAddr": "3.3.3.3",
                        "stratumLevel": 2,
                    },
                }
            }
        ],
        "inputs": {
            "ntp_servers": [
                {"server_address": "1.1.1.1", "preferred": True, "stratum": 1},
                {"server_address": "2.2.2.2", "stratum": 2},
                {"server_address": "3.3.3.3", "stratum": 2},
            ]
        },
        "expected": {"result": "success"},
    },
    {
        "name": "failure-ntp-server",
        "test": VerifyNTPAssociations,
        "eos_data": [
            {
                "peers": {
                    "1.1.1.1": {
                        "condition": "candidate",
                        "peerIpAddr": "1.1.1.1",
                        "stratumLevel": 2,
                    },
                    "2.2.2.2": {
                        "condition": "sys.peer",
                        "peerIpAddr": "2.2.2.2",
                        "stratumLevel": 2,
                    },
                    "3.3.3.3": {
                        "condition": "sys.peer",
                        "peerIpAddr": "3.3.3.3",
                        "stratumLevel": 3,
                    },
                }
            }
        ],
        "inputs": {
            "ntp_servers": [
                {"server_address": "1.1.1.1", "preferred": True, "stratum": 1},
                {"server_address": "2.2.2.2", "stratum": 2},
                {"server_address": "3.3.3.3", "stratum": 2},
            ]
        },
        "expected": {
            "result": "failure",
            "messages": [
                "NTP Server: 1.1.1.1 Preferred: True Stratum: 1 - Incorrect condition - Expected: sys.peer Actual: candidate",
                "NTP Server: 1.1.1.1 Preferred: True Stratum: 1 - Incorrect stratum level - Expected: 1 Actual: 2",
                "NTP Server: 2.2.2.2 Preferred: False Stratum: 2 - Incorrect condition - Expected: candidate Actual: sys.peer",
                "NTP Server: 3.3.3.3 Preferred: False Stratum: 2 - Incorrect condition - Expected: candidate Actual: sys.peer",
                "NTP Server: 3.3.3.3 Preferred: False Stratum: 2 - Incorrect stratum level - Expected: 2 Actual: 3",
            ],
        },
    },
    {
        "name": "failure-no-peers",
        "test": VerifyNTPAssociations,
        "eos_data": [{"peers": {}}],
        "inputs": {
            "ntp_servers": [
                {"server_address": "1.1.1.1", "preferred": True, "stratum": 1},
                {"server_address": "2.2.2.2", "stratum": 1},
                {"server_address": "3.3.3.3", "stratum": 1},
            ]
        },
        "expected": {
            "result": "failure",
            "messages": ["No NTP peers configured"],
        },
    },
    {
        "name": "failure-one-peer-not-found",
        "test": VerifyNTPAssociations,
        "eos_data": [
            {
                "peers": {
                    "1.1.1.1": {
                        "condition": "sys.peer",
                        "peerIpAddr": "1.1.1.1",
                        "stratumLevel": 1,
                    },
                    "2.2.2.2": {
                        "condition": "candidate",
                        "peerIpAddr": "2.2.2.2",
                        "stratumLevel": 1,
                    },
                }
            }
        ],
        "inputs": {
            "ntp_servers": [
                {"server_address": "1.1.1.1", "preferred": True, "stratum": 1},
                {"server_address": "2.2.2.2", "stratum": 1},
                {"server_address": "3.3.3.3", "stratum": 1},
            ]
        },
        "expected": {
            "result": "failure",
            "messages": ["NTP Server: 3.3.3.3 Preferred: False Stratum: 1 - Not configured"],
        },
    },
    {
        "name": "failure-with-two-peers-not-found",
        "test": VerifyNTPAssociations,
        "eos_data": [
            {
                "peers": {
                    "1.1.1.1": {
                        "condition": "candidate",
                        "peerIpAddr": "1.1.1.1",
                        "stratumLevel": 1,
                    }
                }
            }
        ],
        "inputs": {
            "ntp_servers": [
                {"server_address": "1.1.1.1", "preferred": True, "stratum": 1},
                {"server_address": "2.2.2.2", "stratum": 1},
                {"server_address": "3.3.3.3", "stratum": 1},
            ]
        },
        "expected": {
            "result": "failure",
            "messages": [
                "NTP Server: 1.1.1.1 Preferred: True Stratum: 1 - Incorrect condition - Expected: sys.peer Actual: candidate",
                "NTP Server: 2.2.2.2 Preferred: False Stratum: 1 - Not configured",
                "NTP Server: 3.3.3.3 Preferred: False Stratum: 1 - Not configured",
            ],
        },
    },
    {
        "name": "failure-ntp-pool-as-input",
        "test": VerifyNTPAssociations,
        "eos_data": [
            {
                "peers": {
                    "ntp1.pool": {
                        "condition": "sys.peer",
                        "peerIpAddr": "1.1.1.1",
                        "stratumLevel": 1,
                    },
                    "ntp2.pool": {
                        "condition": "candidate",
                        "peerIpAddr": "2.2.2.2",
                        "stratumLevel": 2,
                    },
                    "ntp3.pool": {
                        "condition": "candidate",
                        "peerIpAddr": "3.3.3.3",
                        "stratumLevel": 2,
                    },
                }
            }
        ],
        "inputs": {"ntp_pool": {"server_addresses": ["1.1.1.1", "2.2.2.2"], "preferred_stratum_range": [1, 2]}},
        "expected": {
            "result": "failure",
            "messages": ["NTP Server: 3.3.3.3 Hostname: ntp3.pool - Associated but not part of the provided NTP pool"],
        },
    },
    {
        "name": "failure-ntp-pool-as-input-bad-association",
        "test": VerifyNTPAssociations,
        "eos_data": [
            {
                "peers": {
                    "ntp1.pool": {
                        "condition": "sys.peer",
                        "peerIpAddr": "1.1.1.1",
                        "stratumLevel": 1,
                    },
                    "ntp2.pool": {
                        "condition": "candidate",
                        "peerIpAddr": "2.2.2.2",
                        "stratumLevel": 2,
                    },
                    "ntp3.pool": {
                        "condition": "reject",
                        "peerIpAddr": "3.3.3.3",
                        "stratumLevel": 3,
                    },
                }
            }
        ],
        "inputs": {"ntp_pool": {"server_addresses": ["1.1.1.1", "2.2.2.2", "3.3.3.3"], "preferred_stratum_range": [1, 2]}},
        "expected": {
            "result": "failure",
            "messages": [
                "NTP Server: 3.3.3.3 Hostname: ntp3.pool - Incorrect condition  - Expected: sys.peer, candidate Actual: reject",
                "NTP Server: 3.3.3.3 Hostname: ntp3.pool - Incorrect stratum level - Expected Stratum Range: 1 to 2 Actual: 3",
            ],
        },
    },
    {
        "name": "failure-ntp-pool-hostname",
        "test": VerifyNTPAssociations,
        "eos_data": [
            {
                "peers": {
                    "itsys-ntp010p.aristanetworks.com": {
                        "condition": "sys.peer",
                        "peerIpAddr": "1.1.1.1",
                        "stratumLevel": 5,
                    },
                    "itsys-ntp011p.aristanetworks.com": {
                        "condition": "reject",
                        "peerIpAddr": "2.2.2.2",
                        "stratumLevel": 4,
                    },
                    "itsys-ntp012p.aristanetworks.com": {
                        "condition": "candidate",
                        "peerIpAddr": "3.3.3.3",
                        "stratumLevel": 2,
                    },
                }
            }
        ],
        "inputs": {"ntp_pool": {"server_addresses": ["itsys-ntp010p.aristanetworks.com", "itsys-ntp011p.aristanetworks.com"], "preferred_stratum_range": [1, 2]}},
        "expected": {
            "result": "failure",
            "messages": [
                "NTP Server: 1.1.1.1 Hostname: itsys-ntp010p.aristanetworks.com - Incorrect stratum level - Expected Stratum Range: 1 to 2 Actual: 5",
                "NTP Server: 2.2.2.2 Hostname: itsys-ntp011p.aristanetworks.com - Incorrect condition  - Expected: sys.peer, candidate Actual: reject",
                "NTP Server: 2.2.2.2 Hostname: itsys-ntp011p.aristanetworks.com - Incorrect stratum level - Expected Stratum Range: 1 to 2 Actual: 4",
                "NTP Server: 3.3.3.3 Hostname: itsys-ntp012p.aristanetworks.com - Associated but not part of the provided NTP pool",
            ],
        },
    },
    {
        "name": "success-no-maintenance-configured",
        "test": VerifyMaintenance,
        "eos_data": [
            {
                "units": {},
                "interfaces": {},
                "vrfs": {},
                "warnings": ["Maintenance Mode is disabled."],
            },
        ],
        "inputs": None,
        "expected": {"result": "success"},
    },
    {
        "name": "success-maintenance-configured-but-not-enabled",
        "test": VerifyMaintenance,
        "eos_data": [
            {
                "units": {
                    "System": {
                        "state": "active",
                        "adminState": "active",
                        "stateChangeTime": 0.0,
                        "onBootMaintenance": False,
                        "intfsViolatingTrafficThreshold": False,
                        "aggInBpsRate": 0,
                        "aggOutBpsRate": 0,
                    }
                },
                "interfaces": {},
                "vrfs": {},
            },
        ],
        "inputs": None,
        "expected": {"result": "success"},
    },
    {
        "name": "success-multiple-units-but-not-enabled",
        "test": VerifyMaintenance,
        "eos_data": [
            {
                "units": {
                    "mlag": {
                        "state": "active",
                        "adminState": "active",
                        "stateChangeTime": 0.0,
                        "onBootMaintenance": False,
                        "intfsViolatingTrafficThreshold": False,
                        "aggInBpsRate": 0,
                        "aggOutBpsRate": 0,
                    },
                    "System": {
                        "state": "active",
                        "adminState": "active",
                        "stateChangeTime": 0.0,
                        "onBootMaintenance": False,
                        "intfsViolatingTrafficThreshold": False,
                        "aggInBpsRate": 0,
                        "aggOutBpsRate": 0,
                    },
                },
                "interfaces": {},
                "vrfs": {},
            },
        ],
        "inputs": None,
        "expected": {"result": "success"},
    },
    {
        "name": "failure-maintenance-enabled",
        "test": VerifyMaintenance,
        "eos_data": [
            {
                "units": {
                    "mlag": {
                        "state": "underMaintenance",
                        "adminState": "underMaintenance",
                        "stateChangeTime": 1741257120.9532886,
                        "onBootMaintenance": False,
                        "intfsViolatingTrafficThreshold": False,
                        "aggInBpsRate": 0,
                        "aggOutBpsRate": 0,
                    },
                    "System": {
                        "state": "active",
                        "adminState": "active",
                        "stateChangeTime": 0.0,
                        "onBootMaintenance": False,
                        "intfsViolatingTrafficThreshold": False,
                        "aggInBpsRate": 0,
                        "aggOutBpsRate": 0,
                    },
                },
                "interfaces": {},
                "vrfs": {},
            },
        ],
        "inputs": None,
        "expected": {
            "result": "failure",
            "messages": [
                "Units under maintenance: 'mlag'",
                "Possible causes: 'Quiesce is configured'",
            ],
        },
    },
    {
        "name": "failure-multiple-reasons",
        "test": VerifyMaintenance,
        "eos_data": [
            {
                "units": {
                    "mlag": {
                        "state": "underMaintenance",
                        "adminState": "underMaintenance",
                        "stateChangeTime": 1741257120.9532895,
                        "onBootMaintenance": False,
                        "intfsViolatingTrafficThreshold": False,
                        "aggInBpsRate": 0,
                        "aggOutBpsRate": 0,
                    },
                    "System": {
                        "state": "maintenanceModeEnter",
                        "adminState": "underMaintenance",
                        "stateChangeTime": 1741257669.7231765,
                        "onBootMaintenance": False,
                        "intfsViolatingTrafficThreshold": False,
                        "aggInBpsRate": 0,
                        "aggOutBpsRate": 0,
                    },
                },
                "interfaces": {},
                "vrfs": {},
            },
        ],
        "inputs": None,
        "expected": {
            "result": "failure",
            "messages": [
                "Units under maintenance: 'mlag'",
                "Units entering maintenance: 'System'",
                "Possible causes: 'Quiesce is configured'",
            ],
        },
    },
    {
        "name": "failure-onboot-maintenance",
        "test": VerifyMaintenance,
        "eos_data": [
            {
                "units": {
                    "System": {
                        "state": "underMaintenance",
                        "adminState": "underMaintenance",
                        "stateChangeTime": 1741258774.3756502,
                        "onBootMaintenance": True,
                        "intfsViolatingTrafficThreshold": False,
                        "aggInBpsRate": 0,
                        "aggOutBpsRate": 0,
                    }
                },
                "interfaces": {},
                "vrfs": {},
            },
        ],
        "inputs": None,
        "expected": {
            "result": "failure",
            "messages": [
                "Units under maintenance: 'System'",
                "Possible causes: 'On-boot maintenance is configured, Quiesce is configured'",
            ],
        },
    },
    {
        "name": "failure-entering-maintenance-interface-violation",
        "test": VerifyMaintenance,
        "eos_data": [
            {
                "units": {
                    "System": {
                        "state": "maintenanceModeEnter",
                        "adminState": "underMaintenance",
                        "stateChangeTime": 1741257669.7231765,
                        "onBootMaintenance": False,
                        "intfsViolatingTrafficThreshold": True,
                        "aggInBpsRate": 0,
                        "aggOutBpsRate": 0,
                    }
                },
                "interfaces": {},
                "vrfs": {},
            },
        ],
        "inputs": None,
        "expected": {
            "result": "failure",
            "messages": [
                "Units entering maintenance: 'System'",
                "Possible causes: 'Interface traffic threshold violation, Quiesce is configured'",
            ],
        },
    },
]
