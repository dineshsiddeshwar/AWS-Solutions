import argparse
import os
import sys
import pandas as pd
import subprocess
import re

# Mermaid node shape mapping
SHAPE_SYNTAX = {
    'rectangle': '["{label}"]',
    'round': '("{label}")',
    'stadium': '(["{label}"])',
    'subroutine': '[["{label}"]]',
    'cylinder': '[("{label}")]',
    'circle': '(("{label}"))',
    'doublecircle': '((("{label}")))',
    'asymmetric': '>{label}]',
    'rhombus': '{{"{label}"}}',
    'hexagon': '{{{{"{label}"}}}}',
    'parallelogram': '[/"{label}"/]',
    'parallelogram_alt': '[\\"{label}"\\]',
    'trapezoid': '[/"{label}"\\]',
    'trapezoid_alt': '[\\"{label}"/]',
}

def validate_excel(input_path):
    try:
        xls = pd.ExcelFile(input_path)
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        sys.exit(1)
    if len(xls.sheet_names) < 2:
        print("Excel file must have at least two sheets: Sheet1 (Nodes), Sheet2 (Connections)")
        sys.exit(2)
    nodes_df = pd.read_excel(xls, sheet_name=0)
    conns_df = pd.read_excel(xls, sheet_name=1)
    # Validate columns
    if "Node Name" not in nodes_df.columns:
        print(f"Missing column in Sheet1: Node Name")
        sys.exit(3)
    # Cluster column is optional
    if "Cluster" not in nodes_df.columns:
        nodes_df["Cluster"] = None
    # Parent Cluster column is optional
    if "Parent Cluster" not in nodes_df.columns:
        nodes_df["Parent Cluster"] = None
    # Remove Cluster Direction column handling
    for col in ["Source Node", "Target Node"]:
        if col not in conns_df.columns:
            print(f"Missing column in Sheet2: {col}")
            sys.exit(4)
    # Validate node references
    node_names = set(nodes_df["Node Name"].astype(str))
    for idx, row in conns_df.iterrows():
        if row["Source Node"] not in node_names or row["Target Node"] not in node_names:
            print(f"Invalid connection at row {idx+2}: Node not found in node list.")
            sys.exit(5)
    return nodes_df, conns_df

def get_node_shape(row):
    shape = str(row.get('Node Shape', 'rectangle')).lower()
    label = f"{row['Node Name']}"
    syntax = SHAPE_SYNTAX.get(shape, SHAPE_SYNTAX['rectangle'])
    return f"{str(row['Node Name']).replace(' ', '_')}{syntax.format(label=label)}"

def generate_mermaid(nodes_df, conns_df, direction=None):
    # Hardcode graph direction to TD
    lines = ["graph TD"]
    # Build cluster hierarchy
    clusters = nodes_df.groupby("Cluster")
    cluster_parents = {}
    for cluster, group in clusters:
        # Get parent cluster for this cluster
        parent = group["Parent Cluster"].dropna().iloc[0] if group["Parent Cluster"].dropna().any() else None
        cluster_parents[cluster] = parent
    # Helper to recursively write clusters
    def write_cluster(cluster, indent=1):
        group = clusters.get_group(cluster)
        lines.append("    " * indent + f"subgraph {cluster}")
        # Find child clusters
        child_clusters = [c for c, p in cluster_parents.items() if p == cluster]
        # Write child clusters first
        for child in child_clusters:
            write_cluster(child, indent+1)
        # Write nodes in this cluster that are not in child clusters
        child_nodes = set()
        for child in child_clusters:
            child_nodes.update(clusters.get_group(child)["Node Name"].tolist())
        for _, row in group.iterrows():
            if row["Node Name"] not in child_nodes:
                lines.append("    " * (indent+1) + get_node_shape(row))
        lines.append("    " * indent + "end")
    # Find top-level clusters (no parent)
    top_clusters = [c for c, p in cluster_parents.items() if pd.isna(p) or p == "" or p is None]
    # Write top-level clusters
    for cluster in top_clusters:
        write_cluster(cluster)
    # Add nodes with no cluster
    if None in clusters.groups or "" in clusters.groups:
        for cluster in [None, ""]:
            if cluster in clusters.groups:
                group = clusters.get_group(cluster)
                for _, row in group.iterrows():
                    lines.append(f"    {get_node_shape(row)}")
    # Connections
    for _, row in conns_df.iterrows():
        src = str(row["Source Node"]).replace(" ", "_")
        tgt = str(row["Target Node"]).replace(" ", "_")
        conn_type = row.get("Connection Type")
        arrow = "-->"  # Always use '-->'
        label = str(conn_type).strip() if pd.notna(conn_type) and str(conn_type).strip() else ""
        lines.append(build_edge(src, arrow, label, tgt))
    return "\n".join(lines)

def save_mermaid(mmd_code, mmd_path):
    with open(mmd_path, "w", encoding="utf-8") as f:
        f.write(mmd_code)

def render_mermaid(mmd_path, output_path):
    try:
        # Set Puppeteer Chrome path for Mermaid CLI
        os.environ["PUPPETEER_EXECUTABLE_PATH"] = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        subprocess.run([
            "mmdc", "-i", mmd_path, "-o", output_path
        ], check=True, shell=True)
    except Exception as ex:
        print(f"Error: {ex}")
        sys.exit(6)
    except subprocess.CalledProcessError as e:
        print(f"Mermaid CLI rendering failed: {e}")
        sys.exit(7)

def build_edge(src, arrow, label, tgt):
    # Only allow labels on directed arrows ('-->', '---', 'o-->'), not on '--' or '<-->'
    directed_arrows = ["-->", "---", "o-->"]
    arrow_stripped = arrow.replace(' ', '')
    if label and arrow_stripped in directed_arrows:
        return f"    {src} {arrow}|{label}| {tgt}"
    else:
        return f"    {src} {arrow} {tgt}"

def main():
    parser = argparse.ArgumentParser(description="Generate architecture diagram from Excel using Mermaid.")
    parser.add_argument("--input", required=True, help="Path to Excel input file.")
    parser.add_argument("--output", required=True, help="Path to output image file (PNG, SVG, etc.)")
    args = parser.parse_args()
    if not os.path.isfile(args.input):
        print(f"Input file not found: {args.input}")
        sys.exit(8)
    nodes_df, conns_df = validate_excel(args.input)
    mmd_code = generate_mermaid(nodes_df, conns_df)
    mmd_path = os.path.splitext(args.output)[0] + ".mmd"
    save_mermaid(mmd_code, mmd_path)
    render_mermaid(mmd_path, args.output)
    if os.path.exists(mmd_path):
        os.remove(mmd_path)
    print(f"Diagram generated: {args.output}")

if __name__ == "__main__":
    main() 