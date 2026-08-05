import sys
try:
    import docx
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "python-docx"])
    import docx

import argparse
import os

def read_docx(file_path):
    doc = docx.Document(file_path)
    fullText = []
    for para in doc.paragraphs:
        fullText.append(para.text)
    return '\n'.join(fullText)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Extract text from a DOCX file.")
    parser.add_argument("--input", required=True, help="Path to the DOCX file")
    parser.add_argument("--output", default="extracted_text.txt", help="Path to output text file")
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"Error: Input file {args.input} does not exist.")
        sys.exit(1)

    text = read_docx(args.input)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"Text successfully extracted to {args.output}")
