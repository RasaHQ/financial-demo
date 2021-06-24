"""Deletes all EKS test clusters prefixed with `financial-demo-`"""
import sys
import subprocess
import json
import pprint


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
    print(f"--\nDeleting EKS test cluster: {cluster}")
    cmd = [
        "eksctl",
        "delete",
        "cluster",
        "--name",
        cluster,
    ]

    try:
        subprocess.run(cmd, check=True, capture_output=False)

    except subprocess.CalledProcessError as e:
        print(e.stderr.decode("utf-8"))
        sys.exit(e.returncode)
