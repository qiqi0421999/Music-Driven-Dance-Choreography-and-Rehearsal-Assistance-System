from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import os
import uuid
from datetime import datetime
import json

from config import MUSIC_DIR, OUTPUT_DIR, ALLOWED_EXTENSIONS, DANCE_STYLES
from models.music_processor import MusicProcessor
from models.dance_generator import DanceGenerator
from models.visualization import DanceVisualizer
from utils.file_utils import allowed_file, save_uploaded_file

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB限制

# 初始化处理器
music_processor = MusicProcessor()
dance_generator = DanceGenerator()
dance_visualizer = DanceVisualizer()


@app.route('/')
def index():
    """主页面"""
    return render_template('index.html', dance_styles=DANCE_STYLES)


@app.route('/api/upload_music', methods=['POST'])
def upload_music():
    """上传音乐文件"""
    if 'music_file' not in request.files:
        return jsonify({'error': '没有选择文件'}), 400

    file = request.files['music_file']
    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400

    if not allowed_file(file.filename, ALLOWED_EXTENSIONS):
        return jsonify({'error': '不支持的文件格式'}), 400

    # 保存文件
    filename = save_uploaded_file(file, MUSIC_DIR)

    # 分析音乐
    try:
        music_info = music_processor.analyze_music(str(MUSIC_DIR / filename))
        return jsonify({
            'success': True,
            'filename': filename,
            'music_info': music_info
        })
    except Exception as e:
        return jsonify({'error': f'音乐分析失败: {str(e)}'}), 500


@app.route('/api/get_music_list')
def get_music_list():
    """获取音乐列表"""
    music_files = []
    for file in MUSIC_DIR.iterdir():
        if file.suffix.lower()[1:] in ALLOWED_EXTENSIONS:
            music_files.append({
                'name': file.name,
                'size': f"{file.stat().st_size / 1024 / 1024:.1f} MB",
                'modified': datetime.fromtimestamp(file.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')
            })
    return jsonify(music_files)


@app.route('/api/generate_dance', methods=['POST'])
def generate_dance():
    """生成舞蹈动作"""
    data = request.json

    # 验证输入
    if not data.get('music_file'):
        return jsonify({'error': '请选择音乐文件'}), 400

    if not data.get('dance_style'):
        return jsonify({'error': '请选择舞蹈风格'}), 400

    # 获取输入参数
    music_path = str(MUSIC_DIR / data['music_file'])
    dance_style = data['dance_style']
    additional_keywords = data.get('keywords', '')

    try:
        # 步骤1: 分析音乐
        print("分析音乐中...")
        music_features = music_processor.extract_features(music_path)

        # 步骤2: 生成舞蹈序列
        print("生成舞蹈序列中...")
        dance_sequence = dance_generator.generate(
            music_features=music_features,
            dance_style=dance_style,
            keywords=additional_keywords
        )

        # 步骤3: 生成视频
        print("生成视频中...")
        output_filename = f"dance_{uuid.uuid4().hex[:8]}.mp4"
        output_path = str(OUTPUT_DIR / output_filename)

        # 创建骨骼动画视频
        video_path = dance_visualizer.create_skeleton_video(
            dance_sequence=dance_sequence,
            music_path=music_path,
            output_path=output_path,
            dance_style=dance_style
        )

        # 步骤4: 生成分析报告
        report = {
            'generation_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'music_file': data['music_file'],
            'dance_style': dance_style,
            'music_features': {
                'tempo': music_features.get('tempo', 0),
                'duration': music_features.get('duration', 0),
                'beat_count': len(music_features.get('beats', []))
            },
            'dance_info': {
                'frame_count': len(dance_sequence),
                'joint_count': dance_sequence.shape[1] if len(dance_sequence.shape) > 1 else 0
            },
            'output_files': {
                'video': output_filename
            }
        }

        # 保存报告
        report_filename = f"report_{uuid.uuid4().hex[:8]}.json"
        report_path = str(OUTPUT_DIR / report_filename)
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        return jsonify({
            'success': True,
            'video_url': f'/api/download/{output_filename}',
            'report': report
        })

    except Exception as e:
        print(f"生成失败: {str(e)}")
        return jsonify({'error': f'生成失败: {str(e)}'}), 500


@app.route('/api/download/<filename>')
def download_file(filename):
    """下载生成的文件"""
    file_path = OUTPUT_DIR / filename
    if not file_path.exists():
        return jsonify({'error': '文件不存在'}), 404

    return send_file(file_path, as_attachment=True)


@app.route('/api/get_outputs')
def get_outputs():
    """获取生成结果列表"""
    outputs = []
    for file in OUTPUT_DIR.iterdir():
        if file.suffix.lower() in ['.mp4', '.avi', '.mov']:
            outputs.append({
                'name': file.name,
                'size': f"{file.stat().st_size / 1024 / 1024:.1f} MB",
                'created': datetime.fromtimestamp(file.stat().st_ctime).strftime('%Y-%m-%d %H:%M:%S'),
                'url': f'/api/download/{file.name}'
            })
    return jsonify(outputs)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)