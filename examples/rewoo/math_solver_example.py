"""
Math Problem Solver Example using the REWOO agent pattern.

This example demonstrates how to use the REWOO (Reasoning Without Observation) agent pattern
for solving complex math problems in a step-by-step manner.
"""

import os
import sys
import logging
import time
from typing import Dict, Any, List, Optional, Union, Tuple, ClassVar, Type
import re
import json
import numpy as np

# Add the src directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agent_patterns.rewoo.agent import REWOOAgent
from agent_patterns.rewoo.types import TaskDecompositionResponse
from agent_patterns.rewoo.tool_provider import ToolProvider
from agent_patterns.rewoo.solution_validator import SolutionValidator
from langchain_openai import ChatOpenAI

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CalculatorTool:
    """Calculator tool for performing mathematical operations."""
    
    def __call__(self, expression: str, **kwargs) -> str:
        """Evaluate a mathematical expression."""
        logger.info(f"Calculating: {expression}")
        
        # Clean the expression to make it safer to evaluate
        expression = expression.strip()
        
        # Only allow basic mathematical operations
        allowed_chars = set("0123456789+-*/()^. ")
        if not all(c in allowed_chars for c in expression):
            return "Error: Expression contains invalid characters."
        
        # Replace ^ with ** for exponentiation
        expression = expression.replace("^", "**")
        
        try:
            # Use safe eval (in a real implementation, use a proper expression evaluator)
            allowed_names = {"abs": abs, "round": round, "max": max, "min": min}
            result = eval(expression, {"__builtins__": {}}, allowed_names)
            
            # Format the result
            if isinstance(result, float):
                # Format to 5 decimal places if it's a float
                return str(round(result, 5))
            else:
                return str(result)
        except Exception as e:
            return f"Error evaluating expression: {str(e)}"


class EquationSolverTool:
    """Tool for solving algebraic equations."""
    
    def __call__(self, equation: str, variable: str = "x", **kwargs) -> str:
        """Solve an algebraic equation for the specified variable."""
        logger.info(f"Solving equation: {equation} for {variable}")
        
        # This is a simplified mock implementation
        
        # Simple linear equation: ax + b = c
        linear_pattern = r"(\d*\.?\d*)\s*{}\s*([+-]\s*\d*\.?\d*)\s*=\s*(\d*\.?\d*)".format(variable)
        linear_match = re.search(linear_pattern, equation)
        if linear_match:
            try:
                a = float(linear_match.group(1)) if linear_match.group(1) else 1
                b = float(linear_match.group(2).replace(" ", ""))
                c = float(linear_match.group(3))
                
                solution = (c - b) / a
                return f"{variable} = {solution}"
            except Exception:
                pass
                
        # Quadratic equation: ax^2 + bx + c = 0
        quadratic_pattern = r"(\d*\.?\d*)\s*{}\s*\^\s*2\s*([+-]\s*\d*\.?\d*)\s*{}\s*([+-]\s*\d*\.?\d*)\s*=\s*0".format(variable, variable)
        quadratic_match = re.search(quadratic_pattern, equation)
        if quadratic_match:
            try:
                a = float(quadratic_match.group(1)) if quadratic_match.group(1) else 1
                b = float(quadratic_match.group(2).replace(" ", ""))
                c = float(quadratic_match.group(3).replace(" ", ""))
                
                discriminant = b**2 - 4*a*c
                if discriminant < 0:
                    return "No real solutions"
                elif discriminant == 0:
                    solution = -b / (2*a)
                    return f"{variable} = {solution}"
                else:
                    solution1 = (-b + discriminant**0.5) / (2*a)
                    solution2 = (-b - discriminant**0.5) / (2*a)
                    return f"{variable} = {solution1} or {variable} = {solution2}"
            except Exception:
                pass
        
        # For more complex equations, return a mock result
        if "sin" in equation or "cos" in equation or "tan" in equation:
            return "Trigonometric equation detected. Solution depends on the domain."
        elif "log" in equation or "ln" in equation:
            return "Logarithmic equation detected. Solution requires numerical methods."
        
        return "Could not solve the equation with the current implementation."


class DerivativeTool:
    """Tool for calculating derivatives of mathematical expressions."""
    
    def __call__(self, expression: str, variable: str = "x", **kwargs) -> str:
        """Calculate the derivative of an expression with respect to a variable."""
        logger.info(f"Calculating derivative of {expression} with respect to {variable}")
        
        # Mock implementation with hard-coded results for common expressions
        expression = expression.replace(" ", "").lower()
        
        if expression == "x^2":
            return "2x"
        elif expression == "x^3":
            return "3x^2"
        elif expression == "x^n" or f"{variable}^n":
            return f"n*{variable}^(n-1)"
        elif expression == "sin(x)" or expression == f"sin({variable})":
            return f"cos({variable})"
        elif expression == "cos(x)" or expression == f"cos({variable})":
            return f"-sin({variable})"
        elif expression == "e^x" or expression == f"e^{variable}":
            return f"e^{variable}"
        elif expression == "ln(x)" or expression == f"ln({variable})":
            return f"1/{variable}"
        
        # Try to handle simple polynomial expressions
        if "^" in expression and variable in expression:
            # Try to match patterns like ax^n
            pattern = r"(\d*\.?\d*)\s*{}\s*\^\s*(\d+)".format(re.escape(variable))
            match = re.search(pattern, expression)
            if match:
                coef = match.group(1)
                if coef == "":
                    coef = "1"
                power = int(match.group(2))
                if power == 0:
                    return "0"
                elif power == 1:
                    return coef
                new_coef = float(coef) * power
                new_power = power - 1
                if new_power == 0:
                    return str(new_coef)
                elif new_power == 1:
                    return f"{new_coef}{variable}"
                else:
                    return f"{new_coef}{variable}^{new_power}"
        
        return "Could not calculate the derivative with the current implementation."


