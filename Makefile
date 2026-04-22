.PHONY: dev build run dist reset-demos

APP = dist/Batch\ Rename.app

dev: build run

build:
	uv run python build_app.py

dist: build
	cd dist && zip -r "Batch Rename.zip" "Batch Rename.app"
	@echo "Ready to distribute: dist/Batch Rename.zip"

run:
	-kill $$(pgrep -x "Batch Rename") 2>/dev/null
	while pgrep -x "Batch Rename" > /dev/null 2>&1; do sleep 0.1; done
	open $(APP)

reset-demos:
	rm -rf "demos/01 Simple Demo" "demos/02 Non-Broadcast Concert" "demos/03 Broadcast Concert" "demos/04 Advanced- Shortcodes" "demos/05 Advanced- More Folders" demos/test_clips
	cp -r "previous_version/Adam Borecki's Batch Rename Droplet/Demos/01 Simple Demo" demos/
	cp -r "previous_version/Adam Borecki's Batch Rename Droplet/Demos/02 Non-Broadcast Concert" demos/
	cp -r "previous_version/Adam Borecki's Batch Rename Droplet/Demos/03 Broadcast Concert" demos/
	cp -r "previous_version/Adam Borecki's Batch Rename Droplet/Demos/04 Advanced- Shortcodes" demos/
	cp -r "previous_version/Adam Borecki's Batch Rename Droplet/Demos/05 Advanced- More Folders" demos/
	mkdir -p demos/test_clips
	touch demos/test_clips/001.mov demos/test_clips/002.mov demos/test_clips/003.mov demos/test_clips/004.mov demos/test_clips/005.mov
