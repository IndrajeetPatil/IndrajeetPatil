.PHONY: dev build preview lint format clean downloads hex-stickers update help

dev: ## Start Astro dev server
	pnpm astro dev

build: ## Production build
	pnpm astro build

preview: ## Preview production build locally
	pnpm astro preview

lint: ## Lint and type-check
	pnpm astro check
	pnpm biome check src/

format: ## Format source files
	pnpm biome format --write src/

downloads: ## Fetch CRAN download counts
	cd scripts && uv run fetch_downloads.py

hex-stickers: ## Download R package hex sticker images
	@echo "Fetching hex stickers..."
	@mkdir -p public/images/hex
	@curl -sfL -o public/images/hex/ggstatsplot.png "https://raw.githubusercontent.com/IndrajeetPatil/ggstatsplot/main/man/figures/logo.png" && echo "  ggstatsplot" || echo "  ggstatsplot (failed)"
	@curl -sfL -o public/images/hex/statsExpressions.png "https://raw.githubusercontent.com/IndrajeetPatil/statsExpressions/main/man/figures/logo.png" && echo "  statsExpressions" || echo "  statsExpressions (failed)"
	@curl -sfL -o public/images/hex/datawizard.png "https://raw.githubusercontent.com/easystats/datawizard/main/man/figures/logo.png" && echo "  datawizard" || echo "  datawizard (failed)"
	@curl -sfL -o public/images/hex/insight.png "https://raw.githubusercontent.com/easystats/insight/main/man/figures/logo.png" && echo "  insight" || echo "  insight (failed)"
	@curl -sfL -o public/images/hex/performance.png "https://raw.githubusercontent.com/easystats/performance/main/man/figures/logo.png" && echo "  performance" || echo "  performance (failed)"
	@curl -sfL -o public/images/hex/parameters.png "https://raw.githubusercontent.com/easystats/parameters/main/man/figures/logo.png" && echo "  parameters" || echo "  parameters (failed)"
	@curl -sfL -o public/images/hex/effectsize.png "https://raw.githubusercontent.com/easystats/effectsize/main/man/figures/logo.png" && echo "  effectsize" || echo "  effectsize (failed)"
	@curl -sfL -o public/images/hex/correlation.png "https://raw.githubusercontent.com/easystats/correlation/main/man/figures/logo.png" && echo "  correlation" || echo "  correlation (failed)"
	@curl -sfL -o public/images/hex/bayestestR.png "https://raw.githubusercontent.com/easystats/bayestestR/main/man/figures/logo.png" && echo "  bayestestR" || echo "  bayestestR (failed)"
	@curl -sfL -o public/images/hex/modelbased.png "https://raw.githubusercontent.com/easystats/modelbased/main/man/figures/logo.png" && echo "  modelbased" || echo "  modelbased (failed)"
	@curl -sfL -o public/images/hex/report.png "https://raw.githubusercontent.com/easystats/report/main/man/figures/logo.png" && echo "  report" || echo "  report (failed)"
	@curl -sfL -o public/images/hex/see.png "https://raw.githubusercontent.com/easystats/see/main/man/figures/logo.png" && echo "  see" || echo "  see (failed)"
	@curl -sfL -o public/images/hex/lintr.png "https://raw.githubusercontent.com/r-lib/lintr/main/man/figures/logo.png" && echo "  lintr" || echo "  lintr (failed)"
	@curl -sfL -o public/images/hex/styler.png "https://raw.githubusercontent.com/r-lib/styler/main/man/figures/logo.png" && echo "  styler" || echo "  styler (failed)"
	@curl -sfL -o public/images/hex/ggsignif.png "https://raw.githubusercontent.com/const-ae/ggsignif/main/man/figures/logo.png" && echo "  ggsignif" || echo "  ggsignif (failed)"
	@echo "Done."

clean: ## Remove build artifacts
	rm -rf dist .astro

update: ## Update dependencies
	pnpm update

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
