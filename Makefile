sync:
	op run --env-file="./.env" -- rye run python src/utahwaterpoloassociation/scripts/sync.py

generate:
	mkdir -p output
	rye run python src/utahwaterpoloassociation/scripts/generate.py

server:
	echo "Running at http://127.0.0.1:8000"
	rye run python -m http.server --bind "127.0.0.1" -d "./output"

dev:
	rye run -- honcho -f Procfile start

watch:
	rye run watchmedo shell-command --patterns='content/*;src/utahwaterpoloassociation/templates/*' --recursive --command='make generate' .

copy_assets:
	cp -fR public/* output/

assets:
	rye run watchmedo shell-command --patterns='public/*' --recursive --command='make copy_assets' .

generate_css:
	./tailwindcss -i css/input.css -o output/style.css --minify

tailwind:
	curl -sLO https://github.com/tailwindlabs/tailwindcss/releases/latest/download/tailwindcss-linux-x64
	chmod +x tailwindcss-linux-x64
	mv tailwindcss-linux-x64 tailwindcss

build:
	./build.sh
	
notion_to_markdown:
	mkdir -p markdown
	op run --env-file="./.env" -- rye run notion2md --download -n post --unzipped -p ./markdown --url="https://www.notion.so/Parents-12043305db9a8017b6daead37a6f17fb"
