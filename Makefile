.PHONY: dev build run

APP = dist/Batch\ Rename.app

dev: build run

build:
	uv run python build_app.py

run:
	-kill $$(pgrep -x "Batch Rename") 2>/dev/null
	while pgrep -x "Batch Rename" > /dev/null 2>&1; do sleep 0.1; done
	open $(APP)
