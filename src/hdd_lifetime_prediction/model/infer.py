from .smartctl import SMARTAttributes
from .model import Model

def predict_lifetime(
    smart_attributes: SMARTAttributes,
    model: Model
):
    """Predict the lifetime of a hard drive based on its SMART attributes.

    Args:
        smart_attributes (SMARTAttributes): The SMART attributes of the hard drive.
        model (Model): The model used to predict the lifetime.

    Returns:
        float: The predicted lifetime of the hard drive.
    """
    return model.predict(smart_attributes)


def predict_full(
    smart_attributes: SMARTAttributes,
    model: Model
):
    """Predict the lifetime of a hard drive based on its SMART attributes.

    Args:
        smart_attributes (SMARTAttributes): The SMART attributes of the hard drive.
        model (Model): The model used to predict the lifetime.

    Returns:
        float: The predicted lifetime of the hard drive.
    """
    return model.predict_full(smart_attributes)


if __name__ == "__main__":
    from .smartctl import parse_smartctl
    from .model import TreeModel
    from importlib.resources import files

    smart_output = """
    smartctl 7.2 2020-12-30 r5155 [x86_64-linux-5.15.0-130-generic] (local build)
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
199 UDMA_CRC_Error_Count    0x003e   200   200   000    Old_age   Always       -       0
    """

    smart_attributes = parse_smartctl(smart_output)
    model = TreeModel(
        files("hdd_lifetime_prediction.model")
        .joinpath("long-term-params.yaml")
    )

    predicted_lifetime = predict_lifetime(smart_attributes, model)
    print(f"Predicted lifetime: {predicted_lifetime}")
    print(f"Predicted stats: {predict_full(smart_attributes, model)}")
