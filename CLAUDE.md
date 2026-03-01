# Utah Water Polo Association

Static site for [utahwaterpoloassociation.com](https://utahwaterpoloassociation.com). Generates HTML from league data (JSON/CSV), markdown content, and Jinja2 templates.

## Tech Stack

- **Python** with **rye** for dependency/env management
- **Pydantic** models for all data structures
- **Jinja2** templates (`.html.jinja2`)
- **TailwindCSS** (standalone CLI binary, not npm) for styling
- **Alpine.js** for client-side interactivity
- **Markdown** content with Jinja2 preprocessing
- **Notion API** for syncing content (schedules, pages)

## Commands (Makefile)

| Command | What it does |
|---|---|
| `make dev` | Run dev server + file watcher via honcho |
| `make generate` | Build the site: render pages, copy assets, compile CSS |
| `make sync` | Pull data from Notion API into local JSON/content |
| `make test` | Run pytest |
| `make build` | Full CI build: install rye, sync deps, pull data, generate site |
| `make server` | Serve `output/` on localhost:8000 |
| `make deploy` | Deploy via rsync to shared hosting |
| `make tailwind` | Download the TailwindCSS standalone binary |

Locally, secrets are loaded via 1Password (`op run --env-file="./.env"`). In CI, env vars are set directly.

## Project Structure

```
content/           Markdown pages (synced from Notion), each dir is a route
data/              League JSON files and CSV schedules
public/            Static assets (images, fonts, etc.) copied to output
css/               TailwindCSS input
output/            Generated site (gitignored)
pages/             Additional page definitions
global.json        Site-wide nav and metadata
global.yaml        Additional global config

src/utahwaterpoloassociation/
  models/          Pydantic models: Game, Team, Division, Tournament, League, etc.
  templates/       Jinja2 templates (.html.jinja2)
  pages/           Page types: MarkdownPage, DynamicPage, PageBase
  repos/           Data loading: league JSON parsing, section collection
  services/        Business logic (league rankings)
  scripts/         Entry points: generate.py, sync.py, dump_games.py
  generator.py     Core Generator class: loads pages, renders to output/
  jinja_env.py     Jinja2 environment setup, markdown filter, template globals
  global_data.py   Loads league data + global.json into the Data model
  page.py          Legacy Page model (renders markdown files to HTML)
```

## Architecture

```
Notion API ──sync.py──> data/*.json + content/**/*.md
                              │
                              v
              global_data.py (loads JSON, builds Data model)
                              │
                              v
              Generator: collects pages (Markdown + Dynamic)
                              │
                              v
              Jinja2 templates render with globals `g` (Data) and `p` (page)
                              │
                              v
                          output/*.html
                              │
                    TailwindCSS compiles CSS
                              │
                              v
                      rsync to hosting
```

## Key Conventions

- **Template variables**: `g` is the global `Data` object (league, meta, past seasons). `p` is the current page's `FileData`.
- **Template globals**: `schedule_fall_high_school`, `schedule_spring`, `club_map`, `instagram` are callable Jinja2 globals that render sub-templates.
- **Markdown preprocessing**: Markdown files are run through Jinja2 first, so they can use template variables and globals.
- **Models**: Pydantic BaseModel everywhere. Some models use a `MAP` ClassVar for CSV column mapping (see `models/csv.py`).
- **League data**: `Leagues` enum in `repos/` defines available seasons. Current season is loaded as `data.league`, past seasons in `data.past`.
- **Spelling**: The codebase spells "league" as `leauge` in filenames and classes. Don't "fix" this, it would break imports everywhere.

## Testing

```
make test    # runs: rye run pytest
```

Tests live in `tests/`. Run only the tests you modify to avoid wasting time.

## CI/CD

GitHub Actions (`.github/workflows/deploy.yaml`):
- Triggers on push to any branch and hourly cron
- Runs `make build` (installs rye, syncs, generates)
- Deploys to shared hosting via rsync (main branch only)
- Secrets: `NOTION_TOKEN` (var), `SSH_PRIVATE_KEY` (secret)
