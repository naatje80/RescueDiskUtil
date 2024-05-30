#! /usr/bin/python3

import parted
from tkinter import filedialog
import tkinter as tk
import subprocess
import os

version = 0.1

raid_disks = []
partition_list = []

def mount(partition_path):
    subprocess.run(f'umount -f /mnt; mount -t auto {partition_path} /mnt; thunar /mnt', shell=True)

def gparted(partition_path):
    subprocess.run(f'gparted {partition_path}', shell=True)

def ddrescue(partition_path):
    window.destination_path = filedialog.askdirectory(initialdir = "/")
    # If canceled destination directory, do not continue ddrescue
    if window.destination_path == ():
        return
    partition_name = partition_path.split('/')[-1]
    if os.path.isfile(f'{window.destination_path}/{partition_name}.map'):
        os.remove(f'{window.destination_path}/{partition_name}.map')
    subprocess.Popen(f'ddrescue {partition_path} {window.destination_path}/{partition_name}.img {window.destination_path}/{partition_name}.map > /tmp/ddrescue.log 2>&1', shell=True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    subprocess.run(f'./ddrescueview -r 5s {window.destination_path}/{partition_name}.map', shell=True)

def erase(partition_path):
    subprocess.run(f'xfce4-terminal --command="./HDcleaner/clean_disk.sh {partition_path}"', shell=True)

# Get all possible disk that are used in software raid
# These need to be excluded because the partition table
# could not be read.
if os.path.isfile('/proc/mdstat'):
    file_handel=open('/proc/mdstat', 'r')   
    raid_disks = list(map(lambda x: "/dev/" + x.split('[')[0], file_handel.readlines()[1].split()[4:]))
    file_handel.close()
 
for device in parted.getAllDevices():
    # Skip raid disks and the Raid array itsel
    #print(device.model)
    if device.path in raid_disks or device.model == 'Linux Software RAID Array':
        continue 
    else:     
        disk=parted.newDisk(device)

    # Also add device to list of tuples
    partition_list.append((device.path, False)) 

    if hasattr(disk, 'partitions'):
        for partition in disk.partitions:
            partition_list.append((partition.path, True))
    else:
        continue


window = tk.Tk()
window.title(f'RescueDiskUtil V{version}')

i=0
for partition_path, is_partition in partition_list:
    label = tk.Label(window, text=partition_path)
    label.grid(row=i, column=0)
    if is_partition:
        button = tk.Button(window, text="mount", command=lambda path=partition_path: mount(path))
        button.grid(row=i, column=2)
    else:
        button = tk.Button(window, text="gparted", command=lambda path=partition_path: gparted(path))
        button.grid(row=i, column=2)
    button = tk.Button(window, text="ddrescue", command=lambda path=partition_path: ddrescue(path))
    button.grid(row=i, column=3)
    # Check if submodule is checked-out, otherwise HDcleaner can not be used
    if os.path.isdir('./HDcleaner/') and not is_partition:
        button = tk.Button(window, text="erase", command=lambda path=partition_path: erase(path))
        button.grid(row=i, column=4)
    i+=1

window.mainloop()
