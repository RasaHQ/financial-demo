"""Deletes all EKS test clusters prefixed with `financial-demo-`"""
import sys
import subprocess
import json
import pprint
from pathlib import Path

cwd = Path(__file__).parent.parent
print("--\ncwd={cwd}")

###################################
print("--\nGet the EKS test clusters for financial-demo")
cmd = [
    "eksctl",
    "get",
    "cluster",
    "--output",
    "json",
]

try:
    cp = subprocess.run(cmd, check=True, capture_output=True)

except subprocess.CalledProcessError as e:
    print(e.stderr.decode("utf-8"))
    sys.exit(e.returncode)

# all clusters
clusters = [x["metadata"]["name"] for x in json.loads(cp.stdout.decode("utf-8"))]

# financial-demo test clusters
clusters = [
    c
    for c in clusters
    if c.startswith("financial-demo-") and c != "financial-demo-production"
]

print(f"Found {len(clusters)} financial-demo test clusters")
if len(clusters) > 0:
    pprint.pprint(clusters)

###################################
for cluster in clusters:
    print(f"--\nCleaning up EKS test cluster: {cluster}")

    try:
        # Note: see http://www.gnu.org/software/automake/manual/html_node/Tricks-For-Silencing-Make.html
        print(f"----\nSet kubeconfig to look at this cluster")
        cmd = [
            "make",
            "--no-print-directory",
            "aws-eks-cluster-update-kubeconfig",
            f"AWS_EKS_CLUSTER_NAME={cluster}",
        ]
        subprocess.run(cmd, check=True, capture_output=False, cwd=cwd)

        print(f"----\nUninstall rasa enterprise")
        cmd = ["make", "--no-print-directory", "rasa-enterprise-uninstall"]
        subprocess.run(cmd, check=True, capture_output=False, cwd=cwd)

        print(f"----\nDelete Storage (PVCs)")
        cmd = ["make", "--no-print-directory", "rasa-enterprise-delete-pvc-all"]
        subprocess.run(cmd, check=True, capture_output=False, cwd=cwd)

        print(f"----\nDelete the EKS cluster")
        cmd = [
            "make",
            "--no-print-directory",
            "aws-eks-cluster-delete",
            f"AWS_EKS_CLUSTER_NAME={cluster}",
        ]
        subprocess.run(cmd, check=True, capture_output=False, cwd=cwd)

    except subprocess.CalledProcessError as e:
        print(e.stderr.decode("utf-8"))
        sys.exit(e.returncode)
