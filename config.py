VARIABLE_NAMES = {
    "XMEAS-1":"A Feed Flow",
    "XMEAS-2":"D Feed Flow",
    "XMEAS-3":"E Feed Flow",
    "XMEAS-4":"A & C Feed Flow",
    "XMEAS-5":"Recycle Flow",
    "XMEAS-6":"Reactor Feed Rate",
    "XMEAS-7":"Reactor Pressure",
    "XMEAS-8":"Reactor Level",
    "XMEAS-9":"Reactor Temperature",
    "XMEAS-10":"Purge Rate",
    "XMEAS-11":"Separator Temperature",
    "XMEAS-12":"Separator Level",
    "XMEAS-13":"Separator Pressure",
    "XMEAS-14":"Separator Underflow",
    "XMEAS-15":"Stripper Level",
    "XMEAS-16":"Stripper Pressure",
    "XMEAS-17":"Stripper Underflow",
    "XMEAS-18":"Stripper Temperature",
    "XMEAS-19":"Stripper Steam Flow",
    "XMEAS-20":"Compressor Work",
    "XMEAS-21":"Reactor CW Outlet Temp",
    "XMEAS-22":"Separator CW Outlet Temp",
    "XMEAS-23":"Feed Composition A",
    "XMEAS-24":"Feed Composition B",
    "XMEAS-25":"Feed Composition C",
    "XMEAS-26":"Feed Composition D",
    "XMEAS-27":"Feed Composition E",
    "XMEAS-28":"Feed Composition F",
    "XMEAS-29":"Purge Composition A",
    "XMEAS-30":"Purge Composition B",
    "XMEAS-31":"Purge Composition C",
    "XMEAS-32":"Purge Composition D",
    "XMEAS-33":"Purge Composition E",
    "XMEAS-34":"Purge Composition F",
    "XMEAS-35":"Purge Composition G",
    "XMEAS-36":"Purge Composition H",
    "XMEAS-37":"Product Composition D",
    "XMEAS-38":"Product Composition E",
    "XMEAS-39":"Product Composition F",
    "XMEAS-40":"Product Composition G",
    "XMEAS-41":"Product Composition H",
    "XMV-1":"D Feed Valve",
    "XMV-2":"E Feed Valve",
    "XMV-3":"A Feed Valve",
    "XMV-4":"A & C Feed Valve",
    "XMV-5":"Recycle Valve",
    "XMV-6":"Purge Valve",
    "XMV-7":"Separator Outlet Valve",
    "XMV-8":"Stripper Product Valve",
    "XMV-9":"Steam Valve",
    "XMV-10":"Reactor Cooling Water Valve",
    "XMV-11":"Condenser Cooling Water Valve",
    "XMV-12":"Agitator Speed"
}

FAULT_INFO = {
    "Normal": (
        "Normal Operation",
        "Plant operating normally."
    ),

    "Fault_1": (
        "A/C Feed Ratio Disturbance",
        "Check A/C feed ratio, flow transmitters and control valves."
    ),

    "Fault_2": (
        "B Composition Disturbance",
        "Check raw material composition and analyzer."
    ),

    "Fault_3": (
        "D Feed Temperature Disturbance",
        "Check D feed heater and temperature controller."
    ),

    "Fault_4": (
        "Reactor Cooling Water Inlet Temperature",
        "Inspect reactor cooling water system."
    ),

    "Fault_5": (
        "Condenser Cooling Water Inlet Temperature",
        "Inspect condenser cooling water flow and temperature."
    ),

    "Fault_6": (
        "A Feed Loss",
        "Check feed pump, suction line and feed control valve."
    ),

    "Fault_7": (
        "C Header Pressure Loss",
        "Check upstream pressure and control valve."
    ),

    "Fault_8": (
        "A, B and C Feed Composition",
        "Verify feed composition analyzer."
    ),

    "Fault_9": (
        "D Feed Composition",
        "Check raw material quality."
    ),

    "Fault_10": (
        "C Feed Temperature",
        "Inspect feed heater."
    ),

    "Fault_11": (
        "Reactor Cooling Water Valve",
        "Inspect reactor CW control valve."
    ),

    "Fault_12": (
        "Condenser Cooling Water Valve",
        "Inspect condenser CW valve."
    ),

    "Fault_13": (
        "Reaction Kinetics Change",
        "Investigate catalyst or reaction conditions."
    ),

    "Fault_14": (
        "Reactor Cooling Failure",
        "Check cooling duty and reactor temperature."
    ),

    "Fault_15": (
        "Condenser Performance Loss",
        "Inspect condenser fouling and cooling system."
    ),

    "Fault_16": (
        "Unknown Process Disturbance",
        "Perform detailed process investigation."
    ),

    "Fault_17": (
        "Unknown Process Disturbance",
        "Check process measurements."
    ),

    "Fault_18": (
        "Unknown Process Disturbance",
        "Review process history."
    ),

    "Fault_19": (
        "Unknown Process Disturbance",
        "Check instrumentation."
    ),

    "Fault_20": (
        "Unknown Process Disturbance",
        "Inspect plant operating conditions."
    ),

    "Fault_21": (
        "Valve Sticking",
        "Inspect manipulated valves for sticking."
    )
}

for i in range(2, 22):
    if f"Fault_{i}" not in FAULT_INFO:
        FAULT_INFO[f"Fault_{i}"] = (
            f"Fault {i}",
            "Refer to Tennessee Eastman fault documentation."
        )
ENGINEERING_LIMITS = {

    "XMEAS-7": ("Reactor Pressure", 2600, 3000),

    "XMEAS-9": ("Reactor Temperature", 110, 130),

    "XMEAS-12": ("Separator Pressure", 2500, 3200),

    "XMEAS-15": ("Stripper Pressure", 2600, 3200),

    "XMEAS-18": ("Condenser Temperature", 20, 60),

    "XMEAS-20": ("Cooling Water Flow", 0, 100)
}