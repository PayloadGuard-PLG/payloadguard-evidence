from diagrams import Diagram, Cluster, Edge
from diagrams.programming.language import Python
from diagrams.onprem.client import User
from diagrams.onprem.vcs import Github
from diagrams.generic.storage import Storage

# We save directly to the local repo so Git can track it
filename = "system_architecture_map"

graph_attr = {"fontsize": "20", "bgcolor": "white"}

with Diagram("PayloadGuard End-to-End Blueprint", show=False, filename=filename, graph_attr=graph_attr, direction="LR"):

    user = User("Operator")

    with Cluster("Phase 1: Inputs"):
        sources = Storage("Source Docs")
        metadata = Storage("Metadata.yaml")

    with Cluster("Phase 2: The Engine (Evidence)"):
        core = Python("reconcile.py")
        prover = Python("dafny_adapter.py")

    with Cluster("Phase 3: Artifacts"):
        matrix = Github("Traceability\nMatrix")

    # The Flow
    user >> sources >> core
    user >> metadata >> core
    core >> prover >> core
    core >> matrix
