#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE_DIR="${SOURCE_DIR:-$ROOT_DIR/C4}"
OUTPUT_DIR="${OUTPUT_DIR:-$ROOT_DIR/docs/assets/diagrams}"
PLANTUML_IMAGE="${PLANTUML_IMAGE:-plantuml/plantuml:1.2026.6}"

mkdir -p "$OUTPUT_DIR"

mapfile -t SOURCES < <(
  find "$SOURCE_DIR" -maxdepth 1 -type f -name '*.puml' -printf '%f\n' | sort
)

if [ "${#SOURCES[@]}" -eq 0 ]; then
  echo "No PlantUML sources found in $SOURCE_DIR." >&2
  exit 1
fi

pull_image() {
  local attempt
  for attempt in 1 2 3; do
    if docker pull "$PLANTUML_IMAGE"; then
      return 0
    fi
    echo "PlantUML image pull failed (attempt $attempt/3)." >&2
    sleep $((attempt * 5))
  done

  echo "Unable to pull $PLANTUML_IMAGE after 3 attempts." >&2
  return 1
}

render() {
  local format="$1"
  local args=()

  for source in "${SOURCES[@]}"; do
    args+=("C4/$source")
  done

  docker run --rm \
    -v "$ROOT_DIR:/workspace" \
    -w /workspace \
    "$PLANTUML_IMAGE" \
    -charset UTF-8 "-t$format" \
    -o ../docs/assets/diagrams \
    "${args[@]}"
}

pull_image
render svg
render png

echo "Rendered ${#SOURCES[@]} PlantUML diagrams to docs/assets/diagrams."
