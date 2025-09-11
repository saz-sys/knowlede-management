#!/usr/bin/env python3
"""
アイコンファイルを作成するスクリプト
PILを使用してシンプルなアイコンを生成します
"""

import os
from PIL import Image, ImageDraw

def create_icon():
    """FrameSnap AIアイコンを作成"""
    # アイコンディレクトリを作成
    os.makedirs('assets/icons', exist_ok=True)
    
    # 複数のサイズでアイコンを作成
    sizes = [16, 32, 64, 128, 256, 512, 1024]
    images = []
    
    for size in sizes:
        # 新しい画像を作成（濃い青色の背景）
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # 背景の角丸四角形を描画（濃い青色）
        margin = size // 16
        draw.rounded_rectangle([margin, margin, size-margin, size-margin], 
                              radius=size//8, fill=(25, 42, 86, 255))  # 濃い青色
        
        # カメラの絞りを描画（中心から）
        center_x, center_y = size // 2, size // 2
        aperture_radius = size // 4
        
        # 絞りのセグメントを描画（水色とティールグリーン）
        colors = [(64, 224, 208, 255), (0, 128, 128, 255)]  # 水色とティール
        for i in range(8):
            start_angle = i * 45
            end_angle = (i + 1) * 45
            color = colors[i % 2]
            
            # 扇形を描画
            draw.pieslice([center_x - aperture_radius, center_y - aperture_radius,
                          center_x + aperture_radius, center_y + aperture_radius],
                         start_angle, end_angle, fill=color)
        
        # 中央の白い円を描画
        inner_radius = aperture_radius // 3
        draw.ellipse([center_x - inner_radius, center_y - inner_radius,
                     center_x + inner_radius, center_y + inner_radius],
                    fill=(255, 255, 255, 255))
        
        # 再生ボタン（白い三角形）を描画
        if size >= 32:  # 小さいサイズでは再生ボタンを描画しない
            play_size = size // 12
            play_x = center_x + size // 8
            play_y = center_y
            draw.polygon([(play_x - play_size, play_y - play_size),
                         (play_x - play_size, play_y + play_size),
                         (play_x + play_size, play_y)], fill=(255, 255, 255, 255))
        
        # オレンジのハイライトを描画
        if size >= 64:  # 中サイズ以上でハイライトを描画
            highlight_size = size // 16
            highlight_x = center_x + size // 6
            highlight_y = center_y - size // 8
            draw.ellipse([highlight_x - highlight_size, highlight_y - highlight_size,
                         highlight_x + highlight_size, highlight_y + highlight_size],
                        fill=(255, 165, 0, 255))  # オレンジ
        
        # 右下に顔の輪郭を描画（小さいサイズでは省略）
        if size >= 128:
            face_size = size // 8
            face_x = size - size // 6
            face_y = size - size // 6
            
            # 顔の輪郭（楕円）
            draw.ellipse([face_x - face_size, face_y - face_size,
                         face_x + face_size, face_y + face_size],
                        outline=(255, 255, 255, 255), width=2)
            
            # 目
            eye_size = face_size // 4
            draw.ellipse([face_x - face_size//2 - eye_size, face_y - face_size//2 - eye_size,
                         face_x - face_size//2 + eye_size, face_y - face_size//2 + eye_size],
                        fill=(255, 255, 255, 255))
            draw.ellipse([face_x + face_size//2 - eye_size, face_y - face_size//2 - eye_size,
                         face_x + face_size//2 + eye_size, face_y - face_size//2 + eye_size],
                        fill=(255, 255, 255, 255))
        
        images.append(img)
    
    # ICOファイルとして保存（Windows用）
    images[0].save('assets/icons/framesnap.ico', format='ICO', sizes=[(img.width, img.height) for img in images])
    
    # PNGファイルとして保存（Linux用）
    images[-1].save('assets/icons/framesnap.png', format='PNG')
    
    print("アイコンファイルを作成しました:")
    print("- assets/icons/framesnap.ico (Windows用)")
    print("- assets/icons/framesnap.png (Linux用)")
    print()
    print("macOS用の.icnsファイルを作成するには、以下のコマンドを実行してください:")
    print("iconutil -c icns assets/icons/framesnap.iconset")
    print()
    print("または、以下のサイズのPNGファイルをframesnap.iconsetディレクトリに配置してください:")
    for size in [16, 32, 64, 128, 256, 512, 1024]:
        print(f"- icon_{size}x{size}.png")
        if size != 1024:
            print(f"- icon_{size}x{size}@2x.png")

if __name__ == '__main__':
    create_icon()
