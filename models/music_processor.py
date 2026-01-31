import librosa
import librosa.display
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
import soundfile as sf
import json
from pathlib import Path
import tempfile


class MusicProcessor:
    def __init__(self, sample_rate=22050, n_fft=2048, hop_length=512, n_mels=128):
        self.sample_rate = sample_rate
        self.n_fft = n_fft
        self.hop_length = hop_length
        self.n_mels = n_mels

    def load_music(self, filepath):
        """加载音乐文件"""
        try:
            y, sr = librosa.load(filepath, sr=self.sample_rate)
            return y, sr
        except Exception as e:
            raise Exception(f"无法加载音乐文件: {str(e)}")

    def analyze_music(self, filepath):
        """分析音乐文件"""
        try:
            y, sr = self.load_music(filepath)
            duration = librosa.get_duration(y=y, sr=sr)

            # 提取节奏特征
            tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
            beats = librosa.frames_to_time(beat_frames, sr=sr)

            # 提取频谱特征
            mel_spec = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=self.n_mels)
            mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)

            # 提取色度特征
            chroma = librosa.feature.chroma_stft(y=y, sr=sr)

            # 提取MFCC特征
            mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)

            # 估计拍号
            onset_env = librosa.onset.onset_strength(y=y, sr=sr)
            pulse = librosa.beat.plp(onset_envelope=onset_env, sr=sr)

            return {
                'duration': duration,
                'tempo': float(tempo),
                'beat_count': len(beats),
                'beats': beats.tolist()[:20],  # 只返回前20个拍子
                'sample_rate': sr,
                'shape': {
                    'mel_spec': mel_spec.shape,
                    'chroma': chroma.shape,
                    'mfcc': mfcc.shape
                }
            }
        except Exception as e:
            raise Exception(f"音乐分析失败: {str(e)}")

    def extract_features(self, filepath):
        """提取音乐特征用于舞蹈生成"""
        y, sr = self.load_music(filepath)

        # 基本特征
        duration = librosa.get_duration(y=y, sr=sr)
        tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)

        # 能量特征
        rms = librosa.feature.rms(y=y)[0]
        energy_mean = np.mean(rms)
        energy_std = np.std(rms)

        # 频谱特征
        spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
        spectral_bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)[0]

        # 零交叉率
        zcr = librosa.feature.zero_crossing_rate(y)[0]

        # 节奏密度
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        onset_frames = librosa.onset.onset_detect(onset_envelope=onset_env, sr=sr)
        rhythm_density = len(onset_frames) / duration

        return {
            'tempo': float(tempo),
            'duration': float(duration),
            'energy_mean': float(energy_mean),
            'energy_std': float(energy_std),
            'spectral_centroid_mean': float(np.mean(spectral_centroid)),
            'spectral_bandwidth_mean': float(np.mean(spectral_bandwidth)),
            'zcr_mean': float(np.mean(zcr)),
            'rhythm_density': float(rhythm_density),
            'beats': librosa.frames_to_time(beat_frames, sr=sr).tolist()
        }

    def visualize_music(self, filepath, output_dir):
        """生成音乐可视化图表"""
        y, sr = self.load_music(filepath)

        fig, axes = plt.subplots(3, 1, figsize=(12, 10))

        # 波形图
        time = np.linspace(0, len(y) / sr, len(y))
        axes[0].plot(time, y)
        axes[0].set_title('Waveform')
        axes[0].set_xlabel('Time (s)')
        axes[0].set_ylabel('Amplitude')

        # 频谱图
        mel_spec = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=self.n_mels)
        mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)
        img = librosa.display.specshow(mel_spec_db, sr=sr, hop_length=self.hop_length,
                                       x_axis='time', y_axis='mel', ax=axes[1])
        axes[1].set_title('Mel Spectrogram')
        fig.colorbar(img, ax=axes[1], format='%+2.0f dB')

        # 色度图
        chroma = librosa.feature.chroma_stft(y=y, sr=sr)
        librosa.display.specshow(chroma, sr=sr, hop_length=self.hop_length,
                                 x_axis='time', y_axis='chroma', ax=axes[2])
        axes[2].set_title('Chroma Features')

        plt.tight_layout()

        # 保存图像
        output_path = Path(output_dir) / f"music_analysis_{Path(filepath).stem}.png"
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()

        return str(output_path)