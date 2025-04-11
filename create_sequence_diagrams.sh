#!/bin/bash

# Create simplified sequence diagrams for all patterns
# and generate PNG files

# Self Discovery
cat > uml/self_discovery/self_discovery_sequence_simplified.puml << 'EOF'
@startuml
actor User
participant SelfDiscoveryAgent
participant LLM
participant Tools

User -> SelfDiscoveryAgent: run(input)
activate SelfDiscoveryAgent

SelfDiscoveryAgent -> LLM: discover capabilities
activate LLM
LLM --> SelfDiscoveryAgent: capabilities
deactivate LLM

loop until complete
  SelfDiscoveryAgent -> LLM: get next action
  activate LLM
  LLM --> SelfDiscoveryAgent: action
  deactivate LLM
  
  alt use tool
    SelfDiscoveryAgent -> Tools: execute tool
    activate Tools
    Tools --> SelfDiscoveryAgent: result
    deactivate Tools
  else final answer
    SelfDiscoveryAgent -> SelfDiscoveryAgent: prepare answer
  end
end

SelfDiscoveryAgent --> User: final result
deactivate SelfDiscoveryAgent
@enduml
EOF

# LATS
cat > uml/lats/lats_sequence_simplified.puml << 'EOF'
@startuml
actor User
participant LATSAgent
participant LLM
participant Tools
participant Tracing

User -> LATSAgent: run(input)
activate LATSAgent

LATSAgent -> Tracing: start trace
activate Tracing

loop until complete
  LATSAgent -> Tracing: record step start
  LATSAgent -> LLM: get next action
  activate LLM
  LLM --> LATSAgent: action
  deactivate LLM
  LATSAgent -> Tracing: record step end
  
  alt use tool
    LATSAgent -> Tracing: record tool start
    LATSAgent -> Tools: execute tool
    activate Tools
    Tools --> LATSAgent: result
    deactivate Tools
    LATSAgent -> Tracing: record tool end
  else final answer
    LATSAgent -> Tracing: record final answer
  end
end

LATSAgent -> Tracing: end trace
Tracing --> LATSAgent: trace summary
deactivate Tracing

LATSAgent --> User: final result
deactivate LATSAgent
@enduml
EOF

# Reflection
cat > uml/reflection/reflection_sequence_simplified.puml << 'EOF'
@startuml
actor User
participant ReflectionAgent
participant LLM
participant ReflectionLLM
participant Tools

User -> ReflectionAgent: run(input)
activate ReflectionAgent

loop until complete
  ReflectionAgent -> LLM: get next action
  activate LLM
  LLM --> ReflectionAgent: action
  deactivate LLM
  
  alt use tool
    ReflectionAgent -> Tools: execute tool
    activate Tools
    Tools --> ReflectionAgent: result
    deactivate Tools
  else final answer
    ReflectionAgent -> ReflectionAgent: prepare answer
  end
  
  opt reflection frequency reached
    ReflectionAgent -> ReflectionLLM: generate reflection
    activate ReflectionLLM
    ReflectionLLM --> ReflectionAgent: reflection
    deactivate ReflectionLLM
  end
end

ReflectionAgent --> User: final result
deactivate ReflectionAgent
@enduml
EOF

# ReWOO
cat > uml/rewoo/rewoo_sequence_simplified.puml << 'EOF'
@startuml
actor User
participant ReWOOAgent
participant ReasonLLM
participant WorldLLM
participant ObserveLLM
participant OutcomeLLM

User -> ReWOOAgent: run(input)
activate ReWOOAgent

loop until complete
  ReWOOAgent -> ReasonLLM: reason about action
  activate ReasonLLM
  ReasonLLM --> ReWOOAgent: reasoning
  deactivate ReasonLLM
  
  ReWOOAgent -> WorldLLM: simulate world
  activate WorldLLM
  WorldLLM --> ReWOOAgent: world state
  deactivate WorldLLM
  
  ReWOOAgent -> ObserveLLM: observe effects
  activate ObserveLLM
  ObserveLLM --> ReWOOAgent: observation
  deactivate ObserveLLM
  
  ReWOOAgent -> OutcomeLLM: determine outcome
  activate OutcomeLLM
  OutcomeLLM --> ReWOOAgent: outcome
  deactivate OutcomeLLM
end

ReWOOAgent --> User: final result
deactivate ReWOOAgent
@enduml
EOF

# Reflection and Refinement
cat > uml/reflection_and_refinement/reflection_and_refinement_sequence_simplified.puml << 'EOF'
@startuml
actor User
participant ReflectionAndRefinementAgent
participant LLM
participant ReflectionLLM
participant RefinementLLM
participant Tools

User -> ReflectionAndRefinementAgent: run(input)
activate ReflectionAndRefinementAgent

