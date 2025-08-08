import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
from nbconvert import NotebookExporter
import os

file_paths = [
    "/Users/Ludwig/Documents/GitHub/data_demo/637b023440527bf2daa5932f__post1.json",
    "/Users/Ludwig/Documents/GitHub/data_demo/637c399add50d54aa5af0cf4__post2.json",
    "/Users/Ludwig/Documents/GitHub/data_demo/637d8ea678f0cb97981425dd__post3.json",
    "/Users/Ludwig/Documents/GitHub/data_demo/6380728cdd50d54aa5af0cf5__post5.json",
]

notebook_filename = "/Users/Ludwig/Documents/GitHub/data_tutorial/edies_cleaner.ipynb"
output_dir = "executed_notebooks"

os.makedirs(output_dir, exist_ok=True)

for i, path in enumerate(file_paths):
    # Load the notebook
    with open(notebook_filename) as f:
        nb = nbformat.read(f, as_version=4)

    # Replace the file_path in the correct cell
    for cell in nb.cells:
        if cell.cell_type == "code" and "file_path=" in cell.source:
            lines = cell.source.split('\n')
            new_lines = []
            for line in lines:
                if "file_path=" in line:
                    line = f'file_path="{path}",'
                new_lines.append(line)
            cell.source = "\n".join(new_lines)
            break

    # Run the notebook
    ep = ExecutePreprocessor(timeout=600, kernel_name='python3')
    print(f"🚀 Running notebook for: {path}")
    ep.preprocess(nb, {'metadata': {'path': '.'}})

    # Save executed version
    filename_only = os.path.basename(path).replace(".json", "")
    output_path = os.path.join(output_dir, f"executed_{filename_only}.ipynb")
    with open(output_path, 'w') as f:
        nbformat.write(nb, f)

    print(f"✅ Saved: {output_path}")
