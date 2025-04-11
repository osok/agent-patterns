#!/bin/bash

# Create PNG directories
mkdir -p uml/core/png uml/core/memory/png uml/core/tools/png
mkdir -p uml/re_act/png uml/reflexion/png uml/llm_compiler/png uml/self_discovery/png
mkdir -p uml/lats/png uml/reflection/png uml/rewoo/png uml/reflection_and_refinement/png
mkdir -p uml/plan_and_solve/png uml/storm/png

# Function to generate a PNG from a PUML file
function generate_png() {
  local puml_file=$1
  local dir_name=$(dirname "$puml_file")
  local base_name=$(basename "$puml_file" .puml)
  local output_path="$dir_name/png/$base_name.png"
  
  echo "Generating $output_path from $puml_file"
  curl -s -X POST --data-binary @"$puml_file" http://localhost:8000/plantuml/png > "$output_path"
  
  # Check file size to see if generation was successful
  if [ -f "$output_path" ]; then
    file_size=$(stat -c%s "$output_path")
    if [ $file_size -lt 1000 ]; then
      echo "  Warning: $output_path may have failed (size: $file_size bytes)"
    else
      echo "  Success: $output_path generated (size: $file_size bytes)"
    fi
  else
    echo "  Error: Failed to create $output_path"
  fi
}

# Core diagrams
generate_png "uml/core/base_agent_simplified.puml"
generate_png "uml/core/memory/memory_minimal.puml"

# Pattern diagrams
generate_png "uml/re_act/re_act_class_simplified.puml"
generate_png "uml/reflexion/reflexion_class_simplified.puml"
generate_png "uml/reflexion/reflexion_state.puml"
generate_png "uml/reflexion/reflexion_sequence.puml"
generate_png "uml/llm_compiler/llm_compiler_class.puml"
generate_png "uml/llm_compiler/llm_compiler_state.puml"
generate_png "uml/llm_compiler/llm_compiler_sequence.puml"
generate_png "uml/self_discovery/self_discovery_class.puml"
generate_png "uml/self_discovery/self_discovery_state.puml"
generate_png "uml/self_discovery/self_discovery_sequence.puml"
generate_png "uml/lats/lats_class.puml"
generate_png "uml/lats/lats_state.puml"
generate_png "uml/lats/lats_sequence.puml"
generate_png "uml/reflection/reflection_class.puml"
generate_png "uml/reflection/reflection_state.puml"
generate_png "uml/reflection/reflection_sequence.puml"
generate_png "uml/rewoo/rewoo_class.puml"
generate_png "uml/rewoo/rewoo_state.puml"
generate_png "uml/rewoo/rewoo_sequence.puml"
generate_png "uml/reflection_and_refinement/reflection_and_refinement_class.puml"
generate_png "uml/reflection_and_refinement/reflection_and_refinement_state.puml"
generate_png "uml/reflection_and_refinement/reflection_and_refinement_sequence.puml"
generate_png "uml/plan_and_solve/plan_and_solve_class.puml"
generate_png "uml/plan_and_solve/plan_and_solve_state.puml"
generate_png "uml/plan_and_solve/plan_and_solve_sequence.puml"
generate_png "uml/storm/storm_class.puml"
generate_png "uml/storm/storm_state.puml"
generate_png "uml/storm/storm_sequence.puml"

echo "Done generating PNG diagrams."