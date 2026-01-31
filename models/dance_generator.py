import numpy as np
import random
from scipy.interpolate import interp1d
import json
from pathlib import Path
from config import DANCE_STYLES, DANCE_CONFIG


class DanceGenerator:
    def __init__(self):
        self.frame_rate = DANCE_CONFIG['frame_rate']
        self.joint_count = DANCE_CONFIG['joint_count']

        # 定义关节层级关系
        self.joint_hierarchy = {
            'root': 0,
            'hip': 0,
            'spine': 1,
            'chest': 2,
            'neck': 3,
            'head': 4,
            'left_shoulder': 5,
            'left_elbow': 6,
            'left_wrist': 7,
            'right_shoulder': 8,
            'right_elbow': 9,
            'right_wrist': 10,
            'left_hip': 11,
            'left_knee': 12,
            'left_ankle': 13,
            'right_hip': 14,
            'right_knee': 15,
            'right_ankle': 16
        }

        # 舞蹈动作库
        self.dance_moves = self._load_dance_moves()

    def _load_dance_moves(self):
        """加载预定义的舞蹈动作"""
        moves = {
            "赛乃姆": {
                "move_neck": self._create_neck_movement,
                "rotate_wrist": self._create_wrist_rotation,
                "step_sequence": self._create_step_sequence
            },
            "萨玛舞": {
                "slow_turn": self._create_slow_turn,
                "spread_arms": self._create_spread_arms,
                "bow_step": self._create_bow_step
            },
            "刀郎舞": {
                "squat_jump": self._create_squat_jump,
                "shake_shoulders": self._create_shoulder_shake,
                "animal_imitation": self._create_animal_imitation
            }
        }
        return moves

    def generate(self, music_features, dance_style, keywords=""):
        """生成舞蹈序列"""
        tempo = music_features.get('tempo', 100)
        duration = music_features.get('duration', 30)
        beats = music_features.get('beats', [])

        # 计算帧数
        total_frames = int(duration * self.frame_rate)

        # 初始化舞蹈序列
        dance_sequence = self._initialize_pose()

        # 根据舞蹈风格选择动作生成器
        if dance_style in self.dance_moves:
            style_moves = self.dance_moves[dance_style]
        else:
            style_moves = self.dance_moves["赛乃姆"]  # 默认

        # 生成动作序列
        generated_frames = self._generate_by_style(
            style_moves, tempo, beats, total_frames, dance_style
        )

        # 合并序列
        dance_sequence = np.vstack([dance_sequence, generated_frames])

        # 应用平滑
        dance_sequence = self._smooth_sequence(dance_sequence)

        # 确保序列长度正确
        if len(dance_sequence) > total_frames:
            dance_sequence = dance_sequence[:total_frames]
        elif len(dance_sequence) < total_frames:
            dance_sequence = np.pad(dance_sequence,
                                    ((0, total_frames - len(dance_sequence)), (0, 0), (0, 0)),
                                    mode='edge')

        return dance_sequence

    def _initialize_pose(self):
        """初始化T-pose"""
        # 简单的T-pose
        pose = np.zeros((1, self.joint_count, 3))

        # 设置关节位置
        # 身体中心
        pose[0, 0] = [0, 0, 0]  # 根节点

        # 脊柱
        pose[0, 1] = [0, 0.1, 0]  # 髋部
        pose[0, 2] = [0, 0.2, 0]  # 胸部
        pose[0, 3] = [0, 0.25, 0]  # 颈部
        pose[0, 4] = [0, 0.3, 0]  # 头部

        # 左臂
        pose[0, 5] = [-0.1, 0.2, 0]  # 左肩
        pose[0, 6] = [-0.2, 0.2, 0]  # 左肘
        pose[0, 7] = [-0.3, 0.2, 0]  # 左腕

        # 右臂
        pose[0, 8] = [0.1, 0.2, 0]  # 右肩
        pose[0, 9] = [0.2, 0.2, 0]  # 右肘
        pose[0, 10] = [0.3, 0.2, 0]  # 右腕

        # 左腿
        pose[0, 11] = [-0.05, 0.1, 0]  # 左髋
        pose[0, 12] = [-0.05, 0, 0]  # 左膝
        pose[0, 13] = [-0.05, -0.1, 0]  # 左踝

        # 右腿
        pose[0, 14] = [0.05, 0.1, 0]  # 右髋
        pose[0, 15] = [0.05, 0, 0]  # 右膝
        pose[0, 16] = [0.05, -0.1, 0]  # 右踝

        return pose

    def _generate_by_style(self, style_moves, tempo, beats, total_frames, dance_style):
        """根据风格生成动作序列"""
        frames_per_beat = int((60 / tempo) * self.frame_rate)

        # 根据舞蹈风格调整参数
        if dance_style == "赛乃姆":
            amplitude = 0.5
            speed = 0.8
        elif dance_style == "萨玛舞":
            amplitude = 0.3
            speed = 0.5
        elif dance_style == "刀郎舞":
            amplitude = 0.7
            speed = 1.2
        else:
            amplitude = 0.5
            speed = 1.0

        generated_frames = []

        # 生成基本动作
        for i in range(total_frames // 10):  # 每10帧一个动作单元
            # 根据节奏选择动作
            if i % frames_per_beat == 0:
                # 在重拍上做更大幅度的动作
                move_func = random.choice(list(style_moves.values()))
                move_frames = move_func(
                    duration=frames_per_beat * 2,
                    amplitude=amplitude * 1.5,
                    speed=speed
                )
            else:
                # 弱拍上的过渡动作
                move_func = random.choice(list(style_moves.values()))
                move_frames = move_func(
                    duration=frames_per_beat,
                    amplitude=amplitude * 0.7,
                    speed=speed * 0.8
                )

            generated_frames.extend(move_frames)

        return np.array(generated_frames)

    def _create_neck_movement(self, duration=30, amplitude=1.0, speed=1.0):
        """创建颈部移动动作"""
        frames = []
        base_pose = self._initialize_pose()[0]

        for i in range(duration):
            frame = base_pose.copy()

            # 颈部左右移动
            neck_offset = np.sin(i * 0.1 * speed) * 0.1 * amplitude
            frame[3, 0] += neck_offset  # 颈部X轴移动
            frame[4, 0] += neck_offset * 1.2  # 头部跟随移动

            # 轻微的上下移动
            head_nod = np.sin(i * 0.15 * speed) * 0.05 * amplitude
            frame[4, 1] += head_nod

            frames.append(frame)

        return frames

    def _create_wrist_rotation(self, duration=30, amplitude=1.0, speed=1.0):
        """创建手腕旋转动作"""
        frames = []
        base_pose = self._initialize_pose()[0]

        for i in range(duration):
            frame = base_pose.copy()

            # 手腕旋转
            wrist_angle = i * 0.2 * speed * amplitude

            # 左腕旋转
            frame[7, 0] = -0.3 + np.sin(wrist_angle) * 0.05
            frame[7, 1] = 0.2 + np.cos(wrist_angle) * 0.05

            # 右腕旋转
            frame[10, 0] = 0.3 + np.sin(wrist_angle) * 0.05
            frame[10, 1] = 0.2 + np.cos(wrist_angle) * 0.05

            frames.append(frame)

        return frames

    def _create_step_sequence(self, duration=30, amplitude=1.0, speed=1.0):
        """创建步法序列"""
        frames = []
        base_pose = self._initialize_pose()[0]

        for i in range(duration):
            frame = base_pose.copy()

            # 左右脚步移动
            step_offset = np.sin(i * 0.15 * speed) * 0.1 * amplitude

            # 左脚移动
            frame[13, 0] = -0.05 + step_offset * 0.5
            frame[13, 1] = -0.1 + abs(step_offset) * 0.2

            # 右脚移动
            frame[16, 0] = 0.05 - step_offset * 0.5
            frame[16, 1] = -0.1 + abs(step_offset) * 0.2

            # 髋部跟随
            frame[1, 0] = step_offset * 0.3

            frames.append(frame)

        return frames

    def _create_slow_turn(self, duration=60, amplitude=1.0, speed=0.5):
        """创建缓慢转身动作"""
        frames = []
        base_pose = self._initialize_pose()[0]

        for i in range(duration):
            frame = base_pose.copy()

            # 整体旋转
            rotation_angle = i * 0.05 * speed * amplitude

            # 旋转整个身体
            for j in range(len(frame)):
                x, y, z = frame[j]
                # 绕Y轴旋转
                new_x = x * np.cos(rotation_angle) - z * np.sin(rotation_angle)
                new_z = x * np.sin(rotation_angle) + z * np.cos(rotation_angle)
                frame[j] = [new_x, y, new_z]

            frames.append(frame)

        return frames

    def _create_spread_arms(self, duration=40, amplitude=1.0, speed=0.8):
        """创建展臂动作"""
        frames = []
        base_pose = self._initialize_pose()[0]

        for i in range(duration):
            frame = base_pose.copy()

            # 手臂展开程度
            spread = np.sin(i * 0.1 * speed) * 0.15 * amplitude

            # 左臂
            frame[5, 0] = -0.1 - spread
            frame[6, 0] = -0.2 - spread * 1.5
            frame[7, 0] = -0.3 - spread * 2

            # 右臂
            frame[8, 0] = 0.1 + spread
            frame[9, 0] = 0.2 + spread * 1.5
            frame[10, 0] = 0.3 + spread * 2

            # 手臂上下移动
            arm_lift = np.cos(i * 0.15 * speed) * 0.05 * amplitude
            for j in range(5, 11):
                frame[j, 1] += arm_lift

            frames.append(frame)

        return frames

    def _create_bow_step(self, duration=50, amplitude=1.0, speed=0.6):
        """创建鞠躬步动作"""
        frames = []
        base_pose = self._initialize_pose()[0]

        for i in range(duration):
            frame = base_pose.copy()

            # 鞠躬动作
            bow_depth = np.sin(i * 0.1 * speed) * 0.2 * amplitude

            # 上半身前倾
            for j in range(2, 5):  # 胸部、颈部、头部
                frame[j, 1] -= bow_depth * 0.5
                frame[j, 2] += bow_depth * 0.3

            # 膝盖弯曲
            knee_bend = abs(bow_depth) * 0.3
            frame[12, 1] = 0 - knee_bend  # 左膝
            frame[15, 1] = 0 - knee_bend  # 右膝

            frames.append(frame)

        return frames

    def _create_squat_jump(self, duration=30, amplitude=1.0, speed=1.2):
        """创建蹲跳动作"""
        frames = []
        base_pose = self._initialize_pose()[0]

        for i in range(duration):
            frame = base_pose.copy()

            # 跳跃周期
            jump_phase = (i % 15) / 15.0

            if jump_phase < 0.3:  # 下蹲
                squat_depth = jump_phase * 0.2 * amplitude
                # 降低身体
                for j in range(len(frame)):
                    frame[j, 1] -= squat_depth
                # 弯曲膝盖
                frame[12, 1] = 0 - squat_depth * 2
                frame[15, 1] = 0 - squat_depth * 2

            elif jump_phase < 0.6:  # 起跳
                jump_height = (jump_phase - 0.3) * 0.3 * amplitude
                # 抬起身体
                for j in range(len(frame)):
                    frame[j, 1] += jump_height

            else:  # 落地
                land_depth = (1 - jump_phase) * 0.1 * amplitude
                for j in range(len(frame)):
                    frame[j, 1] -= land_depth

            frames.append(frame)

        return frames

    def _create_shoulder_shake(self, duration=25, amplitude=1.0, speed=1.5):
        """创建肩膀抖动动作"""
        frames = []
        base_pose = self._initialize_pose()[0]

        for i in range(duration):
            frame = base_pose.copy()

            # 肩膀抖动
            shake_freq = i * 0.3 * speed

            # 左肩抖动
            frame[5, 1] = 0.2 + np.sin(shake_freq) * 0.05 * amplitude
            frame[5, 0] = -0.1 + np.cos(shake_freq) * 0.02 * amplitude

            # 右肩抖动
            frame[8, 1] = 0.2 + np.cos(shake_freq) * 0.05 * amplitude
            frame[8, 0] = 0.1 + np.sin(shake_freq) * 0.02 * amplitude

            # 头部跟随
            frame[4, 0] = 0.3 + np.sin(shake_freq * 0.5) * 0.03 * amplitude

            frames.append(frame)

        return frames

    def _create_animal_imitation(self, duration=40, amplitude=1.0, speed=1.0):
        """创建动物模仿动作"""
        frames = []
        base_pose = self._initialize_pose()[0]

        for i in range(duration):
            frame = base_pose.copy()

            # 鸭子步模仿
            duck_walk = i * 0.2 * speed

            # 左右摇摆
            sway = np.sin(duck_walk) * 0.15 * amplitude

            # 身体左右移动
            for j in range(len(frame)):
                frame[j, 0] += sway * (0.5 if j > 10 else 1.0)  # 下半身移动幅度小

            # 膝盖弯曲
            knee_bend = abs(np.sin(duck_walk)) * 0.1 * amplitude
            frame[12, 1] = 0 - knee_bend  # 左膝
            frame[15, 1] = 0 - knee_bend  # 右膝

            # 手臂摆动
            arm_swing = np.cos(duck_walk) * 0.1 * amplitude
            frame[7, 0] = -0.3 - arm_swing  # 左腕
            frame[10, 0] = 0.3 + arm_swing  # 右腕

            frames.append(frame)

        return frames

    def _smooth_sequence(self, sequence, window_size=5):
        """平滑动作序列"""
        if len(sequence) < window_size:
            return sequence

        smoothed = np.zeros_like(sequence)

        for i in range(len(sequence)):
            start = max(0, i - window_size // 2)
            end = min(len(sequence), i + window_size // 2 + 1)

            # 对每个关节的每个坐标进行平均
            for joint in range(sequence.shape[1]):
                for coord in range(3):
                    smoothed[i, joint, coord] = np.mean(
                        sequence[start:end, joint, coord]
                    )

        return smoothed