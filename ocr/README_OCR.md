# OCR Benchmarking Module

Standalone module to extract text from PDFs and images using 4 OCR engines.

## System Dependencies (Install First)

```bash
sudo apt install tesseract-ocr poppler-utils -y
```

## Setup

```bash
python3.11 -m venv ocr_venv
source ocr_venv/bin/activate
pip install -r requirements_ocr.txt
```

## Usage

1. Drop your PDF or image files into `ocr/input/`
2. Run: `python ocr_main.py`
3. Results saved to `ocr/output/`
4. Benchmark table printed to terminal

## Output Files

Each tool saves its result separately: `toolname_originalfilename.txt`

Example: `tesseract_invoice.txt`, `doctr_invoice.txt`

## Choosing the Best Tool

- **Clean printed PDFs** → Tesseract
- **Photos of signs or real world text** → EasyOCR
- **Handwritten documents** → TrOCR (change model to `trocr-base-handwritten` in `trocr_ocr.py`)
- **Invoices, forms, tables, complex layouts** → DocTR
