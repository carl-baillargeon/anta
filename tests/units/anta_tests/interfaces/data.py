"""Test inputs for anta.tests.hardware"""

from typing import Any, Dict, List

INPUT_INTERFACE_UTILIZATION: List[Dict[str, Any]] = [
    {
        "name": "success",
        "eos_data": [
            """Port      Name        Intvl   In Mbps      %  In Kpps  Out Mbps      % Out Kpps
Et1                    5:00       0.0   0.0%        0       0.0   0.0%        0
Et4                    5:00       0.0   0.0%        0       0.0   0.0%        0
"""
        ],
        "side_effect": [],
        "expected_result": "success",
        "expected_messages": [],
    },
    {
        "name": "failure",
        "eos_data": [
            """Port      Name        Intvl   In Mbps      %  In Kpps  Out Mbps      % Out Kpps
Et1                    5:00       0.0   0.0%        0       0.0  80.0%        0
Et4                    5:00       0.0  99.9%        0       0.0   0.0%        0
"""
        ],
        "side_effect": [],
        "expected_result": "failure",
        "expected_messages": ["The following interfaces have a usage > 75%: {'Et1': '80.0%', 'Et4': '99.9%'}"],
    },
]

INPUT_INTERFACE_ERRORS: List[Dict[str, Any]] = [
    {
        "name": "success",
        "eos_data": [
            {
                "interfaceErrorCounters": {
                    "Ethernet1": {"inErrors": 0, "frameTooLongs": 0, "outErrors": 0, "frameTooShorts": 0, "fcsErrors": 0, "alignmentErrors": 0, "symbolErrors": 0},
                    "Ethernet6": {"inErrors": 0, "frameTooLongs": 0, "outErrors": 0, "frameTooShorts": 0, "fcsErrors": 0, "alignmentErrors": 0, "symbolErrors": 0},
                }
            }
        ],
        "side_effect": [],
        "expected_result": "success",
        "expected_messages": [],
    },
    {
        "name": "failure",
        "eos_data": [
            {
                "interfaceErrorCounters": {
                    "Ethernet1": {"inErrors": 42, "frameTooLongs": 0, "outErrors": 0, "frameTooShorts": 0, "fcsErrors": 0, "alignmentErrors": 0, "symbolErrors": 0},
                    "Ethernet6": {"inErrors": 0, "frameTooLongs": 0, "outErrors": 0, "frameTooShorts": 0, "fcsErrors": 0, "alignmentErrors": 666, "symbolErrors": 0},
                }
            }
        ],
        "side_effect": [],
        "expected_result": "failure",
        "expected_messages": [
            "The following interfaces have non 0 error counter(s): [{'Ethernet1': {'inErrors': 42, 'frameTooLongs': 0, 'outErrors': 0, 'frameTooShorts': 0,"
            " 'fcsErrors': 0, 'alignmentErrors': 0, 'symbolErrors': 0}}, {'Ethernet6': {'inErrors': 0, 'frameTooLongs': 0, 'outErrors': 0, 'frameTooShorts':"
            " 0, 'fcsErrors': 0, 'alignmentErrors': 666, 'symbolErrors': 0}}]"
        ],
    },
]


INPUT_INTERFACE_DISCARDS: List[Dict[str, Any]] = [
    {
        "name": "success",
        "eos_data": [
            {
                "inDiscardsTotal": 0,
                "interfaces": {
                    "Ethernet2": {"outDiscards": 0, "inDiscards": 0},
                    "Ethernet1": {"outDiscards": 0, "inDiscards": 0},
                },
                "outDiscardsTotal": 0,
            }
        ],
        "side_effect": [],
        "expected_result": "success",
        "expected_messages": [],
    },
    {
        "name": "failure",
        "eos_data": [
            {
                "inDiscardsTotal": 0,
                "interfaces": {
                    "Ethernet2": {"outDiscards": 42, "inDiscards": 0},
                    "Ethernet1": {"outDiscards": 0, "inDiscards": 42},
                },
                "outDiscardsTotal": 0,
            }
        ],
        "side_effect": [],
        "expected_result": "failure",
        "expected_messages": [
            "The following interfaces have non 0 discard counter(s): [{'Ethernet2': {'outDiscards': 42, 'inDiscards': 0}},"
            " {'Ethernet1': {'outDiscards': 0, 'inDiscards': 42}}]"
        ],
    },
]

