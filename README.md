# HDD Details

Made using ChatGPT

A Python Script to get SMART details from your Hard-Drives in Linux

All started with me wanting a python script to show me the temperature of the hard drives in a table format, it's summer and I want to keep an eye on them, grow in to this

## Usage

```
Usage:
  sudo python3 hdd_details.py [OPTION ...]

  -sort

  available headers:

    Device
    Model/Device
    Serial Number
    Size GiBs
    Capacity
    Status
    Power On Hours
    Temperature

Sorting is optional
```

## Example Output

```
Device       | Model/Device | Serial Number | Size GiBs | Capacity | Status | Power On Hours            | Temperature
------------------------------------------------------------------------------------------------------------------------
/mnt/hdd6tba | ST6000NM0275 | NYP6LB9Q      | 5589.03   | 6,00 TB  | PASSED | 1 year, 11 months, 9 days | 30 (0 9 0 0 0)
/mnt/hdd6tbb | ST6000NM0275 | ZAD1NNZY      | 5589.03   | 6,00 TB  | PASSED | 1 year, 11 months, 9 days | 30 (0 9 0 0 0)
/mnt/hdd6tbc | ST6000NM0275 | BCR5KJ6M      | 5589.03   | 6,00 TB  | PASSED | 1 year, 11 months, 9 days | 30 (0 9 0 0 0)
/mnt/hdd6tbd | ST6000NM0275 | LMO9VN1P      | 5589.03   | 6,00 TB  | PASSED | 1 year, 11 months, 9 days | 30 (0 9 0 0 0)
/mnt/hdd6tbe | ST6000NM0275 | YUI4WT2S      | 5589.03   | 6,00 TB  | PASSED | 1 year, 11 months, 9 days | 30 (0 9 0 0 0)
/mnt/hdd6tbf | ST6000NM0275 | PZX7RF3D      | 5589.03   | 6,00 TB  | PASSED | 1 year, 11 months, 9 days | 30 (0 9 0 0 0)
/mnt/hdd6tbg | ST6000NM0275 | HJK8MC0N      | 5589.03   | 6,00 TB  | PASSED | 1 year, 11 months, 9 days | 30 (0 9 0 0 0)
```

### Known Issues:

Sorting to header values that contain spacing in the name (Serial Number, Size GiBs, Power On Hours) does not output correctly

## hdd_details_json.py

This script does not generate an output in the terminal but creates a .JSON file with info about the hdds

## Example Output:

```json
{
  "hard-drives": [
    {
      "drive_number": 1,
      "device": "/mnt/hdd6tba",
      "model": "ST6000NM0275",
      "serial": "NYP6LB9Q",
      "capacity": "6,00 TB",
      "power on hours": "1 year, 11 months, 9 days",
      "temperature": "30 (0 9 0 0 0)"
    },
        {
      "drive_number": 2,
      "device": "/mnt/hdd6tbb",
      "model": "ST6000NM0275",
      "serial": "ZAD1NNZY",
      "capacity": "6,00 TB",
      "power on hours": "1 year, 11 months, 9 days",
      "temperature": "30 (0 9 0 0 0)"
    },
    ...
  ]
}
```

### Known Issues:

None
