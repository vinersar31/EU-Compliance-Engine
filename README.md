# EU-Compliance-Engine

An automated compliance agent for the EU AI Act (Regulation (EU) 2024/1689).

This project helps evaluate AI systems and software projects to determine if they classify as "Prohibited", "High-Risk" (under Annex III), or have other obligations, based on the EU AI Act standards. It automatically generates a "Conformity Assessment Report" in Markdown format.

## Project Structure

*   `eu_compliance_engine/`: The main package.
    *   `compliance_engine.py`: Contains the `ComplianceEngine` core logic for evaluating systems against the EU AI Act rules.
    *   `agent_tool.py`: Exposes a tool interface (using Pydantic schemas) suitable for integration with agentic systems via function calling.
    *   `cli.py`: A command-line script for testing the engine with a sample definition.
*   `tests/`: Unit tests.
*   `docs/`: Contains reference material, such as `EU_AI_ACT_CORE.md`.

## Integration with Agentic Systems

The `agent_tool.py` module exposes a function, `generate_compliance_report`, along with Pydantic schemas `AISystemDefinition` and `GPAIInfo`. This makes it straightforward for LLMs and agent frameworks to format their output correctly and call the compliance engine.

## Requirements

*   Python 3.10+
*   `pydantic`

Install dependencies with:

```bash
pip install -r requirements.txt
```

## Running the CLI Example

You can test the engine using the provided CLI example:

```bash
python -m eu_compliance_engine.cli
```

## Running Tests

Run the unit test suite with:

```bash
python -m unittest discover tests
```
