#! /usr/bin/python3

import parted
from tkinter import filedialog
import tkinter as tk
import subprocess
import os
import sys
import re
from PIL import ImageTk, Image
from _ped import DiskException

DEBUG = True

version = 0.2

raid_disks = []
disk_dict = {}
partition_dict = {}

script_dir = os.path.abspath(os.path.dirname(sys.argv[0]))

def smart():
    subprocess.run(f'xfce4-terminal --command="/bin/bash -c \\\"/usr/bin/crazy; read -p \\\\\\"Press enter to continue...\\\\\\"\\\""', shell=True)

def clonezilla():
    subprocess.run(f'xfce4-terminal --command="/usr/bin/clonezilla"', shell=True)

def mount(partition_path):
    subprocess.run(f'umount -f /mnt; mount -t auto {partition_path} /mnt; doublecmd -L /mnt -R / --no-splash', shell=True)

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
    subprocess.run(f'xfce4-terminal --command="/bin/bash -c \\\"./HDcleaner/clean_disk.sh {partition_path};read -p \\\\\\"Press enter to continue...\\\\\\"\\\"""', shell=True)

def windows_admin_reset(partition_path):
    subprocess.run(f'xfce4-terminal --command="/bin/bash -c \\\"umount -f /mnt; mount -t auto {partition_path} /mnt; /usr/bin/chntpw /mnt/Windows/System32/config/SAM;read -p \\\\\\"Press enter to continue...\\\\\\"\\\"""', shell=True)

# Should be executed as root
if os.getuid() != 0:
    print('Error: Should be executed with root privileges, exiting....')
    exit(1)

# Get all possible disk that are used in software raid
# These need to be excluded because the partition table
# could not be read.
if os.path.isfile('/proc/mdstat'):
    file_handel=open('/proc/mdstat', 'r')   
    raid_disks = list(map(lambda x: "/dev/" + x.split('[')[0], file_handel.readlines()[1].split()[4:]))
    file_handel.close()
 
for device in parted.getAllDevices():
    # Skip raid disks and the Raid array itsel
    if re.search('^/dev/nvme[0..9]+n[0-9]+$', device.path):
        disk_disktype = 'nvme' # if regular expression matches for the device name, its and nvme disk
    elif re.search('^/dev/sr[0..9]+$', device.path):
        continue # Skip cdrom/dvd drive
    elif subprocess.run('lsblk -no rota ' + device.path, shell=True, capture_output=True).stdout.decode('UTF-8').strip():
        disk_disktype = 'hdd' # if rotational its a regular hdd
    else:
        disk_disktype = 'ssd' # All other cases its and ssd
    if DEBUG: print(f'Found disk: {device.model} Type: {disk_disktype}')
    if device.path in raid_disks or device.model == 'Linux Software RAID Array':
        continue 
    else:     
        try:
            disk=parted.newDisk(device)
        except DiskException:
            # Empty disk, add device and continue to next device
            disk_disktype = subprocess.run('lsblk -no rota ' + device.path, shell=True, capture_output=True).stdout.decode('UTF-8').strip()
            disk_dict[device.path] = {'partitions': [], 'disktype': disk_disktype}
            continue
    
    
    if hasattr(disk, 'partitions'):
        for partition in disk.partitions:
            partition_label = subprocess.run('lsblk -no lable ' + partition.path, shell=True, capture_output=True).stdout.decode('UTF-8').strip().lower()
            partition_fstype = subprocess.run('lsblk -no fstype ' + partition.path, shell=True, capture_output=True).stdout.decode('UTF-8').strip().lower()
            if partition_label == 'vtoyefi' or 'ventoy' in partition_label:
                continue # Ventoy USB stick should be skipped
            else:
                partition_dict['path'] = partition.path
            if partition_fstype == 'ntfs' and (partition_label == '' or partion_label == 'windows'):
                partition_dict['possible_windows_installation'] = True
            else:
                partition_dict['possible_windows_installation'] = False
            if not device.path in disk_dict.keys(): disk_dict[device.path] = {'partitions': [], 'disktype': disk_disktype}
            disk_dict[device.path]['partitions'].append(partition_dict)
            partition_dict.clear()

    else:
        # No partitions on this disk, add device and continue to next device
        disk_dict[device.path] = {'partitions': [], 'disktype': disk_disktype}
        continue # If no partitions are availabe, skip to next


window = tk.Tk()
window.title(f'RescueDiskUtil V{version}')

button = tk.Button(window, text="S.M.A.R.T", command=lambda: smart())
button.grid(row=0, column=3)
button = tk.Button(window, text="Clone", command=lambda: clonezilla())
button.grid(row=0, column=4)

image_dict = {
        'arrow': ImageTk.PhotoImage(Image.open(f'{script_dir}/arrow.png')),
        'ssd': ImageTk.PhotoImage(Image.open(f'{script_dir}/ssd.png')),
        'hdd': ImageTk.PhotoImage(Image.open(f'{script_dir}/hdd.png')),
        'nvme': ImageTk.PhotoImage(Image.open(f'{script_dir}/nvme.png'))
}

i=1
for disk_path in disk_dict.keys():
    disk_type = disk_dict[disk_path]['disktype']
    label = tk.Label(window, image=image_dict[disk_type])
    label.grid(row=i, column=0)
    label = tk.Label(window, text=disk_path)
    label.grid(row=i, column=1)
    button = tk.Button(window, text="gparted", command=lambda path=disk_path: gparted(path))
    button.grid(row=i, column=2)
    button = tk.Button(window, text="ddrescue", command=lambda path=disk_path: ddrescue(path))
    button.grid(row=i, column=3)
    # Check if submodule is checked-out, otherwise HDcleaner can not be used
    if os.path.isdir('./HDcleaner/'):
        button = tk.Button(window, text="erase", command=lambda path=disk_path: erase(path))
        button.grid(row=i, column=4)
    i+=1
    for partition_dict in disk_dict[disk_path]['partitions']:
        if DEBUG: print('Partition info:', partition_dict)
        label = tk.Label(window, image=image_dict['arrow'])
        label.grid(row=i, column=0)
        partition_path = partition_dict['path']
        label = tk.Label(window, text=partition_path)
        label.grid(row=i, column=1)
        button = tk.Button(window, text="mount", command=lambda path=partition_path: mount(path))
        button.grid(row=i, column=2)
        button = tk.Button(window, text="ddrescue", command=lambda path=partition_path: ddrescue(path))
        button.grid(row=i, column=3)
        if partition_dict['possible_windows_installation']:
            button = tk.Button(window, text="Admin reset", command=lambda path=partition_path: windows_admin_reset(path))
            button.grid(row=i, column=4)
        i+=1

# Start the GUI
window.mainloop()