INPUT_INTERFACE_ERR_DISABLED: List[Dict[str, Any]] = [
    {
        "name": "success",
        "eos_data": [
            {
                "interfaceStatuses": {
                    "Management1": {
                        "linkStatus": "connected",
                    },
                    "Ethernet8": {
                        "linkStatus": "connected",
                    },
                }
            }
        ],
        "side_effect": [],
        "expected_result": "success",
        "expected_messages": [],
    },
    {
        "name": "failure",
        "eos_data": [
            {
                "interfaceStatuses": {
                    "Management1": {
                        "linkStatus": "errdisabled",
                    },
                    "Ethernet8": {
                        "linkStatus": "errdisabled",
                    },
                }
            }
        ],
        "side_effect": [],
        "expected_result": "failure",
        "expected_messages": ["The following interfaces are in error disabled state: ['Management1', 'Ethernet8']"],
    },
]

INPUT_INTERFACES_STATUS: List[Dict[str, Any]] = [
    {
        "name": "success",
        "eos_data": [
            {
                "interfaceDescriptions": {
                    "Ethernet8": {"interfaceStatus": "up", "description": "", "lineProtocolStatus": "up"},
                    "Ethernet2": {"interfaceStatus": "up", "description": "", "lineProtocolStatus": "up"},
                    "Ethernet3": {"interfaceStatus": "up", "description": "", "lineProtocolStatus": "up"},
                }
            }
        ],
        "side_effect": 3,
        "expected_result": "success",
        "expected_messages": [],
    },
    {
        "name": "failure",
        "eos_data": [
            {
                "interfaceDescriptions": {
                    "Ethernet8": {"interfaceStatus": "up", "description": "", "lineProtocolStatus": "down"},
                    "Ethernet2": {"interfaceStatus": "up", "description": "", "lineProtocolStatus": "up"},
                    "Ethernet3": {"interfaceStatus": "up", "description": "", "lineProtocolStatus": "up"},
                }
            }
        ],
        "side_effect": 3,
        "expected_result": "failure",
        "expected_messages": ["Only 2, less than 3 Ethernet interfaces are UP/UP", "The following Ethernet interfaces are not UP/UP: ['Ethernet8']"],
    },
    {
        "name": "skipped",
        "eos_data": [
            {
                "interfaceDescriptions": {
                    "Management1": {"interfaceStatus": "up", "description": "", "lineProtocolStatus": "up"},
                    "Ethernet8": {"interfaceStatus": "up", "description": "", "lineProtocolStatus": "up"},
                    "Ethernet2": {"interfaceStatus": "up", "description": "", "lineProtocolStatus": "up"},
                    "Ethernet3": {"interfaceStatus": "up", "description": "", "lineProtocolStatus": "up"},
                }
            }
        ],
        "side_effect": -1,
        "expected_result": "skipped",
        "expected_messages": ["VerifyInterfacesStatus was not run as an invalid minimum value was given -1."],
    },
]

