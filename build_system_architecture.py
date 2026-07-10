from diagrams import Diagram, Cluster, Edge
from diagrams.programming.language import Python
from diagrams.onprem.client import User
from diagrams.onprem.vcs import Github
from diagrams.generic.storage import Storage
from diagrams.generic.device import Tablet

# Mobile-friendly output path
output_path = "/data/data/com.termux/files/home/storage/shared/Download/payloadguard_blueprints/System_Architecture_Map"

graph_attr = {
    "fontsize": "20",
    "bgcolor": "white"
}

with Diagram("PayloadGuard System Pipeline", show=False, filename=output_path, graph_attr=graph_attr, direction="LR"):
    
    user = User("Author")

    with Cluster("Inputs (Source of Truth)"):
        sources = Storage("Source Docs\n(PDF/MD)")
        metadata = Storage("Metadata\n(YAML)")
        
    with Cluster("Verification Gates (The Engine)"):
        logic = Python("evidence/reconcile.py\n(Logic Core)")
        
        with Cluster("Gate Checks"):
            dafny = Python("Dafny\n(Formal Proof)")
            citations = Python("Citation\n(Verifier)")
            tests = Python("Pytest\n(Concrete)")

    with Cluster("Artifact Generation"):
        matrix_gen = Python("generate_matrix.py")
        output_json = Github("Traceability\nMatrix (JSON)")
        output_md = Tablet("Audit Report\n(Markdown)")

    # Data Flow Logic
    user >> Edge(label="Cites") >> metadata
    user >> Edge(label="Uploads") >> sources
    
    sources >> citations
    metadata >> logic
    
    logic >> dafny
    logic >> tests
    
    [dafny, citations, tests] >> matrix_gen
    matrix_gen >> output_json
    matrix_gen >> output_md
