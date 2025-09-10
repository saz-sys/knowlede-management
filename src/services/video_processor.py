"""
VideoProcessor（動画処理）サービス

OpenCVを使用した動画ファイルの読み込み、フレーム抽出、
シーンチェンジ検出、品質評価を行うサービスクラスです。
"""

import cv2
import subprocess
import numpy as np
from pathlib import Path
from typing import Iterator, List, Optional
import logging
from datetime import datetime

from ..models.video_file import VideoFile, VideoFileStatus
from ..models.frame import Frame
from ..lib.errors import (
    VideoProcessingError,
    InvalidVideoFormatError,
    CorruptedVideoError,
    UnsupportedCodecError,
    InsufficientMemoryError,
    InvalidThresholdError,
    InvalidFrameDataError
)


class VideoProcessor:
    """動画処理サービスクラス"""
    
    def __init__(self):
        """VideoProcessorを初期化"""
        self.logger = logging.getLogger(__name__)
        self._current_video_capture: Optional[cv2.VideoCapture] = None
        self._frame_buffer: List[np.ndarray] = []
        self._max_buffer_size = 100  # 最大100フレームをバッファリング
    
    def load_video(self, file_path: Path) -> VideoFile:
        """
        動画ファイルを読み込んでVideoFileオブジェクトを作成
        
        Args:
            file_path: 動画ファイルのパス
            
        Returns:
            VideoFile: 動画ファイル情報
            
        Raises:
            FileNotFoundError: ファイルが存在しない
            InvalidVideoFormatError: MP4以外の形式
            CorruptedVideoError: 動画ファイルが破損
            UnsupportedCodecError: 対応していないコーデック
        """
        self.logger.info(f"動画ファイル読み込み開始: {file_path}")
        
        try:
            # VideoFileインスタンス作成（基本バリデーション含む）
            video_file = VideoFile(file_path=file_path)
            
            # OpenCVで動画情報を取得
            cap = cv2.VideoCapture(str(file_path))
            if not cap.isOpened():
                raise CorruptedVideoError(
                    f"動画ファイルを開けません: {file_path}",
                    details={'file_path': str(file_path)}
                )
            
            try:
                # 動画プロパティの取得
                fps = cap.get(cv2.CAP_PROP_FPS)
                frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                
                # 端末にffprobeがあれば回転メタデータを取得
                rotation = self._get_video_rotation(file_path)
                if rotation in (90, 270):
                    # 表示上は縦横が入れ替わるため論理サイズを交換
                    width, height = height, width
                
                # プロパティの妥当性チェック
                if fps <= 0 or frame_count <= 0 or width <= 0 or height <= 0:
                    raise CorruptedVideoError(
                        f"動画プロパティが無効です: fps={fps}, frames={frame_count}, size={width}x{height}",
                        details={
                            'fps': fps,
                            'frame_count': frame_count,
                            'width': width,
                            'height': height
                        }
                    )
                
                # 再生時間の計算
                duration = frame_count / fps
                
                # VideoFileオブジェクトの更新
                video_file.fps = fps
                video_file.width = width
                video_file.height = height
                video_file.total_frames = frame_count
                video_file.duration = duration
                if rotation is not None:
                    video_file.add_metadata('rotation', rotation)
                
                # コーデック情報の取得
                fourcc = cap.get(cv2.CAP_PROP_FOURCC)
                codec_name = "".join([chr((int(fourcc) >> 8 * i) & 0xFF) for i in range(4)])
                video_file.add_metadata('codec', codec_name)
                
                # 詳細バリデーション
                video_file.validate_video_properties()
                
                self.logger.info(f"動画読み込み成功: {duration:.2f}秒, {width}x{height}, {fps:.2f}fps")
                
                return video_file
                
            finally:
                cap.release()
                
        except FileNotFoundError:
            raise
        except (InvalidVideoFormatError, CorruptedVideoError):
            raise
        except Exception as e:
            self.logger.error(f"動画読み込みエラー: {e}")
            raise VideoProcessingError(
                f"動画ファイルの読み込み中にエラーが発生しました: {e}",
                details={'file_path': str(file_path), 'error': str(e)}
            )
    
    def extract_frames(self, video_file: VideoFile, interval_seconds: float = 1.0) -> Iterator[Frame]:
        """
        動画からフレームを抽出（ジェネレータとして返す）
        
        Args:
            video_file: 処理対象の動画ファイル
            interval_seconds: フレーム抽出間隔（秒）
            
        Yields:
            Frame: 抽出されたフレーム
            
        Raises:
            VideoProcessingError: フレーム抽出に失敗
            InsufficientMemoryError: メモリ不足
        """
        if interval_seconds <= 0:
            raise ValueError(f"フレーム間隔は正の値である必要があります: {interval_seconds}")
        
        self.logger.info(f"フレーム抽出開始: {video_file.file_name}, 間隔={interval_seconds}秒")
        
        cap = cv2.VideoCapture(str(video_file.file_path))
        if not cap.isOpened():
            raise VideoProcessingError(f"動画ファイルを開けません: {video_file.file_path}")
        
        try:
            video_file.start_processing()
            
            frame_interval = int(video_file.fps * interval_seconds)
            current_frame_number = 0
            extracted_count = 0
            
            while True:
                # フレーム位置を設定
                cap.set(cv2.CAP_PROP_POS_FRAMES, current_frame_number)
                
                ret, opencv_frame = cap.read()
                if not ret:
                    break
                
                # メモリ使用量チェック
                if len(self._frame_buffer) >= self._max_buffer_size:
                    self._frame_buffer.clear()  # バッファをクリア
                
                try:
                    # フレームオブジェクト作成
                    timestamp = current_frame_number / video_file.fps
                    frame = Frame.create_from_opencv(
                        video_file=video_file,
                        frame_number=current_frame_number,
                        timestamp=timestamp,
                        opencv_frame=opencv_frame
                    )
                    
                    # 品質メトリクス計算
                    frame.update_quality_metrics()
                    
                    self._frame_buffer.append(opencv_frame)
                    extracted_count += 1
                    
                    self.logger.debug(f"フレーム抽出: {current_frame_number} ({timestamp:.2f}秒)")
                    yield frame
                    
                except MemoryError:
                    raise InsufficientMemoryError(
                        "フレーム抽出中にメモリ不足が発生しました",
                        details={
                            'extracted_frames': extracted_count,
                            'current_frame': current_frame_number
                        }
                    )
                
                current_frame_number += frame_interval
                
                # 最大フレーム数チェック
                if current_frame_number >= video_file.total_frames:
                    break
            
            video_file.complete_processing()
            self.logger.info(f"フレーム抽出完了: {extracted_count}フレーム")
            
        except Exception as e:
            video_file.fail_processing(str(e))
            self.logger.error(f"フレーム抽出エラー: {e}")
            raise VideoProcessingError(
                f"フレーム抽出中にエラーが発生しました: {e}",
                details={'video_file': str(video_file.file_path)}
            )
        finally:
            cap.release()
            self._frame_buffer.clear()
    
    def detect_scene_changes(self, frames: List[Frame], threshold: float = 0.3) -> List[Frame]:
        """
        シーンチェンジを検出して重要フレームを選出
        
        Args:
            frames: 解析対象フレームのリスト
            threshold: シーンチェンジ検出の閾値
            
        Returns:
            List[Frame]: シーンチェンジが検出されたフレーム
            
        Raises:
            InvalidThresholdError: 閾値が範囲外
        """
        if not (0.0 <= threshold <= 1.0):
            raise InvalidThresholdError(
                f"閾値は0.0-1.0の範囲である必要があります: {threshold}"
            )
        
    def _get_video_rotation(self, file_path: Path) -> Optional[int]:
        """
        ffprobeを使って回転メタデータ（rotateタグ）を取得（存在しない場合はNone）
        """
        try:
            result = subprocess.run(
                [
                    'ffprobe',
                    '-v', 'error',
                    '-select_streams', 'v:0',
                    '-show_entries', 'stream_tags=rotate',
                    '-of', 'default=nw=1:nk=1',
                    str(file_path)
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            text = (result.stdout or '').strip()
            if not text:
                return None
            value = int(text)
            value = value % 360
            if value in (0, 90, 180, 270):
                return value
            return None
        except FileNotFoundError:
            # ffprobe未インストール
            return None
        except Exception:
            return None
        if len(frames) < 2:
            return frames.copy()
        
        self.logger.info(f"シーンチェンジ検出開始: {len(frames)}フレーム, 閾値={threshold}")
        
        scene_change_frames = [frames[0]]  # 最初のフレームは常に含める
        
        try:
            for i in range(1, len(frames)):
                current_frame = frames[i]
                previous_frame = frames[i - 1]
                
                # ヒストグラム比較によるシーンチェンジ検出
                scene_score = self._calculate_histogram_difference(
                    previous_frame.image_data,
                    current_frame.image_data
                )
                
                current_frame.scene_score = scene_score
                
                if scene_score >= threshold:
                    scene_change_frames.append(current_frame)
                    self.logger.debug(f"シーンチェンジ検出: フレーム{current_frame.frame_number}, スコア={scene_score:.3f}")
            
            self.logger.info(f"シーンチェンジ検出完了: {len(scene_change_frames)}フレーム選出")
            return scene_change_frames
            
        except Exception as e:
            self.logger.error(f"シーンチェンジ検出エラー: {e}")
            raise VideoProcessingError(
                f"シーンチェンジ検出中にエラーが発生しました: {e}",
                details={'frames_count': len(frames), 'threshold': threshold}
            )
    
    def calculate_quality_score(self, frame: Frame) -> float:
        """
        フレームの品質スコアを計算
        
        Args:
            frame: 評価対象フレーム
            
        Returns:
            float: 品質スコア（0.0-1.0）
            
        Raises:
            InvalidFrameDataError: フレームデータが無効
        """
        if frame is None or frame.image_data is None:
            raise InvalidFrameDataError("フレームデータが無効です")
        
        try:
            # 複数の品質指標を組み合わせて総合スコアを計算
            brightness_score = self._calculate_brightness_quality(frame.image_data)
            contrast_score = self._calculate_contrast_quality(frame.image_data)
            sharpness_score = self._calculate_sharpness_quality(frame.image_data)
            
            # 重み付き平均で総合品質スコア計算
            quality_score = (
                brightness_score * 0.2 +
                contrast_score * 0.3 +
                sharpness_score * 0.5
            )
            
            # フレームのメタデータに詳細スコアを保存
            frame.add_metadata('brightness_score', brightness_score)
            frame.add_metadata('contrast_score', contrast_score)
            frame.add_metadata('sharpness_score', sharpness_score)
            
            return min(1.0, max(0.0, quality_score))
            
        except Exception as e:
            self.logger.error(f"品質スコア計算エラー: {e}")
            raise VideoProcessingError(
                f"品質スコア計算中にエラーが発生しました: {e}",
                details={'frame_number': frame.frame_number}
            )
    
    def get_video_info(self, file_path: Path) -> dict:
        """
        動画ファイルの基本情報を取得
        
        Args:
            file_path: 動画ファイルのパス
            
        Returns:
            dict: 動画情報
        """
        try:
            video_file = self.load_video(file_path)
            return video_file.to_dict()
        except Exception as e:
            self.logger.error(f"動画情報取得エラー: {e}")
            raise VideoProcessingError(
                f"動画情報の取得中にエラーが発生しました: {e}",
                details={'file_path': str(file_path)}
            )
    
    def validate_video_file(self, file_path: Path) -> bool:
        """
        動画ファイルの妥当性を検証
        
        Args:
            file_path: 動画ファイルのパス
            
        Returns:
            bool: 妥当性
        """
        try:
            video_file = self.load_video(file_path)
            return video_file.is_valid
        except Exception:
            return False
    
    def _calculate_histogram_difference(self, image1: np.ndarray, image2: np.ndarray) -> float:
        """ヒストグラム比較によるフレーム間差分を計算"""
        try:
            # BGRからHSVに変換（色相の変化に敏感にするため）
            hsv1 = cv2.cvtColor(image1, cv2.COLOR_RGB2HSV)
            hsv2 = cv2.cvtColor(image2, cv2.COLOR_RGB2HSV)
            
            # HSVの各チャンネルでヒストグラムを計算
            hist1_h = cv2.calcHist([hsv1], [0], None, [180], [0, 180])
            hist1_s = cv2.calcHist([hsv1], [1], None, [256], [0, 256])
            hist1_v = cv2.calcHist([hsv1], [2], None, [256], [0, 256])
            
            hist2_h = cv2.calcHist([hsv2], [0], None, [180], [0, 180])
            hist2_s = cv2.calcHist([hsv2], [1], None, [256], [0, 256])
            hist2_v = cv2.calcHist([hsv2], [2], None, [256], [0, 256])
            
            # 正規化
            cv2.normalize(hist1_h, hist1_h, 0, 1, cv2.NORM_MINMAX)
            cv2.normalize(hist1_s, hist1_s, 0, 1, cv2.NORM_MINMAX)
            cv2.normalize(hist1_v, hist1_v, 0, 1, cv2.NORM_MINMAX)
            cv2.normalize(hist2_h, hist2_h, 0, 1, cv2.NORM_MINMAX)
            cv2.normalize(hist2_s, hist2_s, 0, 1, cv2.NORM_MINMAX)
            cv2.normalize(hist2_v, hist2_v, 0, 1, cv2.NORM_MINMAX)
            
            # 相関係数による比較（1に近いほど類似、0に近いほど異なる）
            corr_h = cv2.compareHist(hist1_h, hist2_h, cv2.HISTCMP_CORREL)
            corr_s = cv2.compareHist(hist1_s, hist2_s, cv2.HISTCMP_CORREL)
            corr_v = cv2.compareHist(hist1_v, hist2_v, cv2.HISTCMP_CORREL)
            
            # 平均相関係数（類似度）
            similarity = (corr_h + corr_s + corr_v) / 3.0
            
            # 差分スコア（1 - 類似度）
            difference = 1.0 - max(0.0, similarity)
            
            return min(1.0, max(0.0, difference))
            
        except Exception as e:
            self.logger.warning(f"ヒストグラム差分計算エラー: {e}")
            return 0.0
    
    def _calculate_brightness_quality(self, image: np.ndarray) -> float:
        """明度品質スコアを計算"""
        try:
            # RGBからグレースケールに変換
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            mean_brightness = np.mean(gray) / 255.0
            
            # 適度な明度（0.3-0.7）を高スコアとする
            if 0.3 <= mean_brightness <= 0.7:
                return 1.0
            elif mean_brightness < 0.3:
                return mean_brightness / 0.3
            else:  # > 0.7
                return (1.0 - mean_brightness) / 0.3
                
        except Exception:
            return 0.5
    
    def _calculate_contrast_quality(self, image: np.ndarray) -> float:
        """コントラスト品質スコアを計算"""
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            contrast = np.std(gray) / 255.0
            
            # 適度なコントラスト（0.1以上）を高スコアとする
            return min(1.0, contrast / 0.1)
            
        except Exception:
            return 0.5
    
    def _calculate_sharpness_quality(self, image: np.ndarray) -> float:
        """鮮明度品質スコアを計算"""
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            
            # ラプラシアンフィルタによるエッジ検出
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            sharpness = np.var(laplacian)
            
            # 正規化（経験的な値を使用）
            normalized_sharpness = min(1.0, sharpness / 1000.0)
            
            return normalized_sharpness
            
        except Exception:
            return 0.5
    
    def cleanup(self):
        """リソースのクリーンアップ"""
        if self._current_video_capture:
            self._current_video_capture.release()
            self._current_video_capture = None
        
        self._frame_buffer.clear()
        self.logger.info("VideoProcessor クリーンアップ完了")
    
    def __del__(self):
        """デストラクタ"""
        self.cleanup()