class IntegralTool:
    """Tool for calculating integrals of mathematical expressions."""
    
    def __call__(self, expression: str, variable: str = "x", **kwargs) -> str:
        """Calculate the indefinite integral of an expression with respect to a variable."""
        logger.info(f"Calculating integral of {expression} with respect to {variable}")
        
        # Mock implementation with hard-coded results for common expressions
        expression = expression.replace(" ", "").lower()
        
        if expression == "x":
            return "x^2/2 + C"
        elif expression == "x^2":
            return "x^3/3 + C"
        elif expression == "x^3":
            return "x^4/4 + C"
        elif expression == "1/x":
            return f"ln|{variable}| + C"
        elif expression == "sin(x)" or expression == f"sin({variable})":
            return f"-cos({variable}) + C"
        elif expression == "cos(x)" or expression == f"cos({variable})":
            return f"sin({variable}) + C"
        elif expression == "e^x" or expression == f"e^{variable}":
            return f"e^{variable} + C"
        
        # Try to handle simple polynomial expressions
        if "^" in expression and variable in expression:
            # Try to match patterns like ax^n
            pattern = r"(\d*\.?\d*)\s*{}\s*\^\s*(\d+)".format(re.escape(variable))
            match = re.search(pattern, expression)
            if match:
                coef = match.group(1)
                if coef == "":
                    coef = "1"
                power = int(match.group(2))
                new_power = power + 1
                new_coef = float(coef) / new_power
                return f"{new_coef}{variable}^{new_power} + C"
        
        return "Could not calculate the integral with the current implementation."


class MatrixTool:
    """Tool for performing matrix operations."""
    
    def __call__(self, operation: str, matrix_a: str, matrix_b: str = None, **kwargs) -> str:
        """Perform matrix operations."""
        logger.info(f"Performing matrix operation: {operation}")
        
        # Mock implementation for matrix operations
        if operation.lower() == "determinant":
            # Simple 2x2 determinant
            if "[[" in matrix_a and "]]" in matrix_a:
                try:
                    # Extract numbers from the matrix string
                    numbers = re.findall(r'-?\d+\.?\d*', matrix_a)
                    if len(numbers) == 4:
                        a, b, c, d = map(float, numbers)
                        det = a * d - b * c
                        return str(det)
                except Exception:
                    pass
            return "Could not calculate determinant with the current implementation."
        
        elif operation.lower() == "inverse":
            # Simple 2x2 inverse
            if "[[" in matrix_a and "]]" in matrix_a:
                try:
                    # Extract numbers from the matrix string
                    numbers = re.findall(r'-?\d+\.?\d*', matrix_a)
                    if len(numbers) == 4:
                        a, b, c, d = map(float, numbers)
                        det = a * d - b * c
                        if det == 0:
                            return "Matrix is singular, inverse does not exist."
                        inv_a = d / det
                        inv_b = -b / det
                        inv_c = -c / det
                        inv_d = a / det
                        return f"[[{inv_a}, {inv_b}], [{inv_c}, {inv_d}]]"
                except Exception:
                    pass
            return "Could not calculate inverse with the current implementation."
        
        elif operation.lower() == "multiply" and matrix_b:
            return "Matrix multiplication not implemented in this mock tool."
        
        return "Unsupported matrix operation or invalid input."


def main():
    """Run the example."""
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Get the openai key from the environment
    openai_key = os.environ.get("OPENAI_API_KEY")
    if not openai_key:
        raise ValueError("OPENAI_API_KEY environment variable not set")
    
    # Define the prompt directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(os.path.dirname(script_dir))
    src_prompt_dir = os.path.join(repo_root, "src", "agent_patterns", "prompts")
    prompt_dir = os.path.join(repo_root, "agent_patterns", "prompts")
    
    # Use the src path if it exists, otherwise use the non-src path
    if os.path.exists(src_prompt_dir):
        prompt_dir = src_prompt_dir
    
    # Create real OpenAI LLMs
    planner_llm = ChatOpenAI(
        model="gpt-4o",
        temperature=0.7,
        api_key=openai_key
    )
    
    solver_llm = ChatOpenAI(
        model="gpt-4o",
        temperature=0.2,
        api_key=openai_key
    )
    
    # Create tools
    calculator_tool = CalculatorTool()
    equation_solver_tool = EquationSolverTool()
    derivative_tool = DerivativeTool()
    integral_tool = IntegralTool()
    matrix_tool = MatrixTool()
    
    # Create REWOO agent
    agent = REWOOAgent(
        llm_configs={
            "planner": planner_llm,
            "solver": solver_llm
        },
        tool_registry={
            "calculator": calculator_tool,
            "equation_solver": equation_solver_tool,
            "derivative": derivative_tool,
            "integral": integral_tool,
            "matrix": matrix_tool
        },
        prompt_dir=prompt_dir
    )
    
    # Run the agent
    query = "A movie theater sold adult tickets for $12 each and child tickets for $8 each. If the theater sold 250 tickets and collected $2,600 in revenue, how many of each type of ticket did they sell?"
    print(f"\nProblem: {query}\n")
    print("-" * 80)
    print("Starting REWOO agent execution...\n")
    
    start_time = time.time()
    result = agent.run(query)
    elapsed_time = time.time() - start_time
    
    print("\nSolution:")
    print("-" * 80)
    print(result)
    print("-" * 80)
    print(f"Execution completed in {elapsed_time:.2f} seconds.")


if __name__ == "__main__":
    main() 