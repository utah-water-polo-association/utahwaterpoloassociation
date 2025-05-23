# In CI environment variables will be set no need to use 1password

UNAME_S := $(shell uname -s)
UNAME_P := $(shell uname -p)
TAILWIND :=./tailwindcss

ifeq "$(CI)" "true"
    PULL_ENV :=
else
    PULL_ENV :=  op run --env-file="./.env" --
endif

ifeq "$(UNAME_S)" "Darwin"
	OS :=macos
else
    OS :=linux
endif

ifeq "$(UNAME_P)" "arm"
	ARCH :=arm64
else
    ARCH :=x64
endif

sync:
	${PULL_ENV} rye run python src/utahwaterpoloassociation/scripts/sync.py

generate:
	mkdir -p output
	rm -fR output/*
	rye run python src/utahwaterpoloassociation/scripts/generate.py
	make copy_assets
	make generate_css

server:
	echo "Running at http://127.0.0.1:8000"
	rye run python -m http.server --bind "127.0.0.1" -d "./output"

dev:
	rye run -- honcho -e .env -f Procfile start

watch:
	rye run watchmedo shell-command --patterns='content/*;src/utahwaterpoloassociation/templates/*;global.yaml' --recursive --command='make generate' .

copy_assets:
	./copy.sh

assets:
	rye run watchmedo shell-command --patterns='public/*' --recursive --command='make copy_assets' .

generate_css:
	${TAILWIND} -i css/input.css -o output/style.css --minify

tailwind:
	curl -sLO https://github.com/tailwindlabs/tailwindcss/releases/latest/download/tailwindcss-${OS}-${ARCH}
	chmod +x tailwindcss-${OS}-${ARCH}
	mv tailwindcss-${OS}-${ARCH} tailwindcss

build:
	./build.sh
	
test:
	rye run pytest

deploy:
	./deploy.sh

load:
	rye run python src/utahwaterpoloassociation/scripts/load.py > output/ratings.html

rsync:
	rsync -r --delete-after output/* eczrvsmy@50.6.153.225:/home1/eczrvsmy/public_html/website_287658e3/
	rsync -r --delete-after output/* eczrvsmy@50.6.153.225:/home1/eczrvsmy/public_html/

rsync_php:
	rsync -r --delete-after public/*.php eczrvsmy@50.6.153.225:/home1/eczrvsmy/public_html/

ssh:
	ssh eczrvsmy@50.6.153.225

dump_games:
	rye run python src/utahwaterpoloassociation/scripts/dump_games.py | jq -s '.[].tournament_name'