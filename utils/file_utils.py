import os
from werkzeug.utils import secure_filename
from pathlib import Path
from datetime import datetime
import uuid


def allowed_file(filename, allowed_extensions):
    """检查文件扩展名是否允许"""
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in allowed_extensions


def save_uploaded_file(file, upload_folder):
    """保存上传的文件"""
    # 生成安全的文件名
    original_filename = secure_filename(file.filename)
    filename_base, filename_ext = os.path.splitext(original_filename)

    # 添加时间戳和随机字符串防止重名
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    random_str = uuid.uuid4().hex[:6]
    new_filename = f"{filename_base}_{timestamp}_{random_str}{filename_ext}"

    # 保存文件
    file_path = Path(upload_folder) / new_filename
    file.save(file_path)

    return new_filename


def clean_old_files(directory, max_age_hours=24):
    """清理旧文件"""
    directory = Path(directory)
    current_time = datetime.now()

    for file_path in directory.iterdir():
        if file_path.is_file():
            file_age = current_time - datetime.fromtimestamp(file_path.stat().st_mtime)
            if file_age.total_seconds() > max_age_hours * 3600:
                try:
                    file_path.unlink()
                    print(f"已删除旧文件: {file_path}")
                except Exception as e:
                    print(f"删除文件失败 {file_path}: {str(e)}")