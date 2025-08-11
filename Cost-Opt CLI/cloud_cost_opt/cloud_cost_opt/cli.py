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
    for svc in list_services():
        print(f"{svc['name']}  description: {svc['description']}")

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
    print("\nTo remediate a recommendation, run: cost-opt remediate <service> <number>")
    print("Example: cost-opt remediate ec2 3 will select the 3rd recommendation for EC2 and prompt for remediation.")

@cli.command()
@click.argument('service')
@click.argument('index', type=int)
def remediate(service, index):
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
    choice = input("Shall we proceed? yes/no: ").strip().lower()
    if choice == "yes":
        # Dynamically import and run the remediation script
        folder = service.upper()
        script_name = f"{service.lower()}_{index}_remediation.py"
        script_path = os.path.join(os.path.dirname(__file__), "..", "Remediators", folder, script_name)
        script_path = os.path.abspath(script_path)
        if os.path.exists(script_path):
            spec = importlib.util.spec_from_file_location("remediate_module", script_path)
            remediate_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(remediate_module)
            if hasattr(remediate_module, "list_actions"):
                remediate_module.list_actions()
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
    elif choice == "no":
        save_to_csv(service, selected)
        print("Recommendation saved to CSV. Exiting.")
    else:
        print("Wrong key entered. Exiting.")
        return

if __name__ == "__main__":
    import sys
    if len(sys.argv) == 1:
        # No arguments provided, show help
        click.echo(cli.get_help(click.Context(cli)))
    else:
        cli()
