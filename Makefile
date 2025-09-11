.PHONY: install build run-app clean distclean

install:
	pip install -r requirements.txt

build:
	@if [ ! -f "assets/icons/framesnap.icns" ]; then \
		echo "Warning: Icon file assets/icons/framesnap.icns not found. Building without icon."; \
	fi
	pyinstaller --noconfirm pyinstaller.spec

run-app:
	open dist/FrameSnap.app || true

clean:
	rm -rf build dist __pycache__ */__pycache__

distclean: clean
	rm -f ThumbnailExtractor.spec


