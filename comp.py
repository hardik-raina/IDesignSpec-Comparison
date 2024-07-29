import argparse
import os
from pprint import pprint
from typing import Dict, List, Set, Tuple
import pandas as pd
from bs4 import BeautifulSoup
import concurrent.futures

class Table:
    ROOT_PATH = None
    def __init__(self, file_path: str) -> None:
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
        rows = last_table.find_all('tr')[1:]  # Skip the header row
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
                    # file_path + link
                    os.path.join(os.path.dirname(file_path), link)
                ])
        # pprint(data)
        columns = ['S.No.', 'Names', 'Size', 'Address', 'Description', 'Link']
        self.df = pd.DataFrame(data, columns=columns)

    def paths(self) -> List[str]:
        return self.df['Link'].to_list()
    
    def __eq__(self, value: object) -> bool:
        if not isinstance(value, Table):
            return NotImplemented
        
        df1 = self.df.drop(columns='Link')
        df2 = value.df.drop(columns='Link')
        
        return df1.equals(df2)

    def __ne__(self, value: object) -> bool:
        return not self == value

    def __str__(self) -> str:
        return self.df.to_string(index=False)

    def __repr__(self) -> str:
        return str(self)


def dfs(t1: Table, t2: Table, visited: Set[str] = set()) -> Dict:
    """Perform DFS and collect file paths of visited nodes."""
    if t1 != t2:
        return {"same":False, "diff": (t1.id, t2.id), "err":False}
    
    stack: List[Tuple[str, str]] = [(x, y) for x, y in zip(t1.paths(), t2.paths())]
    
    while stack:
        # print(f'Stack Size: {len(stack)}')
        t1_child_path, t2_child_path = stack.pop()
        
        if t1_child_path in visited or t2_child_path in visited:
            continue
        
        visited.add(t1_child_path)
        visited.add(t2_child_path)
        
        t1_child_table = Table(t1_child_path)
        t2_child_table = Table(t2_child_path)
        
        if t1_child_table != t2_child_table:
            return {"same":False, "diff": (t1_child_table.id, t2_child_table.id), "err":False}
        
        stack.extend(zip(t1_child_table.paths(), t2_child_table.paths()))
    
    return {"same":True, "diff": (), "err":False}


def run_with_timeout(fn, timeout, *args):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(fn, *args)
        try:
            result = future.result(timeout=timeout)
            return result
        except concurrent.futures.TimeoutError:
            print(f"Function call aborted after {timeout} seconds")
            return {"same":f"Function call aborted after {timeout} seconds", "diff": (), "err":True}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Process HTML table comparison.")
    parser.add_argument('--golden', type=str, default=r"C:/Users/Agnisys96/Desktop/dev/comp/HTML_DATA/cypress.htm",
                        help='Path to the golden HTML file.')
    parser.add_argument('--target', type=str, default=r"C:/Users/Agnisys96/Desktop/dev/comp/HTML_DATA/cypress.htm",
                        help='Path to the target HTML file.')
    parser.add_argument('--max_time', type=int, default=300,
                        help='Maximum time in seconds for processing.')

    args = parser.parse_args()

    Table.ROOT_PATH = os.path.dirname(args.path_golden)

    t1 = Table(args.golden)
    t2 = Table(args.target)

    result = run_with_timeout(dfs, args.max_time, t1, t2)
    print(result)