loop until complete
  ReflectionAndRefinementAgent -> LLM: get next action
  activate LLM
  LLM --> ReflectionAndRefinementAgent: action
  deactivate LLM
  
  alt use tool
    ReflectionAndRefinementAgent -> Tools: execute tool
    activate Tools
    Tools --> ReflectionAndRefinementAgent: result
    deactivate Tools
  else final answer
    ReflectionAndRefinementAgent -> ReflectionAndRefinementAgent: prepare answer
  end
  
  opt reflection phase triggered
    ReflectionAndRefinementAgent -> ReflectionLLM: generate reflection
    activate ReflectionLLM
    ReflectionLLM --> ReflectionAndRefinementAgent: reflection
    deactivate ReflectionLLM
    
    ReflectionAndRefinementAgent -> RefinementLLM: generate refinement
    activate RefinementLLM
    RefinementLLM --> ReflectionAndRefinementAgent: refinement
    deactivate RefinementLLM
  end
end

ReflectionAndRefinementAgent --> User: final result
deactivate ReflectionAndRefinementAgent
@enduml
EOF

# Plan and Solve
cat > uml/plan_and_solve/plan_and_solve_sequence_simplified.puml << 'EOF'
@startuml
actor User
participant PlanAndSolveAgent
participant PlannerLLM
participant SolverLLM
participant Tools

User -> PlanAndSolveAgent: run(input)
activate PlanAndSolveAgent

PlanAndSolveAgent -> PlannerLLM: create plan
activate PlannerLLM
PlannerLLM --> PlanAndSolveAgent: plan
deactivate PlannerLLM

loop through steps
  PlanAndSolveAgent -> SolverLLM: execute step
  activate SolverLLM
  SolverLLM --> PlanAndSolveAgent: solution
  deactivate SolverLLM
  
  opt tool needed
    PlanAndSolveAgent -> Tools: use tool
    activate Tools
    Tools --> PlanAndSolveAgent: result
    deactivate Tools
  end
  
  opt step failed
    PlanAndSolveAgent -> PlannerLLM: revise plan
    activate PlannerLLM
    PlannerLLM --> PlanAndSolveAgent: revised plan
    deactivate PlannerLLM
  end
end

PlanAndSolveAgent -> SolverLLM: create final answer
activate SolverLLM
SolverLLM --> PlanAndSolveAgent: final answer
deactivate SolverLLM

PlanAndSolveAgent --> User: final result
deactivate PlanAndSolveAgent
@enduml
EOF

# STORM
cat > uml/storm/storm_sequence_simplified.puml << 'EOF'
@startuml
actor User
participant STORMAgent
participant EvaluatorLLM
participant OptionsLLM
participant ReasonerLLM
participant MistakeLLM
participant Tools

User -> STORMAgent: run(input)
activate STORMAgent

loop until complete
  STORMAgent -> EvaluatorLLM: self-evaluate
  activate EvaluatorLLM
  EvaluatorLLM --> STORMAgent: evaluation
  deactivate EvaluatorLLM
  
  STORMAgent -> OptionsLLM: generate options
  activate OptionsLLM
  OptionsLLM --> STORMAgent: options
  deactivate OptionsLLM
  
  STORMAgent -> ReasonerLLM: reason through options
  activate ReasonerLLM
  ReasonerLLM --> STORMAgent: reasoning
  deactivate ReasonerLLM
  
  STORMAgent -> MistakeLLM: detect mistakes
  activate MistakeLLM
  MistakeLLM --> STORMAgent: mistakes
  deactivate MistakeLLM
  
  alt tool action chosen
    STORMAgent -> Tools: execute tool
    activate Tools
    Tools --> STORMAgent: result
    deactivate Tools
  else final answer
    STORMAgent -> STORMAgent: prepare answer
  end
end

STORMAgent --> User: final result
deactivate STORMAgent
@enduml
EOF

# Generate PNGs
echo "Generating PNGs for sequence diagrams..."

curl -s -X POST --data-binary @uml/self_discovery/self_discovery_sequence_simplified.puml http://localhost:8000/plantuml/png > uml/self_discovery/png/self_discovery_sequence.png

curl -s -X POST --data-binary @uml/lats/lats_sequence_simplified.puml http://localhost:8000/plantuml/png > uml/lats/png/lats_sequence.png

curl -s -X POST --data-binary @uml/reflection/reflection_sequence_simplified.puml http://localhost:8000/plantuml/png > uml/reflection/png/reflection_sequence.png

curl -s -X POST --data-binary @uml/rewoo/rewoo_sequence_simplified.puml http://localhost:8000/plantuml/png > uml/rewoo/png/rewoo_sequence.png

curl -s -X POST --data-binary @uml/reflection_and_refinement/reflection_and_refinement_sequence_simplified.puml http://localhost:8000/plantuml/png > uml/reflection_and_refinement/png/reflection_and_refinement_sequence.png

curl -s -X POST --data-binary @uml/plan_and_solve/plan_and_solve_sequence_simplified.puml http://localhost:8000/plantuml/png > uml/plan_and_solve/png/plan_and_solve_sequence.png

curl -s -X POST --data-binary @uml/storm/storm_sequence_simplified.puml http://localhost:8000/plantuml/png > uml/storm/png/storm_sequence.png

echo "Done creating sequence diagrams and PNGs."