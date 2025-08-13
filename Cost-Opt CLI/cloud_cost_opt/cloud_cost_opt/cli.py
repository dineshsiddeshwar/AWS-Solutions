import click
from .services import list_services
from .recommend import get_recommendation, save_to_csv
import importlib.util
import os

@click.group()
def cli():
        """Cloud Cost Optimization CLI

        Available commands:
            list         List available cost optimization services
            recommend    Get cost recommendation for a service
        """
        pass

@cli.command()
def list():
    """List available cost optimization services."""
    services = list_services()
    name_col = "Service Name"
    desc_col = "Description"
    name_width = max(len(name_col), max(len(svc['name']) for svc in services))
    desc_width = max(len(desc_col), max(len(svc['description']) for svc in services))
    print(f"{name_col:<{name_width}} | {desc_col:<{desc_width}}")
    print("-" * (name_width + desc_width + 3))
    for svc in services:
        print(f"{svc['name']:<{name_width}} | {svc['description']:<{desc_width}}")
    print()
    print("To get recommendations for a service, use: cost-opt recommend <service>")
    print("Example: cost-opt recommend ec2")

@cli.command()
@click.argument('service')
def recommend(service):
    """List cost recommendations for a service."""
    recs = get_recommendation(service)
    if not recs:
        print(f"No recommendations available for {service}.")
        return
    print(f"Recommendations for {service}:")
    for i, rec in enumerate(recs, 1):
        print(f"{i}. {rec}")
    print("\nIMPORTANT: Before running remediation, tag any resource with Exception=yes if you want to exclude it from automated actions.")
    print("To remediate a recommendation, run: cost-opt remediate <service> <number>")
    print("Example: cost-opt remediate ec2 3 will select the 3rd recommendation for EC2 and prompt for remediation.")

@cli.command()
@click.argument('service')
@click.argument('index', type=int)
@click.option('--auto', is_flag=True, help='Run remediation without prompts (for web usage)')
def remediate(service, index, auto):
    """Select a recommendation and remediate or save to CSV."""
    recs = get_recommendation(service)
    if not recs:
        print(f"No recommendations available for {service}.")
        return
    idx = index - 1
    if idx < 0 or idx >= len(recs):
        print(f"Invalid recommendation number. Please choose between 1 and {len(recs)}.")
        return
    selected = recs[idx]
    print(f"Selected recommendation for {service}:")
    print(f"{index}. {selected}")
    folder = service.upper()
    script_name = f"{service.lower()}_{index}_remediation.py"
    script_path = os.path.join(os.path.dirname(__file__), "Remediators", folder, script_name)
    script_path = os.path.abspath(script_path)
    if os.path.exists(script_path):
        spec = importlib.util.spec_from_file_location("remediate_module", script_path)
        remediate_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(remediate_module)
        if hasattr(remediate_module, "list_actions"):
            remediate_module.list_actions()
            if not auto:
                priv = input("Do you have right privileges to do above activities? yes/no: ").strip().lower()
                if priv == "yes":
                    pass
                elif priv == "no":
                    save_to_csv(service, selected)
                    print("Recommendation saved to CSV. Exiting.")
                    return
                else:
                    print("Wrong key entered. Exiting.")
                    return
        if hasattr(remediate_module, "remediate"):
            remediate_module.remediate()
        else:
            print("Remediation function not found in script.")
    else:
        print(f"Remediation script not found: {script_path}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) == 1:
        # No arguments provided, show help
        click.echo(cli.get_help(click.Context(cli)))
    else:
        cli()