INPUT_STORM_CONTROL_DROPS: List[Dict[str, Any]] = [
    {
        "name": "success",
        "eos_data": [
            {
                "aggregateTrafficClasses": {},
                "interfaces": {
                    "Ethernet1": {
                        "trafficTypes": {"broadcast": {"level": 100, "thresholdType": "packetsPerSecond", "rate": 0, "drop": 0, "dormant": False}},
                        "active": True,
                        "reason": "",
                        "errdisabled": False,
                    }
                },
            }
        ],
        "side_effect": [],
        "expected_result": "success",
        "expected_messages": [],
    },
    {
        "name": "failure",
        "eos_data": [
            {
                "aggregateTrafficClasses": {},
                "interfaces": {
                    "Ethernet1": {
                        "trafficTypes": {"broadcast": {"level": 100, "thresholdType": "packetsPerSecond", "rate": 0, "drop": 666, "dormant": False}},
                        "active": True,
                        "reason": "",
                        "errdisabled": False,
                    }
                },
            }
        ],
        "side_effect": [],
        "expected_result": "failure",
        "expected_messages": ["The following interfaces have none 0 storm-control drop counters {'Ethernet1': {'broadcast': 666}}"],
    },
]

INPUT_PORT_CHANNELS: List[Dict[str, Any]] = [
    {
        "name": "success",
        "eos_data": [
            {
                "portChannels": {
                    "Port-Channel42": {
                        "recircFeature": [],
                        "maxWeight": 16,
                        "minSpeed": "0 gbps",
                        "rxPorts": {},
                        "currWeight": 0,
                        "minLinks": 0,
                        "inactivePorts": {},
                        "activePorts": {},
                        "inactiveLag": False,
                    }
                }
            }
        ],
        "side_effect": [],
        "expected_result": "success",
        "expected_messages": [],
    },
    {
        "name": "failure",
        "eos_data": [
            {
                "portChannels": {
                    "Port-Channel42": {
                        "recircFeature": [],
                        "maxWeight": 16,
                        "minSpeed": "0 gbps",
                        "rxPorts": {},
                        "currWeight": 0,
                        "minLinks": 0,
                        "inactivePorts": {"Ethernet8": {"reasonUnconfigured": "waiting for LACP response"}},
                        "activePorts": {},
                        "inactiveLag": False,
                    }
                }
            }
        ],
        "side_effect": [],
        "expected_result": "failure",
        "expected_messages": ["The following port-channels have inactive port(s): ['Port-Channel42']"],
    },
]

INPUT_ILLEGAL_LACP: List[Dict[str, Any]] = [
    {
        "name": "success",
        "eos_data": [
            {
                "portChannels": {
                    "Port-Channel42": {
                        "interfaces": {
                            "Ethernet8": {
                                "actorPortStatus": "noAgg",
                                "illegalRxCount": 0,
                                "markerResponseTxCount": 0,
                                "markerResponseRxCount": 0,
                                "lacpdusRxCount": 0,
                                "lacpdusTxCount": 454,
                                "markersTxCount": 0,
                                "markersRxCount": 0,
                            }
                        }
                    }
                },
                "orphanPorts": {},
            }
        ],
        "side_effect": [],
        "expected_result": "success",
        "expected_messages": [],
    },
    {
        "name": "failure",
        "eos_data": [
            {
                "portChannels": {
                    "Port-Channel42": {
                        "interfaces": {
                            "Ethernet8": {
                                "actorPortStatus": "noAgg",
                                "illegalRxCount": 666,
                                "markerResponseTxCount": 0,
                                "markerResponseRxCount": 0,
                                "lacpdusRxCount": 0,
                                "lacpdusTxCount": 454,
                                "markersTxCount": 0,
                                "markersRxCount": 0,
                            }
                        }
                    }
                },
                "orphanPorts": {},
            }
        ],
        "side_effect": [],
        "expected_result": "failure",
        "expected_messages": ["The following port-channels have recieved illegal lacp packets on the following ports: [{'Port-Channel42': 'Ethernet8'}]"],
    },
]


