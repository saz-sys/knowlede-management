"""
動画サムネイル抽出機能のセットアップ設定
"""

from setuptools import setup, find_packages

with open("requirements.txt") as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="video-thumbnail-extractor",
    version="1.0.0",
    description="社内向けアニメ動画サムネイル抽出デスクトップアプリケーション",
    long_description="MP4動画からキャラクターの顔が写った複数のサムネイルをPNG形式で抽出するローカル完結型ツール",
    author="Video Thumbnail Extractor Team",
    python_requires=">=3.11",
    packages=find_packages(),
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "thumbnail-extractor=src.cli.main:main",
            "thumbnail-gui=src.gui.main_window:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Topic :: Multimedia :: Video",
        "Topic :: Multimedia :: Graphics",
    ],
    keywords="video thumbnail extraction anime face-detection local-processing",
    package_data={
        "src": ["*.txt", "*.md"],
    },
    include_package_data=True,
)
