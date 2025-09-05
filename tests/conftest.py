"""
pytest設定とフィクスチャ定義

全テストで共有するフィクスチャとテスト設定を定義します。
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path
from typing import Generator
import pytest
import numpy as np

# src ディレクトリをPythonパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@pytest.fixture(scope="session")
def test_data_dir() -> Path:
    """テストデータディレクトリのパス"""
    return Path(__file__).parent / "sample_data"


@pytest.fixture(scope="session")
def fixtures_dir() -> Path:
    """フィクスチャディレクトリのパス"""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """一時ディレクトリを作成して、テスト後に削除"""
    temp_path = Path(tempfile.mkdtemp())
    try:
        yield temp_path
    finally:
        shutil.rmtree(temp_path)


@pytest.fixture
def sample_image_data() -> np.ndarray:
    """サンプル画像データ（テスト用の3チャンネルRGB画像）"""
    # 640x480のランダムな画像データを生成
    return np.random.randint(0, 256, (480, 640, 3), dtype=np.uint8)


@pytest.fixture
def mock_video_file_path(temp_dir: Path) -> Path:
    """モックの動画ファイルパス"""
    video_path = temp_dir / "test_video.mp4"
    # 実際のファイルは作成せず、パスのみ返す
    return video_path


@pytest.fixture(autouse=True)
def setup_test_environment():
    """各テスト実行前の環境設定"""
    # ログレベルを設定
    os.environ["LOG_LEVEL"] = "DEBUG"
    # テスト用の設定を適用
    os.environ["TESTING"] = "true"
    
    yield
    
    # テスト後のクリーンアップ
    os.environ.pop("LOG_LEVEL", None)
    os.environ.pop("TESTING", None)


def pytest_configure(config):
    """pytest設定の初期化"""
    config.addinivalue_line(
        "markers", "contract: Contract tests for API interfaces"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests for component interactions"
    )
    config.addinivalue_line(
        "markers", "unit: Unit tests for individual functions/classes"
    )
    config.addinivalue_line(
        "markers", "performance: Performance and memory usage tests"
    )
    config.addinivalue_line(
        "markers", "slow: Tests that take a long time to run"
    )


def pytest_collection_modifyitems(config, items):
    """テスト収集時の設定変更"""
    # slowマーカーが付いたテストにスキップ設定を追加（CI環境などで）
    if config.getoption("--fast"):
        skip_slow = pytest.mark.skip(reason="--fast option: skipping slow tests")
        for item in items:
            if "slow" in item.keywords:
                item.add_marker(skip_slow)
