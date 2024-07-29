## Usage Instructions

This script compares HTML tables from two files and processes them based on the specified arguments.

### Requirements

- Python 3.x
- `pandas` library

### Setup

* Option 1:
```bash 
pip install -r requirements.txt
```
* Option 2:
```bash
chmod +x setup.sh
./setup.sh
```

### Script Usage

Run the script from the command line with the following options:

```bash
python comp.py --golden <path_to_golden_htm> --target <path_to_target_htm> --max_time <max_processing_time>
```

### Arguments

- `--golden` (str): Path to the golden HTML file (default: `C:/Users/Agnisys96/Desktop/dev/comp/HTML_DATA/cypress.htm`).
- `--target` (str): Path to the target HTML file (default: `C:/Users/Agnisys96/Desktop/dev/comp/HTML_DATA/cypress.htm`).
- `--max_time` (int): Maximum time in seconds for processing (default: `300`).

### Example

To compare `golden.htm` with `target.htm` and set a processing timeout of 600 seconds, use:

```bash
python comp.py --golden /path/to/golden.htm --target /path/to/target.htm --max_time 600
```

### Script Functionality

1. **Initialize `Table` Objects**: Creates `Table` instances for the golden and target HTML files.
2. **Set Root Path**: The root path for processing is set based on the golden HTML file’s directory.

### Notes

- Ensure that paths to the HTML files are correctly specified.
- The script uses `pandas` for processing HTML tables, so ensure it's installed in your environment.
- Recommended directory Structure
- root
  - comp.py
  - golden_folder
    - golden.htm
  - target_folder
    - target.htm
