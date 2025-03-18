# Linting


## Description

[Linter GitHub Actions workflow](/.github/workflows/linter.yml) validates the syntax and format of the most common
languages, either programming or declarative, used in the repository. Each language is configurable with the set of
rules and exceptions agreed within the team. Feel free to browse the [linter configuration files](/.github/linters/).

The following languages have been enabled:

- JSON format and syntax.
- Markdown (GitHub `.md`) format.
- Natural language.
- Python format and syntax according to [PEP8 style guide](https://peps.python.org/pep-0008/).
- Terraform (HCL2) format and syntax.
- CloudFormation templates schema validation, syntax, references, and best practices.

Note linter will highlight mostly style (cosmetic) misalignments with agreed guidelines. However, it does not
validate the code functionality, or even semantics. The objective is to produce standard code, with no personal
nuances if possible, which ultimately helps each other to contribute to code never seen before.

Visit [ECP Development Standardisation - Linting and formatting](https://github.com/sede-x/ecp-development-standardisation/blob/main/coding/linting_formatting.md)
to find how to get started using linting tools in VS Code. Do not wait until code gets the Pull Request phase to
produce clean and beautiful code.


## To-Do list of tasks

1. Solve or ignore JSON errors. Most, if not all, errors are caused by duplicated keys. Although, duplicated keys
   are not disallowed in JSON specification, the strong recommendation is to avoid them. Think of a JSON file as
   a map or as a serialization of an object where attributes must be unique. Revisit why there are duplicated keys,
   and whether it makes sense or not.

2. Solve or ignore Markdown errors. There are no errors because current
   [configuration](/.github/linters/markdown-lint.yml) is quite relax.

3. Solve or ignore Python errors. Although [PEP8 style guide](https://peps.python.org/pep-0008/) limits the length
   of each line to 79 characters (including indentation), this has been extended to 120 in the
   [flake8 configuration](/.github/linters/flake8). Lots of errors, especially the cosmetic ones, can be easily
   fixed with automatic tools like [autoflake](https://pypi.org/project/autoflake/) and
   [autopep8](https://pypi.org/project/autopep8/). Other more sensitive errors, like unused variables or modules,
   can be automatically fixed too, with extra care on the review. Fixing the rest of linting errors will be still a
   tedious piece of grunt work. This is the consequence of lacking a style manual for long time in a big and complex
   project. However, the amount of work should not be an excuse to get on with it.

4. Solve or ignore Terraform errors. The built-in [terraform fmt](https://developer.hashicorp.com/terraform/cli/commands/fmt)
   command in the command-line tool is good enough to solve all Terraform formatting problems within the repository.

5. Solve or ignore CloudFormation errors. Use [cfn-lint](https://github.com/aws-cloudformation/cfn-lint) command-line
   tool to validate the templates locally. Alternative, install the CloudFormation extension for Visual Studio  Code.

6. Finally, configure a branch protection rule on `develop` branch to ensure only properly linted files can reach
   the trunk branch and all code remains stylish. Pull Requests are a must to promote changes, avoiding direct changes
   to the `develop` branch. An additional protection needs to be added so that linter workflow must return a positive
   outcome before the Pull Request becomes mergeable. This is explained
   [here](https://github.com/sede-x/ecp-development-standardisation/blob/main/coding/linting_formatting.md#github-actions-checks).
