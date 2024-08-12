"""
# Author: Hardik Raina
# Contact: hardik@agnisys.com // hardik.agnisys@gmail.com
# Date: 7-30-2024 IST

Note to future contributors:
    - Sections recommended to edit: Table

In case of Dynamic content mismatch:
    - Use headless browser(puppeteer:chrome) to render content and then apply bs4 on the generated output. 
    Apply wait time of 1 second for content to load.
    Use OnClick method to click on the links available in the tables to render the NEXT page.
    WARNING!: Time cost rises to 1 s/page. Not feasible.   

# Purpose of script and flow of control.
 ~ Identify points of differrences between generated output of IDS-NG and those from Golden/Stable releases.~ 

 ~ Flow of control for pivotal Table class. 
    - fetch htm(l) file and capture HTML sections using bs4
    - identify tables in the file
    - last table is expected to be the required table from observations
    - fetch hyperlinks to go to deeper documents
    - attach a new col for the links
    - compare currently fetched table(pd.DataFrame) between Golden and target
    - process differrences(store or break operation and print result)
    - use DFS(depth first search) to fetch the next htm(l) file from both golden and target sections and apply previous steps.
"""

import argparse
import concurrent.futures
import os
import subprocess

from bs4 import BeautifulSoup
import pandas as pd
from pprint import pprint as pp
from typing import Dict, List, Tuple

