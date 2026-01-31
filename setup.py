# 或者创建一个setup.py文件，运行一次即可
import os
from pathlib import Path

# 创建所有文件夹
folders = [
    'templates',
    'static/css',
    'static/js',
    'models',
    'utils',
    'data/music',
    'data/outputs'
]

project_root = Path(__file__).parent
for folder in folders:
    (project_root / folder).mkdir(parents=True, exist_ok=True)
    print(f"创建目录: {folder}")

# 创建空文件
files = {
    'templates/index.html': '',  # 第9部分HTML
    'static/css/style.css': '',  # 第10部分CSS
    'static/js/main.js': '',     # JavaScript
}

for filepath, content in files.items():
    file = project_root / filepath
    file.parent.mkdir(parents=True, exist_ok=True)
    file.touch()  # 创建空文件
    print(f"创建文件: {filepath}")

print("\n完成！请在对应文件中粘贴代码内容")