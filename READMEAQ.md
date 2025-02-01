# MBR解析程序


### 项目目录结构：
```
MBR_parser
├── READMEAQ.md     # 项目说明文档
├── build           # 项目构建过程中的临时文件
├── dist            # 项目构建后的可执行文件
│   └── main.exe
├── main.py         # 项目入口文件
├── main.spec       # 项目构建配置文件
├── mainWindow.py   # 主窗口文件
├── mbr_parser.ico  # 项目图标文件
├── mbr_parser.py   # MBR解析程序文件
└── requirements.txt    # 项目依赖库文件
```
### 项目运行方式：
1. 安装依赖库
```shell
pip install -r requirements.txt
```
2. 运行项目 
PS：此过程注意因为要读取物理磁盘，所以需要管理员权限运行，请使用管理员权限打开
```shell
python main.py
或在IDE中直接运行main.py
或在dist文件夹中直接运行打包生成的main.exe
```

### 项目功能展示：
程序运行界面如下：
![主界面.png](https://s2.loli.net/2024/10/30/tA5pzEOlFcf9Q2I.png)
程序运行结果如下：
![运行结果.png](https://s2.loli.net/2024/10/30/w2VCka3O61notsD.png)




