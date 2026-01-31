# 系统API文档

## 基本信息
- 系统名称：音乐驱动舞蹈辅助排演系统
- 开发者：齐雨晴
- 端口：5000

## 可用接口

### 1. 健康检查
GET /health
返回系统状态

### 2. 音乐上传分析
POST /api/upload_music
参数：music_file (文件)
返回：音乐分析结果

### 3. 舞蹈生成
POST /api/generate_dance
参数：music_file, dance_style
返回：舞蹈视频URL

### 4. 系统信息
GET /api/system_info
返回：系统配置、版本信息

### 5. 文件下载
GET /api/download/文件名
下载生成的视频文件

### 6. 结果列表
GET /api/get_outputs
获取所有生成结果
