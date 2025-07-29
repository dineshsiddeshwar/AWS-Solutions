# Product Technical Specification Document: Python-Based Architecture Diagram Generator Using Mermaid

## 1. Introduction

This document details the technical design and implementation plan for a **Python command-line tool** that generates architecture diagrams from an Excel spreadsheet. The diagrams are expressed in Mermaid syntax and rendered to image files (e.g., PNG or SVG) using Mermaid CLI utilities.

## 2. System Overview

The system accepts an Excel file containing nodes and their connections as input, parses the data, converts it into valid Mermaid diagram code, and then renders the diagram into an image file saved at a user-specified location.

## 3. Architecture & Components

### 3.1 Input Processing

- **Excel Input Format:**
  - Sheet 1: Defines the **nodes** with attributes such as Node Name, Node Type, and optional properties.
  - Sheet 2: Defines **connections** between nodes specifying Source, Target, and optional Connection Type.
  
- **Parsing Library:**
  - `pandas` is used to read and process Excel sheets efficiently.

- **Data Validation:**
  - The tool verifies the presence of mandatory columns in both sheets.
  - Validates node names referenced in the connections sheet exist in the node list to avoid rendering errors.

### 3.2 Mermaid Diagram Code Generation

- Construct a Mermaid **directed graph (graph TD)** text representation:
  - Each node appears as a labeled box.
  - Connections are represented as arrows from source to target.
  - Optional handling for node attributes influencing label formatting or styling (extendable).

- Maintain a clean Mermaid code structure to ensure compatibility with Mermaid CLI rendering.

### 3.3 Diagram Rendering

- Uses **mermaid-cli** (Node.js-based) or **mermaid-cli-python** package to convert Mermaid `.mmd` files into image files.
- Supports output formats:
  - PNG
  - SVG
  - PDF (optional, requires validation)

- Rendering occurs post Mermaid code generation, ensuring visual accuracy.

## 4. Command-Line Interface (CLI)

- **Arguments:**
  - `--input` (str, required): Path to the Excel input file.
  - `--output` (str, required): Full file path (including filename and extension) to save the rendered diagram image.
  
- **Options:**
  - Future scope for flags such as diagram orientation, node grouping, verbosity level.

- **Execution Flow:**
  1. Parse CLI arguments.
  2. Load and validate Excel sheets.
  3. Generate Mermaid code.
  4. Save `.mmd` intermediary file.
  5. Render `.mmd` to specified image format.
  6. Save and confirm output.

## 5. Data Model

| Entity     | Description                                 | Key Attributes                    |
|------------|---------------------------------------------|---------------------------------|
| Node       | Represents a system component in architecture | Node Name (string), Node Type (string), Attributes (optional) |
| Connection | Directed edge indicating relationship or data flow | Source Node (string), Target Node (string), Connection Type (optional) |

## 6. Technology Stack

| Component                | Technology / Library       | Purpose                                   |
|--------------------------|---------------------------|-------------------------------------------|
| Excel Parsing            | pandas                    | Read, parse, and validate Excel sheet data |
| Diagram Definition       | Custom Python logic       | Generate Mermaid syntax text               |
| Diagram Rendering        | mermaid-cli or mermaid-cli-python | Convert Mermaid `.mmd` files to images    |
| CLI Argument Parsing     | argparse                  | Command-line interface management          |
| Environment              | Python 3.7+               | Execution platform                          |
| Dependencies             | Node.js (for mermaid-cli) | Required for diagram rendering              |

## 7. File Inputs and Outputs

- **Input:**
  - Excel file with two sheets:
    - `Sheet1` - Nodes
    - `Sheet2` - Connections

- **Output:**
  - Mermaid `.mmd` file containing the graph structure (temporary or optional save).
  - Rendered diagram image file in user-specified format (PNG, SVG).

## 8. Error Handling & Validation

- Check file existence and readability at input path.
- Validate Excel sheets and mandatory columns.
- Cross-check node references in connections sheet.
- Graceful error messages for:
  - Missing or invalid inputs.
  - Rendering failures.
  - File write permission issues.
- Exit codes to support automation integration.

## 9. Performance Considerations

- Efficient Excel parsing using `pandas`.
- Mermaid CLI rendering optimized for diagrams up to 100 nodes with expected processing under 10 seconds.
- Asynchronous or multiprocessing rendering can be considered for large diagrams in future iterations.

## 10. Extensibility & Future Enhancements

- Support additional input formats: CSV, JSON.
- Support styling Mermaid diagrams with node types/colors.
- Allow custom Mermaid directives via CLI flags.
- Interactive validation and diagram preview.
- GUI wrapper for non-technical users.
- Integration with CI/CD pipelines and documentation tools.

## 11. Development & Deployment

- **Development Environment:**
  - Python virtual environment setup.
  - Node.js environment for Mermaid CLI.
  - Dependency management with `pip` and `npm`.

- **Deployment:**
  - Distributable as a pip-installable Python package or standalone script.
  - Docker container option bundling Python and Node.js runtime for platform independence.

## 12. Summary

This technical approach leverages best-in-class Python and Mermaid tooling to provide developers with an automated, command-line driven pipeline for producing clean, maintainable architecture diagrams from structured Excel input. The system emphasizes usability, extensibility, and integration capability, focused on modern developer workflows.

*End of Document*

---

## 1. Installation Instructions

**A. Python Environment**
1. Ensure you have Python 3.7+ installed.
2. (Recommended) Create a virtual environment:
   ```sh
   python -m venv venv
   ```
   Activate it:
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`

3. Install Python dependencies:
   ```sh
   pip install -r requirements.txt
   ```

**B. Node.js & Mermaid CLI**
1. Install Node.js (if not already installed):  
   [Download Node.js](https://nodejs.org/)

2. Install Mermaid CLI globally:
   ```sh
   npm install -g @mermaid-js/mermaid-cli
   ```

---

## 2. Usage

Assuming your Excel file is named `architecture.xlsx` and you want to output a PNG:

```sh
python excel_to_mermaid.py --input architecture.xlsx --output diagram.png
```

- The tool will:
  - Validate your Excel file (Sheet1: Nodes, Sheet2: Connections)
  - Generate a `.mmd` file alongside your output
  - Render the diagram to the specified image file (PNG, SVG, etc.)

**Example:**
```sh
python excel_to_mermaid.py --input my_architecture.xlsx --output my_diagram.svg
```

---

## 3. Excel File Format

- **Sheet1 (Nodes):**  
  Columns: `Node Name`, `Node Type` (plus optional attributes)
- **Sheet2 (Connections):**  
  Columns: `Source Node`, `Target Node`, `Connection Type` (optional)

---

## 4. Troubleshooting

- If you see `Error: Mermaid CLI (mmdc) not found...`, ensure you installed Mermaid CLI and that `mmdc` is in your PATH.
- For missing columns or invalid references, check your Excel file matches the required format.

---

Let me know if you need a sample Excel file or further customization!