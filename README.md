# Table Comparison Script

This script compares tables in two HTML files and reports differences. It offers various options for comparison modes, processing time, and output verbosity.

## Requirements

- Python 3.x
- `pandas` library

## Setup

* Option 1:
    ```bash 
    pip install -r requirements.txt
    ```
* Option 2:
    ```bash
    chmod +x setup.sh
    ./setup.sh
    ```

## Script Usage

Run the script from the command line with the following options:

```bash
python comp.py [options]
```

### Optional Arguments

- `-h, --help`  
  Show help message and exit.

- `--golden GOLDEN`  
  Path to the "golden" reference HTML file for comparison.

- `--target TARGET`  
  Path to the target HTML file to be compared against the golden file.

- `--mode {f,fast,F,full}`  
  Comparison mode:  
  - `'fast'` (or `'f'`): Stop at the first difference.  
  - `'full'` (or `'F'`): Continue and collect all differences.

- `--max_time MAX_TIME`  
  Maximum time allowed for processing the comparison, in seconds. Default is 300 seconds.

- `--firefox FIREFOX`  
  Open the differences in a Firefox browser. Use `'True'` to enable, `'False'` to disable.

- `--verbose VERBOSE`  
  Enable verbose output for detailed line-by-line differences. Use `'True'` to enable, `'False'` to disable.

- `--debug DEBUG`  
  Enable debug mode for detailed stack trace output. Not recommended for regular use. Use `'True'` to enable, `'False'` to disable.

## Example

To compare `golden.htm` with `target.htm`, set a processing timeout of 600 seconds, and enable verbose output:

```bash
python comp.py --golden /path/to/golden.htm --target /path/to/target.htm --max_time 600 --verbose True
```

## Notes

- Ensure that paths to the HTML files are correctly specified.
- The script uses `pandas` for processing HTML tables, so ensure it's installed in your environment.
- Recommended directory structure:
    ```
    root
    ├── comp.py
    ├── golden_folder
    │   └── golden.htm
    └── target_folder
        └── target.htm
    ```

## Script Functionality

1. **Initialize `Table` Objects**: Creates `Table` instances for the golden and target HTML files.
2. **Set Root Path**: The root path for processing is set based on the golden HTML file’s directory.
