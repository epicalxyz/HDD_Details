import argparse
import subprocess
import re
import psutil
import json
from datetime import timedelta

# This script does not generate an output in the terminal but creates a .JSON file with info about the hdds 

MOUNT_PREFIX = '/mnt/hdd'

class DriveStatus:
    def __init__(self, device, info):
        self.device = device
        self.model_family = ''
        self.device_model = ''
        self.serial_number = ''
        self.size_gibs = None
        self.capacity = ''
        self.status = ''
        self.power_on_hours = None
        self.temperature = None
        self.set_info_attributes(info.splitlines())

    def to_dict(self, drive_number):
        return {
            "drive_number": drive_number,
            "device": self.device,
            "model": self.model_family if self.model_family else self.device_model,
            "serial": self.serial_number,
            "capacity": self.capacity,
            "power on hours": self.power_on_hours,
            "temperature": self.temperature
        }

    def set_info_attributes(self, data):
        parsing_info = False
        power_on_hours_found = False
        temperature_found = False

        for line in data:
            if line.startswith('=== START OF INFORMATION SECTION ==='):
                parsing_info = True
                continue
            if parsing_info:
                parts = line.split(':')
                if len(parts) >= 2:
                    key = parts[0].strip()
                    value = parts[1].strip()
                    if key == 'Model Family':
                        self.model_family = value
                    elif key == 'Device Model':
                        self.device_model = value
                    elif key == 'Serial Number':
                        self.serial_number = value
                    elif key == 'User Capacity':
                        size, capacity = value.split(' bytes [')
                        self.size_gibs = round(int(size.replace(',', '')) / (1024 ** 3), 3)
                        self.capacity = capacity.strip(']')
                    elif key == 'SMART overall-health self-assessment test result':
                        self.status = value

            if line.startswith("SMART Attributes Data Structure revision number:"):
                parsing_info = True

            if parsing_info:
                if line.startswith("  9 Power_On_Hours"):
                    parts = line.split("-")
                    if len(parts) >= 2:
                        self.power_on_hours = parts[1].strip()

                if line.startswith("194 Temperature_Celsius"):
                    parts = line.split("-")
                    if len(parts) == 2:
                        self.temperature = parts[1].strip()

    def to_table_row(self):
        model_device = self.model_family if self.model_family else self.device_model
        return [self.device, model_device, self.serial_number,
                self.size_gibs, self.capacity, self.status,
                self.power_on_hours, self.temperature]

def get_drive_info(device):
    command = ['smartctl', '-a', '-d', 'sat', device]
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return result.stdout

def convert_power_on_hours(raw_value):
    try:
        if "(" in raw_value:
            match = re.search(r'(\d+)\s*\(', raw_value)
            if match:
                raw_hours = int(match.group(1))
                power_on_time = timedelta(hours=raw_hours)
                years = power_on_time.days // 365
                months = (power_on_time.days % 365) // 30
                days = (power_on_time.days % 365) % 30
                return f"{years} years, {months} months, {days} days"
        elif raw_value.isdigit():
            raw_hours = int(raw_value)
            power_on_time = timedelta(hours=raw_hours)
            years = power_on_time.days // 365
            months = (power_on_time.days % 365) // 30
            days = (power_on_time.days % 365) % 30
            return f"{years} years, {months} months, {days} days"
        else:
            return raw_value
    except ValueError:
        return raw_value

mounts = [part.mountpoint for part in psutil.disk_partitions() if part.mountpoint.startswith(MOUNT_PREFIX)]

mount_to_device = {part.mountpoint: part.device for part in psutil.disk_partitions()}

drive_statuses = []

for idx, mount_point in enumerate(mounts, start=1):
    info = get_drive_info(mount_to_device[mount_point])
    drive_status = DriveStatus(mount_point, info)
    if drive_status.power_on_hours is not None:
        drive_status.power_on_hours = convert_power_on_hours(drive_status.power_on_hours)
    drive_statuses.append(drive_status)

# Writing to JSON file
output_file_path = "drive_info.json"

with open(output_file_path, "w") as json_file:
    json.dump({"hard-drives": [drive_status.to_dict(drive_number) for drive_number, drive_status in enumerate(drive_statuses, start=1)]}, json_file, indent=2)

print(f"Drive information written to {output_file_path}")