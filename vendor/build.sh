#!/bin/sh
# Regenerate vendor/tailwind.css after editing classes in index.html.
# Run from the repo root:  sh vendor/build.sh
npx --yes tailwindcss@3.4.14 -c vendor/tailwind.config.js -i vendor/tailwind.input.css -o vendor/tailwind.css --minify
