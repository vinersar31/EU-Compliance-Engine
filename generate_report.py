import json
import sys
from compliance_engine import ComplianceEngine

def main():
    # Provide a sample AI system definition to generate a report
    sample_system = {
        "name": "HR Resume Screening Assistant",
        "description": "An AI system that evaluates candidate resumes for job matching and ranks them.",
        "categories": ["employment_hr"],
        "features": ["profiling"],
        "exceptions": ["improves_human_activity"],
        "gpai": {
            "is_gpai": False
        }
    }

    if len(sys.argv) > 1:
        # Load from file if provided
        filepath = sys.argv[1]
        try:
            with open(filepath, 'r') as f:
                sample_system = json.load(f)
        except Exception as e:
            print(f"Error loading {filepath}: {e}")
            sys.exit(1)

    engine = ComplianceEngine(sample_system)
    report = engine.generate_report()

    print(report)

if __name__ == "__main__":
    main()
