// 全局变量
let selectedMusic = null;
let selectedStyle = null;
let currentVideoUrl = null;

// DOM加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    initDragAndDrop();
    loadMusicList();
    loadResultsList();
    setupEventListeners();
});

// 初始化拖放功能
function initDragAndDrop() {
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('musicFileInput');

    // 点击上传区域触发文件选择
    uploadArea.addEventListener('click', function(e) {
        if (e.target !== fileInput) {
            fileInput.click();
        }
    });

    // 文件选择变化事件
    fileInput.addEventListener('change', function() {
        if (this.files.length > 0) {
            uploadMusicFile(this.files[0]);
        }
    });

    // 拖放事件
    uploadArea.addEventListener('dragover', function(e) {
        e.preventDefault();
        this.style.borderColor = '#667eea';
        this.style.backgroundColor = '#f1f5f9';
    });

    uploadArea.addEventListener('dragleave', function(e) {
        if (!this.contains(e.relatedTarget)) {
            this.style.borderColor = '#cbd5e0';
            this.style.backgroundColor = '#f8fafc';
        }
    });

    uploadArea.addEventListener('drop', function(e) {
        e.preventDefault();
        this.style.borderColor = '#cbd5e0';
        this.style.backgroundColor = '#f8fafc';

        if (e.dataTransfer.files.length > 0) {
            uploadMusicFile(e.dataTransfer.files[0]);
        }
    });
}

// 设置事件监听器
function setupEventListeners() {
    // 舞蹈风格选择
    document.querySelectorAll('.style-card').forEach(card => {
        card.addEventListener('click', function() {
            document.querySelectorAll('.style-card').forEach(c => {
                c.classList.remove('selected');
            });
            this.classList.add('selected');
            selectedStyle = this.dataset.style;
            console.log('选择舞蹈风格:', selectedStyle);
        });
    });

    // 关键词建议
    document.querySelectorAll('.suggestion-tag').forEach(tag => {
        tag.addEventListener('click', function() {
            const keywordInput = document.getElementById('keywordsInput');
            const currentValue = keywordInput.value;
            const newKeyword = this.dataset.keyword;

            if (currentValue) {
                keywordInput.value = currentValue + ', ' + newKeyword;
            } else {
                keywordInput.value = newKeyword;
            }
        });
    });

    // 生成按钮
    document.getElementById('generateBtn').addEventListener('click', generateDance);

    // 视频控制
    document.getElementById('playPauseBtn').addEventListener('click', toggleVideoPlayback);
    document.getElementById('downloadVideoBtn').addEventListener('click', downloadVideo);
    document.getElementById('restartBtn').addEventListener('click', restartGeneration);

    // 视频覆盖层
    const videoOverlay = document.getElementById('videoOverlay');
    if (videoOverlay) {
        videoOverlay.addEventListener('click', function() {
            const video = document.getElementById('previewVideo');
            video.play();
            this.style.opacity = '0';
            this.style.pointerEvents = 'none';
        });
    }

    // 音乐搜索
    const searchInput = document.getElementById('searchMusic');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            filterMusicList(this.value);
        });
    }
}

// 上传音乐文件
async function uploadMusicFile(file) {
    if (!validateMusicFile(file)) {
        showNotification('请选择有效的音乐文件 (MP3, WAV, FLAC, M4A, AAC)', 'error');
        return;
    }

    const formData = new FormData();
    formData.append('music_file', file);

    // 显示进度条
    const progressContainer = document.getElementById('uploadProgress');
    const progressBar = document.getElementById('progressBar');
    const progressText = document.getElementById('progressText');

    progressContainer.style.display = 'block';
    progressBar.style.width = '0%';
    progressText.textContent = '上传中...';

    try {
        const response = await fetch('/api/upload_music', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.success) {
            progressBar.style.width = '100%';
            progressText.textContent = '上传成功！';

            showNotification('音乐文件上传成功', 'success');
            loadMusicList();

            // 自动选择上传的音乐
            setTimeout(() => {
                selectMusicItem(data.filename);
                updateMusicInfo(data.music_info);
            }, 500);
        } else {
            progressText.textContent = '上传失败';
            showNotification(data.error || '上传失败', 'error');
        }
    } catch (error) {
        progressText.textContent = '网络错误';
        showNotification('网络错误，请检查连接', 'error');
    } finally {
        setTimeout(() => {
            progressContainer.style.display = 'none';
        }, 2000);
    }
}

