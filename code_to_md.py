"""
将代码全部转换为md
"""
from typing import *
import os
from io import StringIO
from collections import OrderedDict, namedtuple
import argparse


class Markdown(object):
    def __init__(self):
        self.buffer = StringIO()

    def insert_title(self, content: str, num=1):
        title = "#" * num
        text = f"""
{title} {content}
        """
        self.buffer.write(text)

    def insert_code(self, code: str, code_type: str = ""):
        text = f"""
``` {code_type}
{code}
```        

        """
        self.buffer.write(text)

    def get_md(self):
        return self.buffer.getvalue()


Code = namedtuple("Code", ["type", "content"])


class CodeManager(object):
    def __init__(self):
        self.manager = OrderedDict()
        self.md = Markdown()

    def insert(self, path: str, content: Code):
        path_routes = path.split(os.path.sep)
        print(path)
        manager = self.manager
        for route in path_routes[:-1]:
            if type(manager.get(route, None)) != OrderedDict:
                manager[route] = OrderedDict()
            manager = manager[route]
        manager[path_routes[-1]] = content

    def to_md(self) -> str:
        self.__iter_map(manager=self.manager)
        return self.md.get_md()

    def __iter_map(self, manager: OrderedDict, level: int = 1):
        for key, item in manager.items():
            if type(item) == OrderedDict:
                self.md.insert_title(key, level)
                self.__iter_map(item, level + 1)
            else:
                self.md.insert_title(key, level)
                self.md.insert_code(item[1], item[0])


class CodeToMd(object):
    def __init__(self, start_dir: str = ".", include_types: Sequence[str] = None, save_file: str = "./merge.md"):
        self.start_dir = start_dir
        if include_types is None:
            include_types = ["c", "cpp", "h", "hpp"]
        self.include_types = set(include_types)
        self.save_file = save_file
        self.code_manager = CodeManager()
        self.md = ""

    def find_all_code(self):
        files = []
        for root, ds, fs in os.walk(self.start_dir):
            for f in fs:
                file_split = f.split(".")
                file_type = file_split[-1]
                if file_type in self.include_types:
                    files.append(os.path.join(root, f))
        files = sorted(files)
        return files

    def redirect_file(self, count=1):
        if os.path.exists(self.save_file):
            print(f"{self.save_file}  exists")
            file_split = self.save_file.split(".")
            filename = file_split[0]
            file_type = file_split[-1]
            self.save_file = f"{filename}{count}.{file_type}"
            self.redirect_file(count + 1)
        print(f"save_file_path is {self.save_file}")

    def merge_file(self) -> str:
        files = self.find_all_code()
        for f in files:
            with open(f, "r+") as code:
                file_type = f.split(".")[-1]
                route = f[f.startswith(self.start_dir) + len(self.start_dir):]
                self.code_manager.insert(route, (file_type, code.read()))
        return self.code_manager.to_md()

    def save(self, text: str):
        with open(self.save_file, "w+") as f:
            f.write(text)

    def run(self, cover):
        if not cover:
            self.redirect_file()
        md = self.merge_file()
        self.save(md)


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("-p", "--path", help="目标路径", default=".")
    arg_parser.add_argument("-c", "--cover", help="是否覆盖", default=True)
    args = arg_parser.parse_args()
    tool = CodeToMd(args.path)
    tool.run(args.cover)
