import json
import os
import glob
import subprocess
# import pandas as pd


def read_log_json():
    f = open(f"{os.path.abspath('')}/statements/log/history.json", "r")
    file_content = f.read()
    f.close()
    data = json.loads(file_content) if file_content else []
    return data


def collect_files():
    base_dir = f"{os.path.abspath('')}/statements"
    file_paths = []
    pattern = f"{base_dir}/*.pdf"
    file_paths = [path for path in glob.glob(pattern)]

    return file_paths


def move_files():
    log = read_log_json()
    processed_files = [entry["file_name"] for entry in log]
    # log_df = pd.DataFrame.from_dict(log)
    
    file_paths = collect_files()

    for file in file_paths:
        file_name = file.split("/")[-1]
        if file_name in processed_files:
            print(f"{file_name} has been processed")
            subprocess.run(["mv", file, f"{os.path.abspath('')}/statements/processed/{file_name}"])


if __name__ == "__main__":
    move_files()