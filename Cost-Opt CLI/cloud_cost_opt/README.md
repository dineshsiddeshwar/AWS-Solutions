# Cloud Cost Optimization CLI

A Python package and CLI tool for cloud cost optimization.

## Usage

### List available services
```
cost-opt list
```

### List recommendations for a service
```
cost-opt recommend <service>
```
Example:
```
cost-opt recommend ec2
```

### Remediate a specific recommendation
```
cost-opt remediate <service> <number>
```
Example:
```
cost-opt remediate ec2 1
```
This will:
- Show the selected recommendation
- Ask "Shall we proceed? yes/no:"
	- If "yes", show actions and ask for privilege confirmation
	- If "no", save the recommendation to CSV and exit
- After listing actions, ask "Do you have right privileges to do above activities? yes/no:"
	- If "yes", run the remediation script
	- If "no", save the recommendation to CSV and exit
	- Any other key: exit with error

### Help
```
cost-opt --help
```
Shows all available commands and usage.
