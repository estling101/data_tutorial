import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
import os
import time
import threading
import json

file_paths = [
    "/Users/Ludwig/Documents/GitHub/data_demo/637b023440527bf2daa5932f__post1.json",
    "/Users/Ludwig/Documents/GitHub/data_demo/637c399add50d54aa5af0cf4__post2.json",
    "/Users/Ludwig/Documents/GitHub/data_demo/637d8ea678f0cb97981425dd__post3.json",
    "/Users/Ludwig/Documents/GitHub/data_demo/637f0d5f78f0cb97981425de__post4.json",
    "/Users/Ludwig/Documents/GitHub/data_demo/6380728cdd50d54aa5af0cf5__post5.json",
    "/Users/Ludwig/Documents/GitHub/data_demo/638450a3dd50d54aa5af0cf6__post8.json",
    "/Users/Ludwig/Documents/GitHub/data_demo/63858a2cfb3ff533c12df166__post9.json",
    "/Users/Ludwig/Documents/GitHub/data_demo/6386d89efb3ff533c12df167__post10.json",
    "/Users/Ludwig/Documents/GitHub/data_demo/63882be478f0cb97981425df__post11.json",
    "/Users/Ludwig/Documents/GitHub/data_demo/63898d48d430891009401330__post12.json",

]

notebook_filename = "/Users/Ludwig/Documents/GitHub/data_tutorial/edies_cleaner.ipynb"
output_dir = "executed_notebooks"

os.makedirs(output_dir, exist_ok=True)

def print_still_running(stop_event, interval=30):
    while not stop_event.is_set():
        print("⏳ Still running...")
        time.sleep(interval)

class TimingExecutePreprocessor(ExecutePreprocessor):
    def preprocess_cell(self, cell, resources, index):
        start_time = time.time()
        result = super().preprocess_cell(cell, resources, index)
        end_time = time.time()
        if not hasattr(self, "cell_runtimes"):
            self.cell_runtimes = []
        self.cell_runtimes.append({
            "cell_index": index,
            "cell_type": cell.cell_type,
            "execution_time_sec": end_time - start_time
        })
        return result

for i, path in enumerate(file_paths):
    # Load the notebook
    with open(notebook_filename) as f:
        nb = nbformat.read(f, as_version=4)

    # Replace the injected_file_path in the correct cell
    for cell in nb.cells:
        if cell.cell_type == "code" and "injected_file_path =" in cell.source:
            lines = cell.source.split('\n')
            new_lines = []
            for line in lines:
                if "injected_file_path =" in line:
                    line = f'    injected_file_path = "{path}"'  # preserve 4-space indent
                new_lines.append(line)
            cell.source = "\n".join(new_lines)
            break

    # Prepare and start the "still running" thread
    stop_event = threading.Event()
    thread = threading.Thread(target=print_still_running, args=(stop_event, 180))
    thread.start()

    # Run the notebook with timing
    ep = TimingExecutePreprocessor(timeout=600, kernel_name='your_env_name')
    print(f"🚀 Running notebook for: {path}")
    start_time = time.time()

    try:
        ep.preprocess(nb, {'metadata': {'path': '.'}})
    finally:
        stop_event.set()
        thread.join()

    # Extract post_x from filename
    filename_only = os.path.basename(path).replace(".json", "")  # e.g. '637b023440527bf2daa5932f__post1'
    post_folder = filename_only.split("__")[-1]  # 'post1'
    post_output_dir = os.path.join(output_dir, post_folder)
    os.makedirs(post_output_dir, exist_ok=True)

    # Save executed notebook in post_x folder
    executed_nb_path = os.path.join(post_output_dir, f"executed_{filename_only}.ipynb")
    with open(executed_nb_path, 'w') as f:
        nbformat.write(nb, f)

    # Save runtimes JSON inside same post_x folder
    runtimes_path = os.path.join(post_output_dir, f"runtimes_{filename_only}.json")
    with open(runtimes_path, 'w') as f:
        json.dump(ep.cell_runtimes, f, indent=2)

    end_time = time.time()
    duration = end_time - start_time
    print(f"✅ Saved notebook: {executed_nb_path} (⏱️ {duration:.2f} seconds)")
    print(f"✅ Saved runtimes: {runtimes_path}")