// 验证音乐文件
function validateMusicFile(file) {
    const allowedExtensions = ['mp3', 'wav', 'flac', 'm4a', 'aac'];
    const extension = file.name.split('.').pop().toLowerCase();
    return allowedExtensions.includes(extension);
}

// 加载音乐列表
async function loadMusicList() {
    const musicList = document.getElementById('musicList');
    musicList.innerHTML = '<div class="loading"><div class="spinner"></div>加载中...</div>';

    try {
        const response = await fetch('/api/get_music_list');
        const musicFiles = await response.json();

        if (musicFiles.length === 0) {
            musicList.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-music-slash"></i>
                    <p>暂无音乐文件</p>
                    <p class="file-types">请上传音乐文件开始使用</p>
                </div>
            `;
            return;
        }

        let html = '';
        musicFiles.forEach(file => {
            html += `
                <div class="music-item" data-filename="${file.name}">
                    <div class="music-icon">
                        <i class="fas fa-file-audio"></i>
                    </div>
                    <div class="music-info">
                        <div class="music-name">${file.name}</div>
                        <div class="music-meta">
                            <span><i class="fas fa-hdd"></i> ${file.size}</span>
                            <span><i class="far fa-clock"></i> ${file.modified}</span>
                        </div>
                    </div>
                    <div class="music-action">
                        <i class="fas fa-check-circle"></i>
                    </div>
                </div>
            `;
        });

        musicList.innerHTML = html;

        // 添加点击事件
        document.querySelectorAll('.music-item').forEach(item => {
            item.addEventListener('click', function() {
                selectMusicItem(this.dataset.filename);
            });
        });

    } catch (error) {
        musicList.innerHTML = '<div class="loading">加载失败，请刷新重试</div>';
        showNotification('加载音乐列表失败', 'error');
    }
}

// 过滤音乐列表
function filterMusicList(searchTerm) {
    const items = document.querySelectorAll('.music-item');
    items.forEach(item => {
        const filename = item.dataset.filename.toLowerCase();
        if (filename.includes(searchTerm.toLowerCase())) {
            item.style.display = 'flex';
        } else {
            item.style.display = 'none';
        }
    });
}

// 选择音乐项
async function selectMusicItem(filename) {
    // 更新UI
    document.querySelectorAll('.music-item').forEach(item => {
        item.classList.remove('active');
        if (item.dataset.filename === filename) {
            item.classList.add('active');
        }
    });

    selectedMusic = filename;

    // 加载音乐信息
    try {
        const response = await fetch('/api/upload_music', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ filename: filename })
        });

        const data = await response.json();
        if (data.success) {
            updateMusicInfo(data.music_info);
        }
    } catch (error) {
        console.error('加载音乐信息失败:', error);
    }
}

// 更新音乐信息显示
function updateMusicInfo(musicInfo) {
    const infoSection = document.getElementById('musicInfoSection');
    infoSection.style.display = 'block';

    // 格式化时长
    const duration = musicInfo.duration || 0;
    const minutes = Math.floor(duration / 60);
    const seconds = Math.floor(duration % 60);
    const durationStr = `${minutes}:${seconds.toString().padStart(2, '0')}`;

    // 更新信息
    document.getElementById('infoFilename').textContent = selectedMusic;
    document.getElementById('infoDuration').textContent = durationStr;
    document.getElementById('infoTempo').textContent = musicInfo.tempo ? Math.round(musicInfo.tempo) : '--';
    document.getElementById('infoBeats').textContent = musicInfo.beat_count || '--';
}

// 生成舞蹈
async function generateDance() {
    // 验证输入
    if (!selectedMusic) {
        showNotification('请先选择音乐文件', 'error');
        return;
    }

    if (!selectedStyle) {
        showNotification('请选择舞蹈风格', 'error');
        return;
    }

    const keywords = document.getElementById('keywordsInput').value;
    const options = {
        smooth: document.getElementById('optionSmooth').checked,
        align: document.getElementById('optionAlign').checked,
        loop: document.getElementById('optionLoop').checked
    };

    // 显示进度界面
    const progressSection = document.getElementById('generationProgress');
    progressSection.style.display = 'block';

    // 重置进度
    document.querySelectorAll('.step').forEach((step, index) => {
        step.classList.remove('active');
        if (index === 0) step.classList.add('active');
    });

    const progressDetails = document.getElementById('progressDetails');
    progressDetails.innerHTML = `
        <div class="loading">
            <div class="spinner"></div>
            <p>开始生成舞蹈动作...</p>
        </div>
    `;

    // 更新第一步
    updateProgressStep(1, '正在分析音乐特征...');

    // 准备请求数据
    const requestData = {
        music_file: selectedMusic,
        dance_style: selectedStyle,
        keywords: keywords,
        options: options
    };

    try {
        const response = await fetch('/api/generate_dance', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestData)
        });

        const data = await response.json();

        if (data.success) {
            // 更新所有进度步骤
            updateProgressStep(2, '正在生成舞蹈序列...');
            setTimeout(() => {
                updateProgressStep(3, '正在创建可视化视频...');
                setTimeout(() => {
                    updateProgressStep(4, '生成完成！');

                    // 显示结果
                    currentVideoUrl = data.video_url;
                    showPreviewVideo(data.video_url);
                    updateAnalysisData(data.report);

                    showNotification('舞蹈生成成功！', 'success');

                    // 重新加载结果列表
                    loadResultsList();

                }, 1000);
            }, 1000);
        } else {
            progressDetails.innerHTML = `<p class="error">生成失败: ${data.error}</p>`;
            showNotification(`生成失败: ${data.error}`, 'error');
        }

    } catch (error) {
        progressDetails.innerHTML = `<p class="error">网络错误: ${error.message}</p>`;
        showNotification('网络错误，请检查连接', 'error');
    }
}

// 更新进度步骤
function updateProgressStep(stepNumber, message) {
    // 更新步骤状态
    document.querySelectorAll('.step').forEach((step, index) => {
        if (index < stepNumber) {
            step.classList.add('active');
        } else {
            step.classList.remove('active');
        }
    });

    // 更新进度详情
    const progressDetails = document.getElementById('progressDetails');
    if (stepNumber < 4) {
        progressDetails.innerHTML = `
            <div class="loading">
                <div class="spinner"></div>
                <p>${message}</p>
            </div>
        `;
    } else {
        progressDetails.innerHTML = `
            <div class="success-message">
                <i class="fas fa-check-circle"></i>
                <p>${message}</p>
                <p>视频已生成，可以预览和下载</p>
            </div>
        `;
    }
}

// 显示预览视频
function showPreviewVideo(videoUrl) {
    const previewSection = document.getElementById('previewSection');
    const videoElement = document.getElementById('previewVideo');
    const videoSource = document.getElementById('videoSource');
    const videoOverlay = document.getElementById('videoOverlay');

    previewSection.style.display = 'block';
    videoSource.src = videoUrl;
    videoElement.load();

    // 重置覆盖层
    videoOverlay.style.opacity = '1';
    videoOverlay.style.pointerEvents = 'auto';

    // 滚动到预览区域
    previewSection.scrollIntoView({ behavior: 'smooth' });
}

// 切换视频播放/暂停
function toggleVideoPlayback() {
    const video = document.getElementById('previewVideo');
    const button = document.getElementById('playPauseBtn');
    const videoOverlay = document.getElementById('videoOverlay');

    if (video.paused) {
        video.play();
        button.innerHTML = '<i class="fas fa-pause"></i> 暂停';
        videoOverlay.style.opacity = '0';
        videoOverlay.style.pointerEvents = 'none';
    } else {
        video.pause();
        button.innerHTML = '<i class="fas fa-play"></i> 播放';
    }
}

// 下载视频
function downloadVideo() {
    if (currentVideoUrl) {
        const link = document.createElement('a');
        link.href = currentVideoUrl;
        link.download = `dance_${Date.now()}.mp4`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);

        showNotification('开始下载视频', 'info');
    }
}

// 重新生成
function restartGeneration() {
    document.getElementById('generationProgress').style.display = 'none';
    document.querySelectorAll('.step').forEach(step => step.classList.remove('active'));
    document.querySelector('.step:first-child').classList.add('active');
}

// 更新分析数据
function updateAnalysisData(report) {
    const analysisSection = document.getElementById('analysisSection');
    analysisSection.style.display = 'block';

    // 模拟分析数据（实际应从报告数据中提取）
    const danceInfo = report.dance_info || {};
    const musicFeatures = report.music_features || {};

    document.getElementById('analysisRange').textContent =
        danceInfo.frame_count ? `${danceInfo.frame_count} 帧` : '--';

    document.getElementById('analysisSpeed').textContent =
        musicFeatures.tempo ? `${Math.round(musicFeatures.tempo)} BPM` : '--';

    document.getElementById('analysisRhythm').textContent =
        musicFeatures.beat_count ? `${musicFeatures.beat_count} 拍` : '--';
}

// 加载结果列表
async function loadResultsList() {
    const resultsList = document.getElementById('resultsList');

    try {
        const response = await fetch('/api/get_outputs');
        const outputs = await response.json();

        if (outputs.length === 0) {
            return; // 保持空状态
        }

        let html = '';
        outputs.forEach(output => {
            const date = new Date(output.created);
            const dateStr = date.toLocaleDateString();
            const timeStr = date.toLocaleTimeString();

            html += `
                <div class="result-item" data-url="${output.url}">
                    <div class="result-icon">
                        <i class="fas fa-video"></i>
                    </div>
                    <div class="result-info">
                        <div class="result-name">${output.name}</div>
                        <div class="result-meta">
                            <span><i class="fas fa-hdd"></i> ${output.size}</span>
                            <span><i class="far fa-calendar"></i> ${dateStr} ${timeStr}</span>
                        </div>
                    </div>
                    <div class="result-action">
                        <i class="fas fa-download"></i>
                    </div>
                </div>
            `;
        });

        resultsList.innerHTML = html;

        // 添加点击事件
        document.querySelectorAll('.result-item').forEach(item => {
            item.addEventListener('click', function(e) {
                if (!e.target.classList.contains('fa-download')) {
                    showPreviewVideo(this.dataset.url);
                }
            });

            // 下载按钮
            const downloadBtn = item.querySelector('.fa-download');
            if (downloadBtn) {
                downloadBtn.addEventListener('click', function(e) {
                    e.stopPropagation();
                    const url = item.dataset.url;
                    const link = document.createElement('a');
                    link.href = url;
                    link.download = '';
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                });
            }
        });

    } catch (error) {
        console.error('加载结果列表失败:', error);
    }
}

// 显示通知
function showNotification(message, type = 'info') {
    const container = document.getElementById('notificationContainer');

    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
        ${message}
    `;

    container.appendChild(notification);

    // 3秒后自动移除
    setTimeout(() => {
        notification.style.animation = 'slideIn 0.3s ease reverse';
        setTimeout(() => {
            container.removeChild(notification);
        }, 300);
    }, 3000);
}