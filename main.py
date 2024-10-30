import struct
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow

import mainWindow
import mbr_parser

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
        print(f"  Partition Type: {hex(part['type'])} ({mbr_parser.DOS_PARTITIONS.get(part['type'], 'Unknown')})")
        print(f"  Start LBA: {part['start_lba']}")
        print(f"  Number of Sectors: {part['num_sectors']}")
        print(f"  Estimated Size (MB): {part['num_sectors'] * 512 / (1024 * 1024)}")
        print("")



# 点击按钮时的槽函数
def on_button_clicked():
    print("Button clicked")
    chosen = ui.comboBox.currentText()
    # 提取所选的磁盘编号并生成磁盘路径
    disk_number = int(chosen.split()[1][:-1])
    disk_path = fr"\\.\PhysicalDrive{disk_number}"
    print(disk_path)
    # 读取MBR数据
    mbr_data = mbr_parser.read_mbr(disk_path)

    # 解析MBR数据
    if mbr_data:
        partitions = parse_mbr(mbr_data)

        if partitions:
           print_partition_info(partitions)
        else:
            print("Failed to parse partition table.")
    else:
        print("Failed to read MBR data.")

    # 显示解析结果
    ui.text_display.clear()
    for idx, part in enumerate(partitions):
        ui.text_display.append(f"Partition {idx + 1}:")
        ui.text_display.append(f"  Boot Flag: {hex(part['boot_flag'])}")
        hex_string = '0x' + part['start_chs'].hex()
        ui.text_display.append(f"  Start CHS: {hex_string}")  # 3字节
        ui.text_display.append(f"  Partition Type: {hex(part['type'])} ({mbr_parser.DOS_PARTITIONS.get(part['type'], 'Unknown')})")
        ui.text_display.append(f"  Start LBA: {part['start_lba']}")
        ui.text_display.append(f"  Number of Sectors: {part['num_sectors']}")
        ui.text_display.append(f"  Estimated Size (MB): {part['num_sectors'] * 512 / (1024 * 1024)}")
        ui.text_display.append("")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    ui = mainWindow.Ui_MainWindow()
    ui.setupUi(MainWindow)
    # 获取磁盘信息
    drives = mbr_parser.list_physical_drives_with_partition_type()
    # 提取磁盘名称和分区类型
    drive_names_and_types = mbr_parser.extract_drive_names_and_types(drives)
    # 添加到下拉框
    ui.comboBox.addItems(drive_names_and_types)
    # 当点击按钮时，打印选择的磁盘信息
    ui.pushButton.clicked.connect(on_button_clicked)

    MainWindow.show()
    sys.exit(app.exec_())
