"""
Point2D（2D座標点）データモデル

2次元座標を表すクラスです。座標計算メソッドを含みます。
"""

from dataclasses import dataclass
from typing import Tuple
import math


@dataclass(frozen=True)
class Point2D:
    """2D座標点を表すクラス"""
    
    x: float  # X座標
    y: float  # Y座標
    
    def __post_init__(self):
        """初期化後のバリデーション"""
        if not isinstance(self.x, (int, float)):
            raise TypeError(f"x座標は数値である必要があります: {type(self.x)}")
        if not isinstance(self.y, (int, float)):
            raise TypeError(f"y座標は数値である必要があります: {type(self.y)}")
        
        if math.isnan(self.x) or math.isnan(self.y):
            raise ValueError("座標にNaNは使用できません")
        if math.isinf(self.x) or math.isinf(self.y):
            raise ValueError("座標に無限大は使用できません")
    
    def distance_to(self, other: 'Point2D') -> float:
        """他の点との距離を計算"""
        if not isinstance(other, Point2D):
            raise TypeError("引数はPoint2Dインスタンスである必要があります")
        
        dx = self.x - other.x
        dy = self.y - other.y
        return math.sqrt(dx * dx + dy * dy)
    
    def manhattan_distance_to(self, other: 'Point2D') -> float:
        """他の点とのマンハッタン距離を計算"""
        if not isinstance(other, Point2D):
            raise TypeError("引数はPoint2Dインスタンスである必要があります")
        
        return abs(self.x - other.x) + abs(self.y - other.y)
    
    def midpoint_to(self, other: 'Point2D') -> 'Point2D':
        """他の点との中点を計算"""
        if not isinstance(other, Point2D):
            raise TypeError("引数はPoint2Dインスタンスである必要があります")
        
        return Point2D(
            x=(self.x + other.x) / 2.0,
            y=(self.y + other.y) / 2.0
        )
    
    def translate(self, dx: float, dy: float) -> 'Point2D':
        """座標を平行移動"""
        return Point2D(x=self.x + dx, y=self.y + dy)
    
    def scale(self, factor: float, origin: 'Point2D' = None) -> 'Point2D':
        """座標をスケーリング"""
        if origin is None:
            origin = Point2D(0, 0)
        
        if not isinstance(origin, Point2D):
            raise TypeError("originはPoint2Dインスタンスである必要があります")
        
        # 原点を基準にスケーリング
        translated = self.translate(-origin.x, -origin.y)
        scaled = Point2D(
            x=translated.x * factor,
            y=translated.y * factor
        )
        return scaled.translate(origin.x, origin.y)
    
    def rotate(self, angle_radians: float, origin: 'Point2D' = None) -> 'Point2D':
        """座標を回転"""
        if origin is None:
            origin = Point2D(0, 0)
        
        if not isinstance(origin, Point2D):
            raise TypeError("originはPoint2Dインスタンスである必要があります")
        
        # 原点を基準に回転
        translated = self.translate(-origin.x, -origin.y)
        
        cos_angle = math.cos(angle_radians)
        sin_angle = math.sin(angle_radians)
        
        rotated = Point2D(
            x=translated.x * cos_angle - translated.y * sin_angle,
            y=translated.x * sin_angle + translated.y * cos_angle
        )
        
        return rotated.translate(origin.x, origin.y)
    
    def to_tuple(self) -> Tuple[float, float]:
        """タプル形式で座標を返す"""
        return (self.x, self.y)
    
    def to_int_tuple(self) -> Tuple[int, int]:
        """整数タプル形式で座標を返す（ピクセル座標用）"""
        return (int(round(self.x)), int(round(self.y)))
    
    def is_within_bounds(self, width: float, height: float) -> bool:
        """指定された境界内にあるかチェック"""
        return 0 <= self.x <= width and 0 <= self.y <= height
    
    def is_within_normalized_bounds(self) -> bool:
        """正規化座標（0-1の範囲）内にあるかチェック"""
        return 0.0 <= self.x <= 1.0 and 0.0 <= self.y <= 1.0
    
    def normalize(self, width: float, height: float) -> 'Point2D':
        """ピクセル座標を正規化座標に変換"""
        if width <= 0 or height <= 0:
            raise ValueError("幅と高さは正の値である必要があります")
        
        return Point2D(x=self.x / width, y=self.y / height)
    
    def denormalize(self, width: float, height: float) -> 'Point2D':
        """正規化座標をピクセル座標に変換"""
        if width <= 0 or height <= 0:
            raise ValueError("幅と高さは正の値である必要があります")
        
        return Point2D(x=self.x * width, y=self.y * height)
    
    def __add__(self, other: 'Point2D') -> 'Point2D':
        """座標の加算"""
        if not isinstance(other, Point2D):
            raise TypeError("加算相手はPoint2Dインスタンスである必要があります")
        return Point2D(x=self.x + other.x, y=self.y + other.y)
    
    def __sub__(self, other: 'Point2D') -> 'Point2D':
        """座標の減算"""
        if not isinstance(other, Point2D):
            raise TypeError("減算相手はPoint2Dインスタンスである必要があります")
        return Point2D(x=self.x - other.x, y=self.y - other.y)
    
    def __mul__(self, scalar: float) -> 'Point2D':
        """スカラー倍"""
        return Point2D(x=self.x * scalar, y=self.y * scalar)
    
    def __truediv__(self, scalar: float) -> 'Point2D':
        """スカラー除算"""
        if scalar == 0:
            raise ZeroDivisionError("0で除算することはできません")
        return Point2D(x=self.x / scalar, y=self.y / scalar)
    
    def __str__(self) -> str:
        """文字列表現"""
        return f"Point2D(x={self.x:.2f}, y={self.y:.2f})"
    
    def __repr__(self) -> str:
        """デバッグ用文字列表現"""
        return f"Point2D(x={self.x}, y={self.y})"
