import os
import json
import yaml

def build_matrix():
    print("Scanning system architecture...")
    matrix = {
        "project": "PayloadGuard",
        "verification_gates": ["C1", "C2", "C3", "C4", "C5", "C6"],
        "modules": []
    }

    # Scan the evidence directory for components
    if os.path.exists("evidence"):
        for f in os.listdir("evidence"):
            if f.endswith(".py"):
                matrix["modules"].append({
                    "component": f,
                    "status": "linked",
                    "type": "logic_core"
                })

    # Save the blueprint artifact
    with open("traceability_matrix.json", "w") as f:
        json.dump(matrix, f, indent=4)
    print("✅ Blueprint generated: traceability_matrix.json")

if __name__ == "__main__":
    build_matrix()
