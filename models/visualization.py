
# -*- coding: utf-8 -*-
"""舞蹈可视化模块"""

import numpy as np
import cv2
from moviepy.editor import VideoClip, AudioFileClip, CompositeVideoClip
from moviepy.video.io.ffmpeg_writer import FFMPEG_VideoWriter
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from pathlib import Path
from config import DANCE_STYLES


class DanceVisualizer:
    def __init__(self, frame_rate=30, width=800, height=600):
        self.frame_rate = frame_rate
        self.width = width
        self.height = height

        # 定义关节连接关系
        self.bone_connections = [
            (0, 1),  # 根节点 -> 髋部
            (1, 2),  # 髋部 -> 胸部
            (2, 3),  # 胸部 -> 颈部
            (3, 4),  # 颈部 -> 头部

            (2, 5),  # 胸部 -> 左肩
            (5, 6),  # 左肩 -> 左肘
            (6, 7),  # 左肘 -> 左腕

            (2, 8),  # 胸部 -> 右肩
            (8, 9),  # 右肩 -> 右肘
            (9, 10),  # 右肘 -> 右腕

            (1, 11),  # 髋部 -> 左髋
            (11, 12),  # 左髋 -> 左膝
            (12, 13),  # 左膝 -> 左踝

            (1, 14),  # 髋部 -> 右髋
            (14, 15),  # 右髋 -> 右膝
            (15, 16),  # 右膝 -> 右踝
        ]

        # 关节颜色
        self.joint_colors = [
            (255, 0, 0),  # 红色 - 根节点
            (255, 128, 0),  # 橙色 - 髋部
            (255, 255, 0),  # 黄色 - 胸部
            (0, 255, 0),  # 绿色 - 颈部
            (0, 255, 255),  # 青色 - 头部

            (0, 128, 255),  # 浅蓝 - 左肩
            (0, 0, 255),  # 蓝色 - 左肘
            (128, 0, 255),  # 紫色 - 左腕

            (255, 0, 255),  # 粉色 - 右肩
            (255, 0, 128),  # 玫瑰色 - 右肘
            (128, 128, 128),  # 灰色 - 右腕

            (0, 255, 128),  # 春绿色 - 左髋
            (128, 255, 0),  # 黄绿色 - 左膝
            (255, 128, 128),  # 浅红 - 左踝

            (128, 0, 128),  # 深紫 - 右髋
            (0, 128, 128),  # 橄榄色 - 右膝
            (128, 128, 0),  # 土黄色 - 右踝
        ]

    def create_skeleton_video(self, dance_sequence, music_path, output_path, dance_style):
        """创建骨骼动画视频"""
        # 创建视频写入器
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video_writer = cv2.VideoWriter(
            output_path,
            fourcc,
            self.frame_rate,
            (self.width, self.height)
        )

        try:
            # 创建每一帧
            for frame_idx in range(len(dance_sequence)):
                frame = self._create_frame(
                    dance_sequence[frame_idx],
                    frame_idx,
                    len(dance_sequence),
                    dance_style
                )
                video_writer.write(frame)

            video_writer.release()

            # 添加音频
            self._add_audio_to_video(output_path, music_path)

            return output_path

        except Exception as e:
            print(f"创建视频失败: {str(e)}")
            if video_writer.isOpened():
                video_writer.release()
            raise

    def _create_frame(self, skeleton_pose, frame_idx, total_frames, dance_style):
        """创建单帧图像"""
        # 创建空白画布
        frame = np.ones((self.height, self.width, 3), dtype=np.uint8) * 255

        # 添加背景渐变
        self._add_background_gradient(frame)

        # 添加标题和信息
        self._add_overlay_text(frame, dance_style, frame_idx, total_frames)

        # 计算缩放和偏移，使骨骼适应画布
        scale, offset_x, offset_y = self._calculate_transform(skeleton_pose)

        # 绘制骨骼
        frame = self._draw_skeleton(frame, skeleton_pose, scale, offset_x, offset_y)

        return frame

    def _add_background_gradient(self, frame):
        """添加背景渐变"""
        height, width = frame.shape[:2]

        # 创建渐变
        for y in range(height):
            # 从上到下的渐变
            gradient_value = int(255 - y / height * 100)
            frame[y, :] = (gradient_value, gradient_value, 255)

    def _add_overlay_text(self, frame, dance_style, frame_idx, total_frames):
        """添加覆盖文本"""

        # 修改后：
        # 添加映射
        style_name_map = {
            "赛乃姆": "Sainaimu",
            "萨玛舞": "Samawu",
            "刀郎舞": "Daolangwu"
        }
        english_style = style_name_map.get(dance_style, dance_style)
        title = f"Dance - {english_style}"


        # 舞蹈风格英文描述
        style_desc_map = {
            "赛乃姆": "Uyghur traditional dance",
            "萨玛舞": "Solemn religious dance",
            "刀郎舞": "Lively folk dance"
        }
        subtitle = style_desc_map.get(dance_style, "")

        # 进度信息
        progress = (frame_idx + 1) / total_frames
        time_str = f"{frame_idx // self.frame_rate:02d}:{frame_idx % self.frame_rate:02d}"

        # 绘制标题
        cv2.putText(frame, title, (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 0), 2, cv2.LINE_AA)

        # 绘制副标题
        cv2.putText(frame, subtitle, (20, 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (100, 100, 100), 1, cv2.LINE_AA)

        # 绘制进度条
        bar_width = 400
        bar_height = 20
        bar_x = (self.width - bar_width) // 2
        bar_y = self.height - 60

        # 进度条背景
        cv2.rectangle(frame, (bar_x, bar_y),
                      (bar_x + bar_width, bar_y + bar_height),
                      (200, 200, 200), -1)

        # 进度条前景
        progress_width = int(bar_width * progress)
        cv2.rectangle(frame, (bar_x, bar_y),
                      (bar_x + progress_width, bar_y + bar_height),
                      (0, 128, 255), -1)

        # 进度文本
        total_time_str = f"{total_frames // self.frame_rate:02d}:{total_frames % self.frame_rate:02d}"
        progress_text = f"{time_str} / {total_time_str}"
        cv2.putText(frame, progress_text, (bar_x + bar_width + 10, bar_y + bar_height // 2 + 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1, cv2.LINE_AA)

        # 帧编号
        frame_text = f"Frame: {frame_idx}/{total_frames}"
        cv2.putText(frame, frame_text, (self.width - 150, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 100, 100), 1, cv2.LINE_AA)
    def _calculate_transform(self, skeleton_pose):
        """计算骨骼变换参数"""
        # 获取所有关节的坐标
        all_points = []
        for joint in skeleton_pose:
            all_points.extend([joint[0], joint[1]])  # X和Y坐标

        # 计算边界
        min_val = min(all_points)
        max_val = max(all_points)

        # 计算缩放比例
        range_val = max_val - min_val
        if range_val == 0:
            range_val = 1

        # 计算缩放和偏移
        scale = min(self.width, self.height) * 0.7 / range_val
        offset_x = self.width // 2
        offset_y = self.height // 2 + 50  # 稍微向下偏移

        return scale, offset_x, offset_y

    def _draw_skeleton(self, frame, skeleton_pose, scale, offset_x, offset_y):
        """绘制骨骼"""
        # 首先绘制骨骼连接
        for connection in self.bone_connections:
            joint1_idx, joint2_idx = connection

            # 获取关节位置
            joint1 = skeleton_pose[joint1_idx]
            joint2 = skeleton_pose[joint2_idx]

            # 转换到图像坐标
            x1 = int(joint1[0] * scale + offset_x)
            y1 = int(-joint1[1] * scale + offset_y)  # Y轴需要反转
            x2 = int(joint2[0] * scale + offset_x)
            y2 = int(-joint2[1] * scale + offset_y)

            # 绘制骨骼（线条）
            if 0 <= x1 < self.width and 0 <= y1 < self.height and \
                    0 <= x2 < self.width and 0 <= y2 < self.height:
                # 使用渐变色
                color = self._get_bone_color(connection)
                cv2.line(frame, (x1, y1), (x2, y2), color, 3, cv2.LINE_AA)

        # 然后绘制关节
        for i, joint in enumerate(skeleton_pose):
            x = int(joint[0] * scale + offset_x)
            y = int(-joint[1] * scale + offset_y)  # Y轴需要反转

            if 0 <= x < self.width and 0 <= y < self.height:
                # 绘制关节点
                color = self.joint_colors[i % len(self.joint_colors)]
                cv2.circle(frame, (x, y), 8, color, -1, cv2.LINE_AA)

                # 关节编号
                cv2.putText(frame, str(i), (x + 10, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1, cv2.LINE_AA)

        return frame

    def _get_bone_color(self, connection):
        """获取骨骼颜色"""
        # 根据连接类型返回不同颜色
        joint1, joint2 = connection

        # 脊柱
        if joint1 <= 4 and joint2 <= 4:
            return (0, 128, 255)  # 橙色

        # 手臂
        elif 5 <= joint1 <= 10 and 5 <= joint2 <= 10:
            if joint1 <= 7:  # 左臂
                return (255, 0, 0)  # 蓝色
            else:  # 右臂
                return (0, 0, 255)  # 红色

        # 腿
        else:
            if joint1 <= 13:  # 左腿
                return (0, 255, 0)  # 绿色
            else:  # 右腿
                return (255, 0, 255)  # 紫色

    def _add_audio_to_video(self, video_path, audio_path):
        """添加音频到视频"""
        try:
            from moviepy.editor import VideoFileClip, AudioFileClip

            # 加载视频和音频
            video = VideoFileClip(video_path)
            audio = AudioFileClip(audio_path)

            # 截取音频与视频等长
            if audio.duration > video.duration:
                audio = audio.subclip(0, video.duration)

            # 合并音频视频
            final_video = video.set_audio(audio)

            # 输出临时文件
            temp_path = video_path.replace('.mp4', '_temp.mp4')
            final_video.write_videofile(
                temp_path,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True
            )

            # 替换原文件
            import shutil
            shutil.move(temp_path, video_path)

            # 关闭剪辑
            video.close()
            audio.close()

        except Exception as e:
            print(f"添加音频失败: {str(e)}")
            # 即使音频添加失败，也返回视频文件

    def create_dance_analysis_image(self, dance_sequence, output_path):
        """创建舞蹈分析图像"""
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))

        # 提取关节轨迹
        joints_to_plot = [0, 4, 7, 10, 13, 16]  # 根节点、头、双手、双脚
        joint_names = ['Root', 'Head', 'Left Hand', 'Right Hand', 'Left Foot', 'Right Foot']

        # 1. X坐标轨迹
        for i, joint_idx in enumerate(joints_to_plot):
            x_trajectory = dance_sequence[:, joint_idx, 0]
            axes[0, 0].plot(x_trajectory, label=joint_names[i])

        axes[0, 0].set_title('X Coordinate Trajectory')
        axes[0, 0].set_xlabel('Frame')
        axes[0, 0].set_ylabel('X Position')
        axes[0, 0].legend(loc='best')
        axes[0, 0].grid(True, alpha=0.3)

        # 2. Y坐标轨迹
        for i, joint_idx in enumerate(joints_to_plot):
            y_trajectory = dance_sequence[:, joint_idx, 1]
            axes[0, 1].plot(y_trajectory, label=joint_names[i])

        axes[0, 1].set_title('Y Coordinate Trajectory')
        axes[0, 1].set_xlabel('Frame')
        axes[0, 1].set_ylabel('Y Position')
        axes[0, 1].legend(loc='best')
        axes[0, 1].grid(True, alpha=0.3)

        # 3. 速度分析
        for i, joint_idx in enumerate(joints_to_plot[:3]):  # 只显示前3个
            velocity = np.diff(dance_sequence[:, joint_idx, :2], axis=0)
            speed = np.sqrt(velocity[:, 0] ** 2 + velocity[:, 1] ** 2)
            axes[1, 0].plot(speed, label=joint_names[i])

        axes[1, 0].set_title('Joint Speed Analysis')
        axes[1, 0].set_xlabel('Frame')
        axes[1, 0].set_ylabel('Speed')
        axes[1, 0].legend(loc='best')
        axes[1, 0].grid(True, alpha=0.3)

        # 4. 动作幅度直方图
        movement_ranges = []
        for joint_idx in joints_to_plot:
            x_range = np.max(dance_sequence[:, joint_idx, 0]) - np.min(dance_sequence[:, joint_idx, 0])
            y_range = np.max(dance_sequence[:, joint_idx, 1]) - np.min(dance_sequence[:, joint_idx, 1])
            movement_ranges.append(np.sqrt(x_range ** 2 + y_range ** 2))

        axes[1, 1].bar(range(len(joints_to_plot)), movement_ranges)
        axes[1, 1].set_title('Movement Range by Joint')
        axes[1, 1].set_xlabel('Joint')
        axes[1, 1].set_ylabel('Movement Range')
        axes[1, 1].set_xticks(range(len(joints_to_plot)))
        axes[1, 1].set_xticklabels(joint_names, rotation=45)
        axes[1, 1].grid(True, alpha=0.3, axis='y')

        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()

        return output_path