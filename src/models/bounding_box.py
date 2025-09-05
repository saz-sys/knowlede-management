"""
BoundingBox（境界ボックス）データモデル

境界ボックスを表すクラスです。ピクセル座標変換機能を含みます。
"""

from dataclasses import dataclass
from typing import Tuple, Optional
from .point_2d import Point2D


@dataclass(frozen=True)
class BoundingBox:
    """境界ボックスを表すクラス（正規化座標0-1で管理）"""
    
    x: float      # 左上角のX座標（正規化）
    y: float      # 左上角のY座標（正規化）
    width: float  # 幅（正規化）
    height: float # 高さ（正規化）
    
    def __post_init__(self):
        """初期化後のバリデーション"""
        # 座標値の型チェック
        for attr_name, value in [("x", self.x), ("y", self.y), ("width", self.width), ("height", self.height)]:
            if not isinstance(value, (int, float)):
                raise TypeError(f"{attr_name}は数値である必要があります: {type(value)}")
        
        # 正規化座標の範囲チェック
        if not (0.0 <= self.x <= 1.0):
            raise ValueError(f"xは0-1の範囲である必要があります: {self.x}")
        if not (0.0 <= self.y <= 1.0):
            raise ValueError(f"yは0-1の範囲である必要があります: {self.y}")
        if not (0.0 < self.width <= 1.0):
            raise ValueError(f"widthは0より大きく1以下である必要があります: {self.width}")
        if not (0.0 < self.height <= 1.0):
            raise ValueError(f"heightは0より大きく1以下である必要があります: {self.height}")
        
        # 境界チェック（右下角が1.0を超えないこと）
        if self.x + self.width > 1.0:
            raise ValueError(f"右端が画像境界を超えています: x={self.x}, width={self.width}")
        if self.y + self.height > 1.0:
            raise ValueError(f"下端が画像境界を超えています: y={self.y}, height={self.height}")
    
    @property
    def left(self) -> float:
        """左端のX座標"""
        return self.x
    
    @property
    def top(self) -> float:
        """上端のY座標"""
        return self.y
    
    @property
    def right(self) -> float:
        """右端のX座標"""
        return self.x + self.width
    
    @property
    def bottom(self) -> float:
        """下端のY座標"""
        return self.y + self.height
    
    @property
    def center(self) -> Point2D:
        """中心座標"""
        return Point2D(
            x=self.x + self.width / 2.0,
            y=self.y + self.height / 2.0
        )
    
    @property
    def top_left(self) -> Point2D:
        """左上角の座標"""
        return Point2D(x=self.x, y=self.y)
    
    @property
    def top_right(self) -> Point2D:
        """右上角の座標"""
        return Point2D(x=self.right, y=self.y)
    
    @property
    def bottom_left(self) -> Point2D:
        """左下角の座標"""
        return Point2D(x=self.x, y=self.bottom)
    
    @property
    def bottom_right(self) -> Point2D:
        """右下角の座標"""
        return Point2D(x=self.right, y=self.bottom)
    
    @property
    def area(self) -> float:
        """面積（正規化座標での面積）"""
        return self.width * self.height
    
    @property
    def aspect_ratio(self) -> float:
        """アスペクト比（幅/高さ）"""
        return self.width / self.height
    
    def to_pixel_coordinates(self, image_width: int, image_height: int) -> Tuple[int, int, int, int]:
        """ピクセル座標に変換（x, y, width, height）"""
        if image_width <= 0 or image_height <= 0:
            raise ValueError("画像の幅と高さは正の値である必要があります")
        
        pixel_x = int(round(self.x * image_width))
        pixel_y = int(round(self.y * image_height))
        pixel_width = int(round(self.width * image_width))
        pixel_height = int(round(self.height * image_height))
        
        # 境界チェック
        pixel_x = max(0, min(pixel_x, image_width - 1))
        pixel_y = max(0, min(pixel_y, image_height - 1))
        pixel_width = max(1, min(pixel_width, image_width - pixel_x))
        pixel_height = max(1, min(pixel_height, image_height - pixel_y))
        
        return (pixel_x, pixel_y, pixel_width, pixel_height)
    
    def to_pixel_coordinates_xyxy(self, image_width: int, image_height: int) -> Tuple[int, int, int, int]:
        """ピクセル座標に変換（x1, y1, x2, y2）"""
        if image_width <= 0 or image_height <= 0:
            raise ValueError("画像の幅と高さは正の値である必要があります")
        
        x1 = int(round(self.x * image_width))
        y1 = int(round(self.y * image_height))
        x2 = int(round(self.right * image_width))
        y2 = int(round(self.bottom * image_height))
        
        # 境界チェック
        x1 = max(0, min(x1, image_width - 1))
        y1 = max(0, min(y1, image_height - 1))
        x2 = max(x1 + 1, min(x2, image_width))
        y2 = max(y1 + 1, min(y2, image_height))
        
        return (x1, y1, x2, y2)
    
    @classmethod
    def from_pixel_coordinates(
        cls, 
        x: int, 
        y: int, 
        width: int, 
        height: int, 
        image_width: int, 
        image_height: int
    ) -> 'BoundingBox':
        """ピクセル座標から境界ボックスを作成"""
        if image_width <= 0 or image_height <= 0:
            raise ValueError("画像の幅と高さは正の値である必要があります")
        
        # 正規化座標に変換
        norm_x = x / image_width
        norm_y = y / image_height
        norm_width = width / image_width
        norm_height = height / image_height
        
        return cls(x=norm_x, y=norm_y, width=norm_width, height=norm_height)
    
    @classmethod
    def from_pixel_coordinates_xyxy(
        cls, 
        x1: int, 
        y1: int, 
        x2: int, 
        y2: int, 
        image_width: int, 
        image_height: int
    ) -> 'BoundingBox':
        """ピクセル座標（x1, y1, x2, y2）から境界ボックスを作成"""
        if image_width <= 0 or image_height <= 0:
            raise ValueError("画像の幅と高さは正の値である必要があります")
        
        # 座標の順序を修正
        x_min, x_max = min(x1, x2), max(x1, x2)
        y_min, y_max = min(y1, y2), max(y1, y2)
        
        width = x_max - x_min
        height = y_max - y_min
        
        return cls.from_pixel_coordinates(x_min, y_min, width, height, image_width, image_height)
    
    def contains_point(self, point: Point2D) -> bool:
        """指定した点が境界ボックス内にあるかチェック"""
        if not isinstance(point, Point2D):
            raise TypeError("引数はPoint2Dインスタンスである必要があります")
        
        return (self.x <= point.x <= self.right and 
                self.y <= point.y <= self.bottom)
    
    def overlaps_with(self, other: 'BoundingBox') -> bool:
        """他の境界ボックスと重複しているかチェック"""
        if not isinstance(other, BoundingBox):
            raise TypeError("引数はBoundingBoxインスタンスである必要があります")
        
        return not (self.right <= other.x or 
                   other.right <= self.x or 
                   self.bottom <= other.y or 
                   other.bottom <= self.y)
    
    def intersection_with(self, other: 'BoundingBox') -> Optional['BoundingBox']:
        """他の境界ボックスとの交差領域を計算"""
        if not isinstance(other, BoundingBox):
            raise TypeError("引数はBoundingBoxインスタンスである必要があります")
        
        if not self.overlaps_with(other):
            return None
        
        x_left = max(self.x, other.x)
        y_top = max(self.y, other.y)
        x_right = min(self.right, other.right)
        y_bottom = min(self.bottom, other.bottom)
        
        width = x_right - x_left
        height = y_bottom - y_top
        
        if width > 0 and height > 0:
            return BoundingBox(x=x_left, y=y_top, width=width, height=height)
        return None
    
    def union_with(self, other: 'BoundingBox') -> 'BoundingBox':
        """他の境界ボックスとの結合領域を計算"""
        if not isinstance(other, BoundingBox):
            raise TypeError("引数はBoundingBoxインスタンスである必要があります")
        
        x_left = min(self.x, other.x)
        y_top = min(self.y, other.y)
        x_right = max(self.right, other.right)
        y_bottom = max(self.bottom, other.bottom)
        
        width = x_right - x_left
        height = y_bottom - y_top
        
        return BoundingBox(x=x_left, y=y_top, width=width, height=height)
    
    def iou(self, other: 'BoundingBox') -> float:
        """他の境界ボックスとのIoU（Intersection over Union）を計算"""
        if not isinstance(other, BoundingBox):
            raise TypeError("引数はBoundingBoxインスタンスである必要があります")
        
        intersection = self.intersection_with(other)
        if intersection is None:
            return 0.0
        
        intersection_area = intersection.area
        union_area = self.area + other.area - intersection_area
        
        if union_area == 0:
            return 0.0
        
        return intersection_area / union_area
    
    def expand(self, margin_ratio: float) -> 'BoundingBox':
        """境界ボックスを指定した比率で拡大"""
        if margin_ratio < 0:
            raise ValueError("拡大比率は0以上である必要があります")
        
        margin_x = self.width * margin_ratio / 2.0
        margin_y = self.height * margin_ratio / 2.0
        
        new_x = max(0.0, self.x - margin_x)
        new_y = max(0.0, self.y - margin_y)
        new_width = min(1.0 - new_x, self.width + 2 * margin_x)
        new_height = min(1.0 - new_y, self.height + 2 * margin_y)
        
        return BoundingBox(x=new_x, y=new_y, width=new_width, height=new_height)
    
    def scale(self, scale_factor: float) -> 'BoundingBox':
        """境界ボックスを中心基準でスケーリング"""
        if scale_factor <= 0:
            raise ValueError("スケール係数は正の値である必要があります")
        
        center = self.center
        new_width = min(1.0, self.width * scale_factor)
        new_height = min(1.0, self.height * scale_factor)
        
        new_x = max(0.0, center.x - new_width / 2.0)
        new_y = max(0.0, center.y - new_height / 2.0)
        
        # 境界調整
        if new_x + new_width > 1.0:
            new_x = 1.0 - new_width
        if new_y + new_height > 1.0:
            new_y = 1.0 - new_height
        
        return BoundingBox(x=new_x, y=new_y, width=new_width, height=new_height)
    
    def __str__(self) -> str:
        """文字列表現"""
        return f"BoundingBox(x={self.x:.3f}, y={self.y:.3f}, w={self.width:.3f}, h={self.height:.3f})"
    
    def __repr__(self) -> str:
        """デバッグ用文字列表現"""
        return f"BoundingBox(x={self.x}, y={self.y}, width={self.width}, height={self.height})"
