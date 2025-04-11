# Patterns API Reference

This document provides detailed API reference for the agent patterns in Agent Patterns.

## ReActAgent

::: agent_patterns.patterns.re_act_agent.ReActAgent
    handler: python
    selection:
      members:
        - __init__
        - build_graph
        - start_node
        - thinking_node
        - action_node
        - observation_node
        - final_node
        - should_continue

## ReflexionAgent

::: agent_patterns.patterns.reflexion_agent.ReflexionAgent
    handler: python
    selection:
      members:
        - __init__
        - build_graph
        - start_node
        - thinking_node
        - action_node
        - observation_node
        - reflection_node
        - plan_node
        - final_node
        - should_reflect
        - should_continue

## PlanAndSolveAgent

::: agent_patterns.patterns.plan_and_solve_agent.PlanAndSolveAgent
    handler: python
    selection:
      members:
        - __init__
        - build_graph
        - get_plan_node
        - execute_plan_node
        - finalize_response_node

## ReflectionAgent

::: agent_patterns.patterns.reflection_agent.ReflectionAgent
    handler: python
    selection:
      members:
        - __init__
        - build_graph
        - thinking_node
        - reflection_node
        - final_node
        - should_reflect

## ReflectionAndRefinementAgent

::: agent_patterns.patterns.reflection_and_refinement_agent.ReflectionAndRefinementAgent
    handler: python
    selection:
      members:
        - __init__
        - build_graph
        - start_node
        - thinking_node
        - reflection_node
        - refinement_node
        - final_node
        - should_refine

## LLMCompilerAgent

::: agent_patterns.patterns.llm_compiler_agent.LLMCompilerAgent
    handler: python
    selection:
      members:
        - __init__
        - build_graph
        - plan_node
        - execute_node
        - refine_node
        - final_node
        - should_refine

## ReWOOAgent

::: agent_patterns.patterns.rewoo_agent.REWOOAgent
    handler: python
    selection:
      members:
        - __init__
        - build_graph
        - run
        - stream
        - _plan_steps
        - _execute_step
        - _check_completion
        - _format_final_answer
        - _should_continue_execution

## LATSAgent

::: agent_patterns.patterns.lats_agent.LATSAgent
    handler: python
    selection:
      members:
        - __init__
        - build_graph
        - start_node
        - thinking_node
        - action_node
        - observation_node
        - trace_node
        - final_node
        - get_trace
        - should_continue

## STORMAgent

::: agent_patterns.patterns.storm_agent.STORMAgent
    handler: python
    selection:
      members:
        - __init__
        - build_graph
        - run
        - stream
        - _generate_initial_outline
        - _identify_perspectives
        - _simulate_conversations
        - _refine_outline
        - _write_sections
        - _finalize_article

## SelfDiscoveryAgent

::: agent_patterns.patterns.self_discovery_agent.SelfDiscoveryAgent
    handler: python
    selection:
      members:
        - __init__
        - build_graph
        - start_node
        - discover_node
        - plan_node
        - execute_node
        - learn_node
        - final_node
        - should_discover

## Agent Factory Functions

::: agent_patterns.patterns.factory.create_reflection_and_refinement_agent
    handler: python

::: agent_patterns.patterns.factory.create_plan_and_solve_agent
    handler: python

::: agent_patterns.patterns.factory.create_react_agent
    handler: python

::: agent_patterns.patterns.factory.create_reflection_agent
    handler: python