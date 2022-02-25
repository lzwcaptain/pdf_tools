import argparse
import os
from typing import *
import fitz


def find_all_pdfs(dist_dir: str) -> List[str]:
    pdfs = []
    for root, ds, fs in os.walk(dist_dir):
        for f in fs:
            if f.endswith(".pdf"):
                file_path = os.path.join(root, f)
                pdfs.append(file_path)
    pdfs = sorted(pdfs)
    return pdfs


def create_bookmark(dist_dir: str, pdf_paths: List[str]):
    """
        /a/b/c/d/e.pdf b->c->d
    :param dist_dir:
    :param pdf_paths:
    :return:
    """

    result_pdf = fitz.open()
    pdf_toc = []
    mark_set = list()
    for file_path in pdf_paths:
        doc = fitz.open(file_path)
        toc = doc.get_toc()
        file_path_ac = file_path[file_path.find(dist_dir) + len(dist_dir) + 1:]
        path_split_sep = file_path_ac.split(os.path.sep)

        if path_split_sep[-1].endswith(".pdf"):
            path_split_sep[-1] = path_split_sep[-1].split(".")[0]
        # 添加目录标签
        for mark_count in range(1, len(path_split_sep) + 1):
            item = [mark_count, path_split_sep[mark_count - 1], result_pdf.page_count + 1]
            if item[0:2] not in mark_set:
                pdf_toc.append(item)
                mark_set.append(item[0:2])

        # 追加文件自身标签
        for i in range(len(toc)):
            toc[i][0] += len(path_split_sep)
            toc[i][2] += result_pdf.page_count
            pdf_toc.append(toc[i])

        result_pdf.insert_pdf(doc)
        print(f"添加 {file_path}")
    result_pdf.set_toc(pdf_toc)
    return result_pdf


def run(dist_path: str, file_name: str):
    pdf_paths = find_all_pdfs(dist_path)
    result_pdf = create_bookmark(dist_path, pdf_paths)
    result_pdf.save(os.path.join(dist_path, file_name))



if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("-d", "--dist", help="开始目录(默认本地目录)", default="./")
    arg_parser.add_argument("-f", "--file_name", help="保存文件名(.pdf)", default="merge.pdf")
    args = arg_parser.parse_args()
    dist = args.dist
    file_name = args.file_name
    run(dist, file_name)
