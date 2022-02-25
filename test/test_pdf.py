import fitz

if __name__=="__main__":
    doc = fitz.open("./book-rev11.pdf")
    for t in doc.get_toc():
        print(t)