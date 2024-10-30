import wmi
import struct
import subprocess


# DOS分区类型
DOS_PARTITIONS = {
    0x00: "Empty",
    0x01: "FAT12, CHS",
    0x04: "FAT16, 16-32 MB, CHS",
    0x05: "Microsoft Extended, CHS",
    0x06: "FAT16, 32 MB-2GB, CHS",
    0x07: "NTFS",
    0x0b: "FAT32, CHS",
    0x0c: "FAT32, LBA",
    0x0e: "FAT16, 32 MB-2GB, LBA",
    0x0f: "Microsoft Extended, LBA",
    0x11: "Hidden Fat12, CHS",
    0x14: "Hidden FAT16, 16-32 MB, CHS",
    0x16: "Hidden FAT16, 32 MB-2GB, CHS",
    0x1b: "Hidden FAT32, CHS",
    0x1c: "Hidden FAT32, LBA",
    0x1e: "Hidden FAT16, 32 MB-2GB, LBA",
    0x42: "Microsoft MBR, Dynamic Disk",
    0x82: "Solaris x86 -or- Linux Swap",
    0x83: "Linux",
    0x84: "Hibernation",
    0x85: "Linux Extended",
    0x86: "NTFS Volume Set",
    0x87: "NTFS Volume SET",
    0xa0: "Hibernation",
    0xa1: "Hibernation",
    0xa5: "FreeBSD",
    0xa6: "OpenBSD",
    0xa8: "Mac OSX",
    0xa9: "NetBSD",
    0xab: "Mac OSX Boot",
    0xb7: "BSDI",
    0xb8: "BSDI swap",
    # FIXME: I'm pretty sure 0xdb is a recovery partition
    0xdb: "Recovery Partition",
    0xde: "Dell Diagnostic Partition",
    0xee: "EFI GPT Disk",
    0xef: "EFI System Partition",
    0xfb: "Vmware File System",
    0xfc: "Vmware swap",
    # FIXME Add flag for VirtualBox Partitions
}

# 列出物理磁盘
def list_physical_drives_with_partition_type():
    # 创建WMI对象用于查询磁盘信息
    c = wmi.WMI()
    disks_info = []

    # 获取分区类型信息
    command = "powershell -Command \"Get-Disk | Select-Object -Property Number,PartitionStyle\""
    result = subprocess.run(command, stdout=subprocess.PIPE, text=True, shell=True)
    partition_info = result.stdout.strip().splitlines()[2:]  # 跳过头两行
    partition_dict = {}

    # 解析分区类型信息并存储到字典中
    for line in partition_info:
        parts = line.split()
        if len(parts) >= 2:
            disk_number = int(parts[0])
            partition_style = parts[1]
            partition_dict[disk_number] = partition_style

    # 遍历物理磁盘，获取详细信息
    for disk in c.Win32_DiskDrive():
        try:
            disk_number = int(''.join(filter(str.isdigit, disk.DeviceID)))  # 提取物理磁盘编号
        except ValueError:
            disk_number = -1  # 如果无法提取编号，设置为无效值
        partition_style = partition_dict.get(disk_number, "Unknown")

        # 构造磁盘信息字典
        disk_info = {
            "Device ID": disk.DeviceID,
            "Model": disk.Model,
            "Size (GB)": int(disk.Size) // (1024 ** 3),
            "Partitions": disk.Partitions,
            "Partition Style": partition_style
        }
        disks_info.append(disk_info)

    return disks_info

# 打印物理磁盘信息
def list_physical_drives(drives):
    # drives = list_physical_drives_with_partition_type()
    for drive in drives:
        for key, value in drive.items():
            print(f"{key}: {value}")
        print("-" * 40)

# 提取磁盘名称和类型
def extract_drive_names_and_types(drives):
    drive_names_and_types = []
    for drive in drives:
        # 处理device_id，使其只保留最后的数字
        device_id = drive.get("Device ID", "Unknown")
        device_id = ''.join(filter(str.isdigit, device_id))
        name = drive.get("Model", "Unknown")
        partition_style = drive.get("Partition Style", "Unknown")
        drive_names_and_types.append(f"Device {device_id}: {name}: {partition_style}")
    return drive_names_and_types

# 打印磁盘名称和类型
def print_drive_names_and_types(drive_names_and_types):
    for drive in drive_names_and_types:
        print(drive)

# 读取MBR数据
def read_mbr(disk_path):
    try:
        with open(disk_path, "rb") as disk:
            # 读取前512字节（MBR内容）
            mbr_data = disk.read(512)
        return mbr_data
    except Exception as e:
        print(f"Error reading disk {disk_path}: {e}")
        return None


def parse_mbr(mbr_data):
    if len(mbr_data) != 512:
        print("Invalid MBR data size.")
        return None

    # MBR结构解析
    # 解析分区表项（447到510字节，共4个分区，每个16字节）
    partition_table = mbr_data[446:510]
    partitions = []

    for i in range(4):
        entry = partition_table[i * 16: (i + 1) * 16]
        boot_flag, start_chs, part_type, end_chs, start_lba, num_sectors = struct.unpack("<B3sB3sII", entry)

        # 存储分区信息
        partition_info = {
            "boot_flag": boot_flag,     # 引导标志
            "start_chs": start_chs,     # 起始磁头、扇区、柱面
            "type": part_type,          # 分区类型
            "end_chs": end_chs,         # 结束磁头、扇区、柱面
            "start_lba": start_lba,     # 逻辑起始扇区号
            "num_sectors": num_sectors  # 分区扇区数
        }
        partitions.append(partition_info)

    return partitions

# 打印分区信息
def print_partition_info(partitions):
    for idx, part in enumerate(partitions):
        print(f"Partition {idx + 1}:")
        print(f"  Boot Flag: {hex(part['boot_flag'])}")
        hex_string = '0x' + part['start_chs'].hex()
        print(f"  Start CHS: {hex_string}")  # 3字节
        print(f"  Partition Type: {hex(part['type'])} ({DOS_PARTITIONS.get(part['type'], 'Unknown')})")
        print(f"  Start LBA: {part['start_lba']}")
        print(f"  Number of Sectors: {part['num_sectors']}")
        print(f"  Estimated Size (MB): {part['num_sectors'] * 512 / (1024 * 1024)}")
        print("")

# 以下为后端测试代码
def main():
    # 列出物理磁盘，查看物理磁盘分区类型
    drives = list_physical_drives_with_partition_type()
    list_physical_drives(drives)   #后端调试用

    extract_drive_names_and_types(drives)
    print_drive_names_and_types(extract_drive_names_and_types(drives))

    disk_path = r"\\.\PhysicalDrive2"  # 选择第一个物理磁盘
    mbr_data = read_mbr(disk_path)
    # print(mbr_data)

    if mbr_data:
        partitions = parse_mbr(mbr_data)

        if partitions:
            print_partition_info(partitions)
        else:
            print("Failed to parse partition table.")
    else:
        print("Failed to read MBR data.")


if __name__ == "__main__":
    main()
