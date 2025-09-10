"""
ThumbnailExtractor（サムネイル抽出）サービス

画像リサイズ、切り抜き、PNG保存を使用して、
高品質なサムネイルを生成するサービスクラスです。
"""

import cv2
import numpy as np
from pathlib import Path
from typing import List, Optional, Callable
import logging

from ..models.frame import Frame
from ..models.thumbnail import Thumbnail
from ..models.user_settings import UserSettings, ThumbnailOrientation
from ..models.thumbnail_extraction_job import ThumbnailExtractionJob, JobStatus, JobPhase
from ..lib.errors import (
    ThumbnailExtractionError,
    InsufficientFramesError,
    InvalidSettingsError,
    ThumbnailGenerationError,
    InvalidResolutionError,
    ImageResizeError,
    InvalidDimensionsError,
    InvalidOrientationError,
    CropError,
    FileSaveError,
    BatchSaveError,
    DirectoryError,
    DiskSpaceError,
    FilePermissionError
)


class ThumbnailExtractor:
    """サムネイル抽出サービスクラス"""
    
    def __init__(self):
        """ThumbnailExtractorを初期化"""
        self.logger = logging.getLogger(__name__)
        self.logger.info("ThumbnailExtractor初期化完了")
    
    def extract_thumbnails(self,
                         frames: List[Frame],
                         settings: UserSettings,
                         progress_callback: Optional[Callable[[float], None]] = None) -> List[Thumbnail]:
        """
        フレームからサムネイルを抽出
        
        Args:
            frames: サムネイル抽出対象フレーム
            settings: ユーザー設定
            progress_callback: 進捗通知コールバック
            
        Returns:
            List[Thumbnail]: 生成されたサムネイル
            
        Raises:
            ThumbnailExtractionError: サムネイル抽出に失敗
            InsufficientFramesError: フレーム数が不足
            InvalidSettingsError: 設定が無効
        """
        if not frames:
            raise InsufficientFramesError("抽出対象のフレームが指定されていません")
        
        if settings is None:
            raise InvalidSettingsError("ユーザー設定が指定されていません")
        
        if len(frames) < settings.thumbnail_count:
            self.logger.warning(f"フレーム数が不足しています: {len(frames)} < {settings.thumbnail_count}")
        
        self.logger.info(f"サムネイル抽出開始: {len(frames)}フレーム → {settings.thumbnail_count}枚")
        
        try:
            thumbnails = []
            total_frames = min(len(frames), settings.thumbnail_count)
            
            for i, frame in enumerate(frames[:total_frames]):
                try:
                    # 進捗報告
                    if progress_callback:
                        progress = (i + 1) / total_frames
                        progress_callback(progress)
                    
                    # サムネイル生成
                    thumbnail = self.generate_thumbnail(frame, settings)
                    thumbnails.append(thumbnail)
                    
                    self.logger.debug(f"サムネイル生成完了: {i+1}/{total_frames}")
                    
                except Exception as e:
                    self.logger.warning(f"フレーム{frame.frame_number}のサムネイル生成でエラー: {e}")
                    continue
            
            if not thumbnails:
                raise ThumbnailExtractionError("サムネイルを1枚も生成できませんでした")
            
            self.logger.info(f"サムネイル抽出完了: {len(thumbnails)}枚生成")
            return thumbnails
            
        except (InsufficientFramesError, InvalidSettingsError):
            raise
        except Exception as e:
            self.logger.error(f"サムネイル抽出エラー: {e}")
            raise ThumbnailExtractionError(
                f"サムネイル抽出中にエラーが発生しました: {e}",
                details={'frames_count': len(frames), 'target_count': settings.thumbnail_count}
            )
    
    def generate_thumbnail(self, frame: Frame, settings: UserSettings) -> Thumbnail:
        """
        単一フレームからサムネイルを生成
        
        Args:
            frame: 元フレーム
            settings: ユーザー設定
            
        Returns:
            Thumbnail: 生成されたサムネイル
            
        Raises:
            ThumbnailGenerationError: サムネイル生成に失敗
        """
        try:
            # 元画像を取得（サイズ変更せず、元のフレーム解像度を保持）
            source_image = frame.image_data.copy()

            # サイズから向きを自動判定（幅 < 高さ = 縦型、幅 > 高さ = 横型）
            processed_image = source_image
            height, width = processed_image.shape[:2]
            
            # ユーザー指定サイズから向きを判定
            is_portrait_output = settings.is_portrait_output
            
            try:
                if is_portrait_output:
                    # ユーザー指定の縦比率（例: 1080x1920 → 9:16 ≒ 0.5625）
                    target_aspect = (settings.output_width / settings.output_height)
                    current_aspect = width / height
                    if current_aspect > target_aspect:
                        # 横長 → 左右をクロップ
                        new_width = int(height * target_aspect)
                        start_x = max(0, (width - new_width) // 2)
                        end_x = start_x + new_width
                        processed_image = processed_image[:, start_x:end_x, :]
                    elif current_aspect < target_aspect:
                        # 縦長すぎる → 上下をクロップ
                        new_height = int(width / target_aspect)
                        start_y = max(0, (height - new_height) // 2)
                        end_y = start_y + new_height
                        processed_image = processed_image[start_y:end_y, :, :]
                else:  # 横型出力
                    # ユーザー指定の横比率（例: 1920x1080 → 16:9 ≒ 1.7778）
                    target_aspect = (settings.output_width / settings.output_height)
                    current_aspect = width / height
                    if current_aspect < target_aspect:
                        # 縦長 → 上下をクロップ
                        new_height = int(width / target_aspect)
                        start_y = max(0, (height - new_height) // 2)
                        end_y = start_y + new_height
                        processed_image = processed_image[start_y:end_y, :, :]
                    elif current_aspect > target_aspect:
                        # 横長すぎる → 左右をクロップ
                        new_width = int(height * target_aspect)
                        start_x = max(0, (width - new_width) // 2)
                        end_x = start_x + new_width
                        processed_image = processed_image[:, start_x:end_x, :]
            except Exception:
                pass

            # Thumbnailオブジェクト作成（元解像度のまま）
            thumbnail = Thumbnail.create_from_frame(frame, settings, processed_image)
            
            # 品質メトリクス更新
            thumbnail.update_quality_metrics()
            
            return thumbnail
            
        except Exception as e:
            self.logger.error(f"サムネイル生成エラー: {e}")
            raise ThumbnailGenerationError(
                f"サムネイル生成中にエラーが発生しました: {e}",
                details={'frame_number': frame.frame_number}
            )
    
    def resize_image(self,
                    image: np.ndarray,
                    target_width: int,
                    target_height: int,
                    maintain_aspect_ratio: bool = True) -> np.ndarray:
        """
        画像をリサイズ
        
        Args:
            image: 元画像
            target_width: 目標幅
            target_height: 目標高さ
            maintain_aspect_ratio: アスペクト比を維持するか
            
        Returns:
            np.ndarray: リサイズされた画像
            
        Raises:
            InvalidDimensionsError: 無効な寸法
            ImageResizeError: リサイズに失敗
        """
        if target_width <= 0 or target_height <= 0:
            raise InvalidDimensionsError(f"寸法は正の値である必要があります: {target_width}x{target_height}")
        
        try:
            current_height, current_width = image.shape[:2]
            
            if maintain_aspect_ratio:
                # アスペクト比を維持してリサイズ
                scale_w = target_width / current_width
                scale_h = target_height / current_height
                scale = min(scale_w, scale_h)
                
                new_width = int(current_width * scale)
                new_height = int(current_height * scale)
                
                # リサイズ
                resized = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_LANCZOS4)
                
                # パディングして目標サイズに調整
                if new_width != target_width or new_height != target_height:
                    # 黒いキャンバスを作成
                    canvas = np.zeros((target_height, target_width, 3), dtype=np.uint8)
                    
                    # 中央に配置
                    start_y = (target_height - new_height) // 2
                    start_x = (target_width - new_width) // 2
                    end_y = start_y + new_height
                    end_x = start_x + new_width
                    
                    canvas[start_y:end_y, start_x:end_x] = resized
                    return canvas
                else:
                    return resized
            else:
                # アスペクト比を無視してリサイズ
                return cv2.resize(image, (target_width, target_height), interpolation=cv2.INTER_LANCZOS4)
                
        except Exception as e:
            self.logger.error(f"画像リサイズエラー: {e}")
            raise ImageResizeError(
                f"画像リサイズ中にエラーが発生しました: {e}",
                details={'target_size': f"{target_width}x{target_height}"}
            )
    
    def crop_to_orientation(self, image: np.ndarray, orientation: str) -> np.ndarray:
        """
        指定された向きにクロップ
        
        Args:
            image: 元画像
            orientation: 向き（'landscape' または 'portrait'）
            
        Returns:
            np.ndarray: クロップされた画像
            
        Raises:
            InvalidOrientationError: 無効な向き
            CropError: クロップに失敗
        """
        if orientation not in ['landscape', 'portrait']:
            raise InvalidOrientationError(f"向きは'landscape'または'portrait'である必要があります: {orientation}")
        
        try:
            height, width = image.shape[:2]
            current_aspect = width / height
            
            if orientation == 'landscape':
                target_aspect = 16 / 9  # 一般的な横型アスペクト比
                
                if current_aspect < target_aspect:
                    # 現在が縦長すぎる場合、上下をクロップ
                    new_height = int(width / target_aspect)
                    start_y = (height - new_height) // 2
                    end_y = start_y + new_height
                    return image[start_y:end_y, :, :]
                elif current_aspect > target_aspect:
                    # 現在が横長すぎる場合、左右をクロップ
                    new_width = int(height * target_aspect)
                    start_x = (width - new_width) // 2
                    end_x = start_x + new_width
                    return image[:, start_x:end_x, :]
                else:
                    # アスペクト比が適切な場合はそのまま
                    return image.copy()
                    
            else:  # portrait
                target_aspect = 9 / 16  # 一般的な縦型アスペクト比
                
                if current_aspect > target_aspect:
                    # 現在が横長すぎる場合、左右をクロップ
                    new_width = int(height * target_aspect)
                    start_x = (width - new_width) // 2
                    end_x = start_x + new_width
                    return image[:, start_x:end_x, :]
                elif current_aspect < target_aspect:
                    # 現在が縦長すぎる場合、上下をクロップ
                    new_height = int(width / target_aspect)
                    start_y = (height - new_height) // 2
                    end_y = start_y + new_height
                    return image[start_y:end_y, :, :]
                else:
                    # アスペクト比が適切な場合はそのまま
                    return image.copy()
                    
        except Exception as e:
            self.logger.error(f"画像クロップエラー: {e}")
            raise CropError(
                f"画像クロップ中にエラーが発生しました: {e}",
                details={'orientation': orientation}
            )
    
    def save_thumbnail(self, thumbnail: Thumbnail, file_path: str) -> bool:
        """
        サムネイルをファイルに保存
        
        Args:
            thumbnail: 保存するサムネイル
            file_path: 保存先ファイルパス
            
        Returns:
            bool: 保存成功かどうか
            
        Raises:
            FileSaveError: ファイル保存に失敗
        """
        try:
            # 保存先ディレクトリを確認・作成
            save_path = Path(file_path)
            save_path.parent.mkdir(parents=True, exist_ok=True)
            
            # ディスク容量チェック
            if not self._check_disk_space(save_path.parent, thumbnail.pixel_count * 3):
                raise DiskSpaceError("ディスク容量が不足しています")
            
            # 権限チェック
            if not self._check_write_permission(save_path.parent):
                raise FilePermissionError(f"書き込み権限がありません: {save_path.parent}")
            
            # PNG保存（高品質設定）
            return thumbnail.save(save_path, overwrite=True)
            
        except (DiskSpaceError, FilePermissionError):
            raise
        except Exception as e:
            self.logger.error(f"サムネイル保存エラー: {e}")
            raise FileSaveError(
                f"サムネイル保存中にエラーが発生しました: {e}",
                details={'file_path': file_path}
            )
    
    def save_thumbnails_batch(self, thumbnails: List[Thumbnail], output_directory: str) -> List[str]:
        """
        サムネイルを一括保存
        
        Args:
            thumbnails: 保存するサムネイルのリスト
            output_directory: 出力ディレクトリ
            
        Returns:
            List[str]: 保存されたファイルパスのリスト
            
        Raises:
            BatchSaveError: 一括保存に失敗
            DirectoryError: ディレクトリエラー
        """
        if not thumbnails:
            return []
        
        output_path = Path(output_directory)
        
        # ディレクトリの確認・作成
        try:
            output_path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise DirectoryError(f"出力ディレクトリの作成に失敗しました: {e}")
        
        # 書き込み権限チェック
        if not self._check_write_permission(output_path):
            raise DirectoryError(f"出力ディレクトリに書き込み権限がありません: {output_path}")
        
        self.logger.info(f"サムネイル一括保存開始: {len(thumbnails)}枚 → {output_directory}")
        
        saved_paths = []
        failed_count = 0
        
        try:
            for i, thumbnail in enumerate(thumbnails):
                try:
                    # ファイル名生成
                    filename = thumbnail.user_settings.get_output_filename(i, thumbnail.source_timestamp)
                    file_path = output_path / filename
                    
                    # 保存実行
                    if self.save_thumbnail(thumbnail, str(file_path)):
                        saved_paths.append(str(file_path))
                        self.logger.debug(f"保存完了: {filename}")
                    else:
                        failed_count += 1
                        self.logger.warning(f"保存失敗: {filename}")
                        
                except Exception as e:
                    failed_count += 1
                    self.logger.warning(f"サムネイル{i}の保存でエラー: {e}")
                    continue
            
            # 失敗率が50%を超える場合はエラー
            if failed_count > len(thumbnails) * 0.5:
                raise BatchSaveError(
                    f"一括保存で失敗率が高すぎます: {failed_count}/{len(thumbnails)}",
                    details={
                        'total_thumbnails': len(thumbnails),
                        'failed_count': failed_count,
                        'success_count': len(saved_paths)
                    }
                )
            
            self.logger.info(f"一括保存完了: {len(saved_paths)}/{len(thumbnails)}枚成功")
            return saved_paths
            
        except BatchSaveError:
            raise
        except Exception as e:
            self.logger.error(f"一括保存エラー: {e}")
            raise BatchSaveError(
                f"一括保存中にエラーが発生しました: {e}",
                details={'output_directory': output_directory}
            )
    
    def create_extraction_job(self, frames: List[Frame], settings: UserSettings) -> ThumbnailExtractionJob:
        """
        サムネイル抽出ジョブを作成
        
        Args:
            frames: 処理対象フレーム
            settings: ユーザー設定
            
        Returns:
            ThumbnailExtractionJob: 作成されたジョブ
        """
        try:
            job = ThumbnailExtractionJob.create(
                video_file=frames[0].video_file if frames else None,
                user_settings=settings
            )
            
            # フレームを追加
            for frame in frames:
                job.add_extracted_frame(frame)
            
            self.logger.info(f"抽出ジョブ作成完了: {job.job_id}")
            return job
            
        except Exception as e:
            self.logger.error(f"ジョブ作成エラー: {e}")
            raise ThumbnailExtractionError(
                f"抽出ジョブの作成中にエラーが発生しました: {e}",
                details={'frames_count': len(frames)}
            )
    
    def _check_disk_space(self, directory: Path, required_bytes: int) -> bool:
        """ディスク容量をチェック"""
        try:
            import shutil
            total, used, free = shutil.disk_usage(directory)
            
            # 必要な容量の2倍の余裕があるかチェック
            required_with_margin = required_bytes * 2
            return free >= required_with_margin
            
        except Exception as e:
            self.logger.warning(f"ディスク容量チェックエラー: {e}")
            return True  # チェックできない場合は継続
    
    def _check_write_permission(self, directory: Path) -> bool:
        """書き込み権限をチェック"""
        try:
            # テストファイルの作成・削除
            test_file = directory / ".write_test"
            test_file.touch()
            test_file.unlink()
            return True
            
        except Exception:
            return False
    
    def cleanup(self):
        """リソースのクリーンアップ"""
        # 特にクリーンアップが必要なリソースはない
        self.logger.info("ThumbnailExtractor クリーンアップ完了")
    
    def __del__(self):
        """デストラクタ"""
        self.cleanup()
