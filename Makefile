.PHONY: install build run-app clean distclean

install:
	pip install -r requirements.txt

build:
	pyinstaller --noconfirm pyinstaller.spec

run-app:
	open dist/ThumbnailExtractor.app || true

clean:
	rm -rf build dist __pycache__ */__pycache__

distclean: clean
	rm -f ThumbnailExtractor.spec


