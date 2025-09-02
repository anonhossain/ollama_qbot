import fitz  # PyMuPDF for PDF -> images
import os
import base64
import json
import requests
import shutil
from dotenv import load_dotenv

load_dotenv()

class PDFImageExtractor:
    """Convert PDF pages to images and manage temporary image folder."""

    def __init__(self, pdf_path: str, output_folder: str = "pdf_images"):
        self.pdf_path = pdf_path
        self.output_folder = output_folder

    def pdf_to_images(self) -> list:
        """Convert each page of PDF to JPG image and return paths."""
        doc = fitz.open(self.pdf_path)
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

        image_paths = []
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            pix = page.get_pixmap(dpi=200)  # higher DPI for better OCR quality
            image_path = os.path.join(self.output_folder, f"page_{page_num + 1}.jpg")
            pix.save(image_path)
            image_paths.append(image_path)
            print(f"✅ Page {page_num + 1} saved as {image_path}")
        doc.close()
        return image_paths

    def cleanup_images(self):
        """Delete all images from the output folder after extraction."""
        if os.path.exists(self.output_folder):
            shutil.rmtree(self.output_folder)
            print(f"🗑️ Deleted temporary folder: {self.output_folder}")


class GemmaOCR:
    """Send images to Gemma3 model via Ollama API to extract text."""

    def __init__(self, model=None, ollama_url=None):
        self.model = model or os.getenv("OCR_MODEL")
        self.ollama_url = ollama_url or os.getenv("OLLAMA_HOST_URL") + "/api/generate"

    def encode_image(self, image_path: str) -> str:
        """Convert image file to base64 string."""
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")

    def extract_text_from_image(self, image_path: str) -> str:
        """Send image to Gemma3 for OCR-like extraction."""
        image_b64 = self.encode_image(image_path)

        payload = {
            "model": self.model,
            "prompt": "Extract and return all readable text from this image. Do not add any extra commentary.",
            "images": [image_b64]
        }

        try:
            # Stream the response to handle multiple JSON objects
            response = requests.post(self.ollama_url, json=payload, stream=True)
            if response.status_code != 200:
                print(f"⚠️ Ollama API error {response.status_code}: {response.text}")
                return ""

            extracted_text = ""
            for line in response.iter_lines():
                if not line:
                    continue
                try:
                    data = json.loads(line.decode("utf-8"))
                    extracted_text += data.get("response") or data.get("content") or ""
                except json.JSONDecodeError:
                    continue  # skip malformed lines

            return extracted_text.strip()

        except Exception as e:
            print(f"⚠️ Error extracting text from image: {e}")
            return ""


class PDFProcessor:
    """Full pipeline for processing PDF into text using Gemma OCR."""

    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.extractor = PDFImageExtractor(pdf_path)
        self.gemma_ocr = GemmaOCR()

    def process_pdf(self) -> str:
        """Full pipeline: PDF -> images -> Gemma OCR -> combined text."""
        image_paths = self.extractor.pdf_to_images()
        all_text = ""

        for idx, image_path in enumerate(image_paths):
            print(f"\n🔍 Processing Page {idx + 1}...")
            page_text = self.gemma_ocr.extract_text_from_image(image_path)
            all_text += f"\n\n--- Page {idx + 1} ---\n{page_text}"

        # Clean up temporary images
        self.extractor.cleanup_images()
        return all_text


def save_combined_text_from_pdfs(upload_folder: str = "upload", output_file: str = "output/combined_output.txt"):
    """Process all PDFs from the upload folder and save the combined extracted text to a file."""
    # Ensure upload folder exists
    os.makedirs(upload_folder, exist_ok=True)

    if not os.path.exists(upload_folder):
        print(f"⚠️ Upload folder '{upload_folder}' not found.")
        return

    pdf_files = [f for f in os.listdir(upload_folder) if f.endswith(".pdf")]
    if not pdf_files:
        print(f"⚠️ No PDF files found in '{upload_folder}'")
        return

    all_extracted_text = ""

    # Process each PDF file
    for pdf_file in pdf_files:
        pdf_path = os.path.join(upload_folder, pdf_file)
        print(f"\n📄 Processing PDF: {pdf_path}")
        processor = PDFProcessor(pdf_path)
        extracted_text = processor.process_pdf()
        all_extracted_text += f"\n\n--- Extracted from {pdf_file} ---\n{extracted_text}"

    # Ensure the output folder exists before writing
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(all_extracted_text)

    print(f"\n✅ Extraction Complete! All text saved to {output_file}")

    # Process each PDF file
    for pdf_file in pdf_files:
        pdf_path = os.path.join(upload_folder, pdf_file)
        print(f"\n📄 Processing PDF: {pdf_path}")
        processor = PDFProcessor(pdf_path)
        extracted_text = processor.process_pdf()
        all_extracted_text += f"\n\n--- Extracted from {pdf_file} ---\n{extracted_text}"

    # Save all extracted text into one file
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(all_extracted_text)

    print(f"\n✅ Extraction Complete! All text saved to {output_file}")


if __name__ == "__main__":
    save_combined_text_from_pdfs()
