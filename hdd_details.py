import argparse
import subprocess
import re
import psutil
from datetime import timedelta

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

for mount_point in mounts:
    info = get_drive_info(mount_to_device[mount_point])
    drive_status = DriveStatus(mount_point, info)
    if drive_status.power_on_hours is not None:
        drive_status.power_on_hours = convert_power_on_hours(drive_status.power_on_hours)
    drive_statuses.append(drive_status)

parser = argparse.ArgumentParser(description="Get drive information and optionally sort by a selected header.")
headers = ["Device", "Model/Device", "Serial Number", "Size GiBs", "Capacity", "Status", "Power On Hours", "Temperature"]
parser.add_argument("-sort", choices=headers, help="Sort by the selected header")
args = parser.parse_args()

if args.sort in headers:
    drive_statuses.sort(key=lambda status: status.to_table_row()[headers.index(args.sort)])

max_widths = [max(len(header), max(len(str(item)) for item in column)) for header, column in zip(headers, zip(*[drive_status.to_table_row() for drive_status in drive_statuses]))]

print(" | ".join(header.ljust(width) for header, width in zip(headers, max_widths)))
print("-" * sum(max_widths + [len(max_widths) + 13]))

for drive_status in drive_statuses:
    table_row = drive_status.to_table_row()
    formatted_row = [str(item).ljust(width) for item, width in zip(table_row, max_widths)]
    print(" | ".join(formatted_row))