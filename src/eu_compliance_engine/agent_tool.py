from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from eu_compliance_engine.compliance_engine import ComplianceEngine

class GPAIInfo(BaseModel):
    is_gpai: bool = Field(default=False, description="Whether the system is a General Purpose AI model")
    flops: Optional[float] = Field(default=None, description="The computational power used to train the model in FLOPS, if known")

class AISystemDefinition(BaseModel):
    name: str = Field(..., description="The name of the AI system")
    description: str = Field(..., description="A detailed description of the AI system's purpose and functionality")
    categories: List[str] = Field(default_factory=list, description="Categories the system falls into, e.g., 'biometrics', 'employment_hr', 'social_scoring'")
    features: List[str] = Field(default_factory=list, description="Features of the system, e.g., 'profiling', 'interaction_with_humans', 'generates_content'")
    exceptions: List[str] = Field(default_factory=list, description="Exceptions that might apply, e.g., 'narrow_procedural_task'")
    gpai: Optional[GPAIInfo] = Field(default=None, description="Information regarding whether this is a General Purpose AI (GPAI)")

def generate_compliance_report(system_definition: AISystemDefinition) -> str:
    """
    Evaluates an AI system against the EU AI Act (Regulation (EU) 2024/1689)
    and generates a Conformity Assessment Report in Markdown format.

    This function is designed to be used as a tool by agentic systems.
    """
    sys_def_dict = system_definition.model_dump()
    if sys_def_dict.get("gpai") is None:
        sys_def_dict["gpai"] = {}

    engine = ComplianceEngine(sys_def_dict)
    return engine.generate_report()
