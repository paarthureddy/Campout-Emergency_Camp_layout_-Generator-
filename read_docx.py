import sys
try:
    import docx
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "python-docx"])
    import docx

def read_docx(file_path):
    doc = docx.Document(file_path)
    fullText = []
    for para in doc.paragraphs:
        fullText.append(para.text)
    return '\n'.join(fullText)

if __name__ == '__main__':
    text = read_docx(r"E:\sem 7\nn&dl\NN_DL_Group-2_Case_Study_Updated.docx")
    with open(r"e:\Projects\Neural_Networks_Case_Study_G2\extracted_text.txt", "w", encoding="utf-8") as f:
        f.write(text)