class Table:
    VERBOSE:bool = False
    DEBUG:bool = False
    MODE:str = 'fast'

    def __init__(self, file_path: str) -> None:
        """
        Critical Table class with functionality for Table extraction from given HTM(L) file and operations thereon.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        self.folder_path = os.path.dirname(file_path)
        self.id = file_path

        with open(file_path, 'r', encoding='utf-8') as fp:
            soup = BeautifulSoup(fp, "lxml")
        
        tables = soup.findAll("table")

        if not tables:
            raise ValueError(f"No tables found in file: {file_path}")

        last_table = tables[-1]
        rows = last_table.find_all('tr')[1:]
        data = []

        for row in rows:
            cols = row.find_all('td')
            if len(cols) == 5:
                link_tag = cols[1].find('a')
                link = link_tag['href'].split('.htm')[0] + '.htm' if link_tag else ''
                data.append([
                    cols[0].text.strip(),
                    cols[1].text.strip(),
                    cols[2].text.strip(),
                    cols[3].text.strip(),
                    cols[4].text.strip(),
                    os.path.join(os.path.dirname(file_path), link)
                ])

                if self.DEBUG: 
                    pp(os.path.join(os.path.dirname(file_path), link))

        columns = ['S.No.', 'Names', 'Size', 'Address', 'Description', 'Link']
        self.df = pd.DataFrame(data, columns=columns)

    def paths(self) -> List[str]:
        """
        Helper function returns list of all links/paths found in file leading to other files. \n
        Args: \n
            None \n
        Returns: \n
            List[str]: List of all paths
        """
        return self.df['Link'].to_list()
    
    def __eq__(self, value: object) -> bool:
        if not isinstance(value, Table):
            return NotImplemented
        
        df1 = self.df.drop(columns='Link').reset_index(drop=True)
        df2 = value.df.drop(columns='Link').reset_index(drop=True)

        return df1.equals(df2)
        
    def __ne__(self, value: object) -> bool:
        return not self == value

    def __str__(self) -> str:
        return self.df.to_string(index=False)

    def __repr__(self) -> str:
        return str(self)
    
    def as_df(self) -> pd.DataFrame:
        """
        Returns the underlying DataFrame as is. 
        Args:
            None
        Returns:
            Underlying pd.DataFrame
        """
        return self.df


def dfs(t1: Table, t2: Table, 
        DEBUG:bool = False, MODE:str = 'fast'
        ) -> Dict:
    """
    Perform DFS and collect file paths of visited nodes. \n
    Args: \n
        t1:Table -> root_node for Golden \n
        t2: Table -> root_node for Target \n
        DEBUG: bool -> Controls printing of debug information including Stack Trace \n
        MODE:Literal -> 'fast' mode for breaking on first diff. 'full' mode for collecting all diff \n
    Returns: \n
        Dict[str, ...] -> 'same':bool (If the 2 files are same throughout) \n
                       -> 'diff':List (List of lists of pairs of diferrent files) \n
                       -> 'err':bool (Error in script execution) \n
    """

    visited = set()
    same:bool = True
    diff = []
    if t1 != t2:
        return {"same":False, "diff": [t1.id, t2.id], "err":False}
    
    stack: List[Tuple[str, str]] = [(x, y) for x, y in zip(t1.paths(), t2.paths())]
    
    while stack:
        if DEBUG: 
            print(f'Stack Size: {len(stack)}: ', end='')
        
        t1_child_path, t2_child_path = stack.pop()

        if DEBUG: 
            print(t1_child_path, '|', t2_child_path)


        if t1_child_path in visited or t2_child_path in visited:
            continue
        
        visited.add(t1_child_path)
        visited.add(t2_child_path)
        
        t1_child_table = Table(t1_child_path)
        t2_child_table = Table(t2_child_path)
        
        if t1_child_table != t2_child_table:
            same = False
            diff.append([t1_child_table.id, t2_child_table.id])
            if MODE == 'fast' or MODE == 'f': break

        stack.extend(zip(t1_child_table.paths(), t2_child_table.paths()))
    
    return {"same":same, "diff": diff, "err":False}


def run_with_timeout(fn, timeout:int, *args):
    """
    Multithreaded execution with enforced timelimit using concurrency. \n
    Args: \n
        (function, *function_arguments)  \n
    Returns: \n
        Dict[str, ...] -> 'same':bool (If the 2 files are same throughout) \n
                       -> 'diff':List (List of lists of pairs of diferrent files) \n
                       -> 'err':bool (Error in script execution)
    """
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(fn, *args)
        try:
            result = future.result(timeout=timeout)
            return result
        except concurrent.futures.TimeoutError:
            print(f"Function call aborted after {timeout} seconds")
            return {"same":f"Function call aborted after {timeout} seconds", "diff": [], "err":True}


def show_in_table(file1_path:str, file2_path:str) -> None:
    """
    Show(print) diferrences in the Table(class) generated from both files. In the form of booleans for same or diferrent values. 
    
    Args:
        file1_path:str -> Path of the Golden file to generate df on
        file2_path:str -> Path of the Target file to generate df on
    """
    df1 = Table(file1).as_df()
    df2 = Table(file2).as_df()

    print('-'*50)
    print('\t \t differences'.upper())
    print('-'*50)
    print(df1.eq(df2).to_string())
    print('-'*50)

def firefox(file1_path, file2_path) -> None:
    """
    Render diferrences using firefox CLI. Execution through the subprocess module. \n
    Args: \n
        file1_path:str -> Golden file path to render \n
        file2_path:str -> Target file path to render
    """
    subprocess.run(f'firefox {file1_path} {file2_path}'.split(), 
                   check=True)


if __name__ == '__main__':
    
    VERBOSE:bool = False
    DEBUG:bool = False
    FIREFOX:bool = False
    MODE:str = 'fast'

    parser = argparse.ArgumentParser(description="Compare tables in two HTML files and report differences.")
    parser.add_argument('--golden', type=str, default=r"GOLDEN/cypress.htm",
                        help='Path to the "golden" reference HTML file for comparison.')
    parser.add_argument('--target', type=str, default=r"EXP/cypress.htm",
                        help='Path to the target HTML file to be compared against the golden file.')
    parser.add_argument('--mode', choices=['f', 'fast', 'F', 'full'], default='f', 
                        help="Comparison mode: 'fast' (or 'f') to stop at the first difference, "
                            "'full' (or 'F') to continue and collect all differences.")
    parser.add_argument('--max_time', type=int, default=300,
                        help='Maximum time allowed for processing the comparison, in seconds. Default is 300 seconds.')
    parser.add_argument('--firefox', type=str, default='False', 
                        help="Open the differences in a Firefox browser. Use 'True' to enable, 'False' to disable.")
    parser.add_argument('--verbose', type=str, default='False', 
                        help="Enable verbose output for detailed line-by-line differences. Use 'True' to enable, 'False' to disable.")
    parser.add_argument('--debug', type=str, default='False', 
                        help="Enable debug mode for detailed stack trace output. Not recommended for regular use. Use 'True' to enable, 'False' to disable.")

    
    args = parser.parse_args()

    if args.verbose == True or args.verbose.casefold() == 'True'.casefold():
        Table.VERBOSE = VERBOSE = True
    
    if args.debug == True or args.debug.casefold() == 'True'.casefold():
        Table.DEBUG = DEBUG = True

    if args.firefox == True or args.firefox.casefold() == 'True'.casefold():
        Table.firefox = FIREFOX = True

    if args.mode in ['f', 'fast']: 
        Table.MODE = MODE = 'fast'
    if args.mode in ['F', 'full']:
        Table.MODE = MODE = 'full'


    t1 = Table(args.golden)
    t2 = Table(args.target)

    result = run_with_timeout(dfs, args.max_time, t1, t2, DEBUG, MODE)

    import json
    print(json.dumps(result, indent=4))

    file1, file2 = result['diff'][0]

    if VERBOSE:
        show_in_table(file1, file2)

    if FIREFOX == True:
        try: firefox(file1, file2)
        except: print("Issue Opening using firefox CLI. Check Logs.")
        finally: firefox(file1, file2)