#!/usr/bin/env python3
"""
音乐驱动舞蹈辅助排演系统 - 启动脚本
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app import app


def check_dependencies():
    """检查必要的依赖和目录"""
    print("检查系统依赖...")

    # 检查必要目录
    required_dirs = [
        project_root / "static",
        project_root / "static/css",
        project_root / "static/js",
        project_root / "templates",
        project_root / "data",
        project_root / "data/music",
        project_root / "data/outputs",
        project_root / "models",
        project_root / "utils"
    ]

    for dir_path in required_dirs:
        if not dir_path.exists():
            print(f"创建目录: {dir_path}")
            dir_path.mkdir(parents=True, exist_ok=True)

    # 检查配置文件
    config_file = project_root / "config.py"
    if not config_file.exists():
        print("错误: config.py 配置文件不存在!")
        print("请从 config.py.example 创建配置文件")
        sys.exit(1)

    print("✓ 系统依赖检查完成")


def print_banner():
    """打印启动横幅"""
    banner = """
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║    音乐驱动舞蹈辅助排演系统                                        ║
║    Music-Driven Dance Rehearsal Assistant System                  ║
║                                                                   ║
║    Version: 1.0.0                                                 ║
║    Focus: 新疆舞蹈数字化与创作辅助                                 ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
    """
    print(banner)


def main():
    """主函数"""
    print_banner()
    check_dependencies()

    print("\n启动信息:")
    print(f"• 项目根目录: {project_root}")
    print(f"• Web界面: http://127.0.0.1:5000")
    print(f"• 音乐文件目录: {project_root}/data/music")
    print(f"• 输出文件目录: {project_root}/data/outputs")

    print("\n启动服务器...")
    print("按 Ctrl+C 停止服务器\n")

    # 启动Flask应用
    try:
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True,
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n服务器已停止")
        sys.exit(0)
    except Exception as e:
        print(f"\n启动服务器时出错: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()