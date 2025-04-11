#!/bin/bash

# Script to generate PNG diagrams from simplified PlantUML files
# Usage: ./update_diagrams.sh

# Ensure we're in the right directory
cd "$(dirname "$0")"

# Check if Kroki server is running
if ! curl -s http://localhost:8000 > /dev/null; then
  echo "Error: Kroki server not running at http://localhost:8000"
  exit 1
fi

# Function to generate a PNG from a PUML file
function generate_png() {
  local puml_file=$1
  local png_file=${puml_file/.puml/.png}
  local png_dir=$(dirname "$png_file")/png
  
  # Create png directory if it doesn't exist
  mkdir -p $(dirname "$png_dir")
  
  # Set the output path
  local output_path="$png_dir/$(basename "$png_file")"
  
  echo "Generating $output_path from $puml_file"
  curl -s -X POST --data-binary @"$puml_file" http://localhost:8000/plantuml/png > "$output_path"
  
  # Check if generation was successful
  if [ -f "$output_path" ] && [ $(stat -c%s "$output_path") -gt 1000 ]; then
    echo "  Success: $(stat -c%s "$output_path") bytes"
  else
    echo "  Error: Failed to generate PNG or file is too small"
  fi
}

# Generate PNGs from simplified diagrams
generate_png "uml/core/base_agent_simplified.puml"
generate_png "uml/core/memory/memory_minimal.puml"
generate_png "uml/re_act/re_act_class_simplified.puml"
generate_png "uml/reflexion/reflexion_class_simplified.puml"

echo "Done generating PNG diagrams."