import re
from dataclasses import dataclass


@dataclass
class SMARTAttribute:
    id: str
    name: str
    raw: str
    normalized: str
    worst: str


@dataclass
class SMARTAttributes:
    attributes: list[SMARTAttribute]


def parse_smartctl(smartctl_output: str) -> SMARTAttributes:
    """Parse the output of the 'smartctl' command.

    Args:
        smartctl_output: The output of the 'smartctl' command. This command should be run as `smartctl -A /dev/sdx`

    Returns: a SMARTAttributes object containing the parsed data.
    """
    # Initialize the dictionary to store the parsed data
    parsed_data = {}

    # Split the output into lines
    lines = smartctl_output.splitlines()

    relevant_lines = []
    # Look for the line that looks like ID# Attribute_Name ...
    # and between there and the next blank line
    _relevant = False
    header = ""
    for line in lines:
        if re.match(r"ID#.*ATTRIBUTE_NAME.*VALUE.*RAW_VALUE", line):
            _relevant = True
            header = line
            continue
        if not _relevant:
            continue
        if not line:
            break
        relevant_lines.append(line)

    if not header:
        raise ValueError("Could not parse SMART data")

    # Parse the header lines to name: (start, stop)
    colnames = header.split()
    column_indices = {}
    for i, colname in enumerate(colnames):
        start = header.index(colname)
        next_colname = colnames[i + 1] if i + 1 < len(colnames) else None
        stop = header.index(next_colname) - 1 if next_colname else None
        column_indices[colname] = (start, stop)

    # Iterate over the lines containing the attribute data
    attributes = []
    for line in relevant_lines:
        # Extract the attribute data
        attribute_id = line[slice(*column_indices["ID#"])].strip()
        attribute_name = line[slice(*column_indices["ATTRIBUTE_NAME"])].strip()
        raw_value = line[slice(*column_indices["RAW_VALUE"])].strip()
        normalized_value = line[slice(*column_indices["VALUE"])].strip()
        worst_value = line[slice(*column_indices["WORST"])].strip()

        # Store the attribute data in a new SMARTAttribute
        attribute = SMARTAttribute(
            id=attribute_id,
            name=attribute_name,
            raw=raw_value,
            normalized=normalized_value,
            worst=worst_value,
        )

        attributes += [attribute]

    return SMARTAttributes(attributes)


if __name__ == "__main__":
    from pprint import pprint

    output_to_test = """smartctl 7.2 2020-12-30 r5155 [x86_64-linux-5.15.0-130-generic] (local build)
Copyright (C) 2002-20, Bruce Allen, Christian Franke, www.smartmontools.org

=== START OF READ SMART DATA SECTION ===
SMART Attributes Data Structure revision number: 10
Vendor Specific SMART Attributes with Thresholds:
ID# ATTRIBUTE_NAME          FLAG     VALUE WORST THRESH TYPE      UPDATED  WHEN_FAILED RAW_VALUE
  1 Raw_Read_Error_Rate     0x000f   118   086   006    Pre-fail  Always       -       172762880
  3 Spin_Up_Time            0x0003   094   092   000    Pre-fail  Always       -       0
  4 Start_Stop_Count        0x0032   088   088   020    Old_age   Always       -       12392
  5 Reallocated_Sector_Ct   0x0033   100   100   010    Pre-fail  Always       -       0
  7 Seek_Error_Rate         0x000f   087   060   030    Pre-fail  Always       -       586245897
  9 Power_On_Hours          0x0032   026   026   000    Old_age   Always       -       65573
 10 Spin_Retry_Count        0x0013   100   100   097    Pre-fail  Always       -       0
 12 Power_Cycle_Count       0x0032   100   100   020    Old_age   Always       -       69
184 End-to-End_Error        0x0032   100   100   099    Old_age   Always       -       0
187 Reported_Uncorrect      0x0032   001   001   000    Old_age   Always       -       649
188 Command_Timeout         0x0032   100   100   000    Old_age   Always       -       0
189 High_Fly_Writes         0x003a   100   100   000    Old_age   Always       -       0
190 Airflow_Temperature_Cel 0x0022   067   054   045    Old_age   Always       -       33 (Min/Max 23/37)
191 G-Sense_Error_Rate      0x0032   100   100   000    Old_age   Always       -       0
192 Power-Off_Retract_Count 0x0032   100   100   000    Old_age   Always       -       45
193 Load_Cycle_Count        0x0032   094   094   000    Old_age   Always       -       12392
194 Temperature_Celsius     0x0022   033   046   000    Old_age   Always       -       33 (0 17 0 0 0)
197 Current_Pending_Sector  0x0012   100   098   000    Old_age   Always       -       0
198 Offline_Uncorrectable   0x0010   100   098   000    Old_age   Offline      -       0
199 UDMA_CRC_Error_Count    0x003e   200   200   000    Old_age   Always       -       0"""

    parsed_data = parse_smartctl(output_to_test)
    pprint(parsed_data)
