"""
Claude AI Service
Handles interactions with Anthropic's Claude API for LCA analysis
"""
import os
from typing import List, Dict, Any
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv('../.env')

class ClaudeService:
    """Service class for Claude AI interactions"""

    def __init__(self):
        self.api_key = os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
        self.client = Anthropic(api_key=self.api_key)
        self.model = "claude-sonnet-4-20250514"  # Latest Sonnet model

    def analyze_process_impact(
        self,
        process_data: Dict[str, Any],
        analysis_type: str = "environmental_impact"
    ) -> Dict[str, Any]:
        """
        Analyze a single process using Claude AI

        Args:
            process_data: Process information from OpenLCA
            analysis_type: Type of analysis to perform

        Returns:
            AI-generated analysis
        """
        prompt = self._build_analysis_prompt(process_data, analysis_type)

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=2048,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            analysis_text = message.content[0].text

            return {
                "process_id": process_data.get("id"),
                "process_name": process_data.get("name"),
                "analysis_type": analysis_type,
                "analysis": analysis_text,
                "model": self.model
            }
        except Exception as e:
            raise Exception(f"Failed to analyze process with Claude: {str(e)}")

    def compare_processes(
        self,
        processes_data: List[Dict[str, Any]],
        comparison_criteria: str = "environmental_impact"
    ) -> Dict[str, Any]:
        """
        Compare multiple processes using Claude AI

        Args:
            processes_data: List of process information from OpenLCA
            comparison_criteria: What to compare (e.g., environmental_impact, cost, efficiency)

        Returns:
            AI-generated comparison analysis
        """
        prompt = self._build_comparison_prompt(processes_data, comparison_criteria)

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=3072,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            comparison_text = message.content[0].text

            return {
                "process_count": len(processes_data),
                "process_names": [p.get("name") for p in processes_data],
                "comparison_criteria": comparison_criteria,
                "comparison": comparison_text,
                "model": self.model
            }
        except Exception as e:
            raise Exception(f"Failed to compare processes with Claude: {str(e)}")

    def get_recommendations(
        self,
        process_data: Dict[str, Any],
        goal: str = "reduce_environmental_impact"
    ) -> Dict[str, Any]:
        """
        Get AI recommendations for improving a process

        Args:
            process_data: Process information from OpenLCA
            goal: Optimization goal

        Returns:
            AI-generated recommendations
        """
        prompt = self._build_recommendation_prompt(process_data, goal)

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=2048,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            recommendations_text = message.content[0].text

            return {
                "process_id": process_data.get("id"),
                "process_name": process_data.get("name"),
                "goal": goal,
                "recommendations": recommendations_text,
                "model": self.model
            }
        except Exception as e:
            raise Exception(f"Failed to get recommendations from Claude: {str(e)}")

    def _build_analysis_prompt(
        self,
        process_data: Dict[str, Any],
        analysis_type: str
    ) -> str:
        """Build prompt for process analysis"""
        process_name = process_data.get("name", "Unknown")
        description = process_data.get("description", "No description available")
        category = process_data.get("category", "Uncategorized")
        location = process_data.get("location", "Unknown location")

        exchanges_info = ""
        if "exchanges" in process_data and process_data["exchanges"]:
            exchanges_info = "\n\nKey Inputs/Outputs:\n"
            for exchange in process_data["exchanges"][:5]:
                flow_type = "Input" if exchange.get("is_input") else "Output"
                exchanges_info += f"- {flow_type}: {exchange.get('flow_name')} ({exchange.get('amount')} {exchange.get('unit')})\n"

        prompt = f"""You are an expert in Life Cycle Assessment (LCA) and environmental impact analysis.

Analyze the following industrial process:

Process Name: {process_name}
Category: {category}
Location: {location}
Description: {description}
{exchanges_info}

Analysis Type: {analysis_type}

Please provide a comprehensive analysis that includes:
1. Environmental Impact Assessment: Key environmental concerns and impacts
2. Resource Usage: Analysis of inputs and resource consumption
3. Emissions & Outputs: Notable emissions and outputs of concern
4. Sustainability Rating: Overall sustainability assessment
5. Key Findings: Main takeaways and areas of concern

Be specific, technical, and provide actionable insights."""

        return prompt

    def _build_comparison_prompt(
        self,
        processes_data: List[Dict[str, Any]],
        comparison_criteria: str
    ) -> str:
        """Build prompt for comparing processes"""
        processes_summary = ""
        for i, process in enumerate(processes_data, 1):
            processes_summary += f"\n{i}. {process.get('name', 'Unknown')}"
            processes_summary += f"\n   Category: {process.get('category', 'N/A')}"
            processes_summary += f"\n   Description: {process.get('description', 'N/A')[:100]}..."

            if "exchanges" in process and process["exchanges"]:
                processes_summary += f"\n   Key exchanges: {len(process['exchanges'])} flows"

        prompt = f"""You are an expert in Life Cycle Assessment (LCA) and environmental impact analysis.

Compare the following industrial processes based on {comparison_criteria}:
{processes_summary}

Please provide a detailed comparison that includes:
1. Overview: Brief summary of each process
2. Environmental Impact Comparison: Relative environmental impacts
3. Resource Efficiency: Which process is more resource-efficient
4. Trade-offs: Key trade-offs between the processes
5. Recommendation: Which process is preferable and under what conditions
6. Summary Table: Create a comparison table with key metrics

Be specific and provide a data-driven comparison."""

        return prompt

    def _build_recommendation_prompt(
        self,
        process_data: Dict[str, Any],
        goal: str
    ) -> str:
        """Build prompt for getting recommendations"""
        process_name = process_data.get("name", "Unknown")
        description = process_data.get("description", "No description available")

        exchanges_info = ""
        if "exchanges" in process_data and process_data["exchanges"]:
            exchanges_info = "\n\nCurrent Inputs/Outputs:\n"
            for exchange in process_data["exchanges"][:8]:
                flow_type = "Input" if exchange.get("is_input") else "Output"
                exchanges_info += f"- {flow_type}: {exchange.get('flow_name')} ({exchange.get('amount')} {exchange.get('unit')})\n"

        prompt = f"""You are an expert in Life Cycle Assessment (LCA) and sustainable process optimization.

Process: {process_name}
Description: {description}
{exchanges_info}

Goal: {goal}

Please provide actionable recommendations to achieve this goal:
1. Immediate Actions: Quick wins that can be implemented now
2. Material Substitutions: Alternative materials or inputs to consider
3. Process Improvements: Changes to the process flow or methodology
4. Technology Upgrades: Relevant technologies or innovations
5. Best Practices: Industry best practices for this type of process
6. Expected Impact: Estimated impact of implementing these recommendations

Be practical, specific, and prioritize recommendations by potential impact."""

        return prompt


# Singleton instance
_claude_service_instance = None

def get_claude_service() -> ClaudeService:
    """Get singleton instance of ClaudeService"""
    global _claude_service_instance
    if _claude_service_instance is None:
        _claude_service_instance = ClaudeService()
    return _claude_service_instance