INPUT_LOOPBACK_COUNT: List[Dict[str, Any]] = [
    {
        "name": "success",
        "eos_data": [
            {
                "interfaces": {
                    "Loopback42": {
                        "name": "Loopback42",
                        "interfaceStatus": "connected",
                        "interfaceAddress": {"ipAddr": {"maskLen": 0, "address": "0.0.0.0"}, "unnumberedIntf": "Vlan42"},
                        "ipv4Routable240": False,
                        "lineProtocolStatus": "up",
                        "mtu": 65535,
                    },
                    "Loopback666": {
                        "name": "Loopback666",
                        "interfaceStatus": "connected",
                        "interfaceAddress": {"ipAddr": {"maskLen": 32, "address": "6.6.6.6"}},
                        "ipv4Routable240": False,
                        "lineProtocolStatus": "up",
                        "mtu": 65535,
                    },
                }
            }
        ],
        "side_effect": 2,
        "expected_result": "success",
        "expected_messages": [],
    },
    {
        "name": "failure-loopback-down",
        "eos_data": [
            {
                "interfaces": {
                    "Loopback42": {
                        "name": "Loopback42",
                        "interfaceStatus": "connected",
                        "interfaceAddress": {"ipAddr": {"maskLen": 0, "address": "0.0.0.0"}, "unnumberedIntf": "Vlan42"},
                        "ipv4Routable240": False,
                        "lineProtocolStatus": "up",
                        "mtu": 65535,
                    },
                    "Loopback666": {
                        "name": "Loopback666",
                        "interfaceStatus": "connected",
                        "interfaceAddress": {"ipAddr": {"maskLen": 32, "address": "6.6.6.6"}},
                        "ipv4Routable240": False,
                        "lineProtocolStatus": "down",
                        "mtu": 65535,
                    },
                }
            }
        ],
        "side_effect": 2,
        "expected_result": "failure",
        "expected_messages": ["The following Loopbacks are not up: ['Loopback666']"],
    },
    {
        "name": "failure-count-loopback",
        "eos_data": [
            {
                "interfaces": {
                    "Loopback42": {
                        "name": "Loopback42",
                        "interfaceStatus": "connected",
                        "interfaceAddress": {"ipAddr": {"maskLen": 0, "address": "0.0.0.0"}, "unnumberedIntf": "Vlan42"},
                        "ipv4Routable240": False,
                        "lineProtocolStatus": "up",
                        "mtu": 65535,
                    },
                }
            }
        ],
        "side_effect": 2,
        "expected_result": "failure",
        "expected_messages": ["Found 1 Loopbacks when expecting 2"],
    },
    {
        "name": "skipped",
        "eos_data": [
            {
                "interfaces": {
                    "Loopback42": {
                        "name": "Loopback42",
                        "interfaceStatus": "connected",
                        "interfaceAddress": {"ipAddr": {"maskLen": 0, "address": "0.0.0.0"}, "unnumberedIntf": "Vlan42"},
                        "ipv4Routable240": False,
                        "lineProtocolStatus": "up",
                        "mtu": 65535,
                    },
                }
            }
        ],
        "side_effect": None,
        "expected_result": "skipped",
        "expected_messages": ["VerifyLoopbackCount was not run as no number value was given."],
    },
]


INPUT_SVI: List[Dict[str, Any]] = [
    {
        "name": "success",
        "eos_data": [
            {
                "interfaces": {
                    "Vlan42": {
                        "name": "Vlan42",
                        "interfaceStatus": "connected",
                        "interfaceAddress": {"ipAddr": {"maskLen": 24, "address": "11.11.11.11"}},
                        "ipv4Routable240": False,
                        "lineProtocolStatus": "up",
                        "mtu": 1500,
                    }
                }
            }
        ],
        "side_effect": [],
        "expected_result": "success",
        "expected_messages": [],
    },
    {
        "name": "failure",
        "eos_data": [
            {
                "interfaces": {
                    "Vlan42": {
                        "name": "Vlan42",
                        "interfaceStatus": "notconnect",
                        "interfaceAddress": {"ipAddr": {"maskLen": 24, "address": "11.11.11.11"}},
                        "ipv4Routable240": False,
                        "lineProtocolStatus": "lowerLayerDown",
                        "mtu": 1500,
                    }
                }
            }
        ],
        "side_effect": [],
        "expected_result": "failure",
        "expected_messages": ["The following SVIs are not up: ['Vlan42']"],
    },
]