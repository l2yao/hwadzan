import argparse
import os
from markitdown import MarkItDown
import subprocess
import platform

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

if platform.system() == 'Windows':
    try:
        import win32com.client
        # Use Word to open and save as docx
        word = win32com.client.Dispatch('Word.Application')
        word.Visible = False
    except Exception as e:
        # Fall through to libreoffice fallback
        print(f"pywin32 conversion failed: {e}")

def convert_doc_to_md(doc_path, md_path):
    """
    Converts a .doc file to a .md file using the markitdown library.
    """
    if not os.path.exists(doc_path):
        print(f"Error: Input file not found at {doc_path}")
        return
    
    try:
        input_lower = doc_path.lower()
        docx_path = doc_path.replace('.doc', '.docx')
        if os.path.exists(docx_path):
            print(f"Detected existing .docx file. Using {docx_path} for conversion...")
            source_for_conversion = docx_path
        elif input_lower.endswith('.doc') and not input_lower.endswith('.docx'):
            print(f"Detected legacy .doc file. Converting {doc_path} to .docx first...")
            _convert_doc_to_docx(doc_path, docx_path)
            source_for_conversion = docx_path
        else:
            source_for_conversion = doc_path

        print(f"Converting {source_for_conversion} to {md_path}...")
        converter = MarkItDown()
        result = converter.convert(source_for_conversion)
        with open(md_path, 'w', encoding='utf-8') as md_file:
            md_file.write(result.markdown)
        print(f"Conversion complete. Markdown file saved at {md_path}")
    except Exception as e:
        print(f"An error occurred during conversion: {e}")


def _convert_doc_to_docx(doc_path, docx_path):
    """
    Convert a legacy .doc file to .docx.

    Strategy:
    - On Windows: try to use pywin32 (COM automation) to have Word save as .docx.
    - Fallback: call LibreOffice's `soffice --headless --convert-to docx`.

    Returns the path to the created .docx file or raises RuntimeError on failure.

    Notes for users:
    - For Windows: install pywin32 (pip install pywin32).
    - For fallback: ensure LibreOffice is installed and `soffice` is on PATH.
    """
    if not os.path.exists(doc_path):
        raise RuntimeError(f"Input file not found: {doc_path}")

    # Try Windows COM first
    if platform.system() == 'Windows':
        try:
            doc = word.Documents.Open(os.path.abspath(doc_path))
            # Try SaveAs2 if available, otherwise SaveAs. Use FileFormat=12 (wdFormatXMLDocument -> .docx)
            save_fn = getattr(doc, 'SaveAs2', None)
            if save_fn:
                save_fn(os.path.abspath(docx_path), 12)
            else:
                doc.SaveAs(os.path.abspath(docx_path), 12)
            doc.Close()
            return docx_path
        except Exception as e:
            # Fall through to libreoffice fallback
            print(f"pywin32 conversion failed: {e}")

    # Fallback to soffice (LibreOffice)
    try:
        # LibreOffice will create the file in the same directory as the input unless outdir is specified
        subprocess.run([
            'soffice',
            '--headless',
            '--convert-to',
            'docx',
            '--outdir',
            os.path.dirname(docx_path),
            os.path.abspath(doc_path),
        ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        raise RuntimeError(f"Could not convert .doc to .docx: {e}")

def find_doc_files(root_dir):
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for fn in filenames:
            lower = fn.lower()
            if lower.endswith('.doc'):
                yield os.path.join(dirpath, fn)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert all .doc files to .md files under a given directory")
    parser.add_argument("doc_path", help="The path to the input .doc files.")
    args = parser.parse_args()

    for path in find_doc_files(args.doc_path):
        md_path = path.replace('.doc', '.md')
        if os.path.exists(md_path):
            print(f"Skipping existing file: {md_path}")
            continue
        convert_doc_to_md(path, md_path)
