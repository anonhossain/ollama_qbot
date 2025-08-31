import fitz  # PyMuPDF for PDF -> images
import os
import base64
import json
import requests
import shutil


class PDFImageExtractor:
    """Convert PDF pages to images and manage temporary image folder."""

    def __init__(self, pdf_path, output_folder="pdf_images"):
        self.pdf_path = pdf_path
        self.output_folder = output_folder

    def pdf_to_images(self):
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

    def __init__(self, model="gemma3:latest", ollama_url="http://localhost:11434/api/generate"):
        self.model = model
        self.ollama_url = ollama_url

    def encode_image(self, image_path):
        """Convert image file to base64 string."""
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")

    def extract_text_from_image(self, image_path):
        """Send image to Gemma3 for OCR-like extraction."""
        image_b64 = self.encode_image(image_path)

        payload = {
            "model": self.model,
            "prompt": "Extract and return all readable text from this image.",
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


def process_pdf_with_gemma(pdf_path):
    """Full pipeline: PDF -> images -> Gemma OCR -> combined text."""
    extractor = PDFImageExtractor(pdf_path)
    gemma_ocr = GemmaOCR()

    image_paths = extractor.pdf_to_images()
    all_text = ""

    for idx, image_path in enumerate(image_paths):
        print(f"\n🔍 Processing Page {idx + 1}...")
        page_text = gemma_ocr.extract_text_from_image(image_path)
        all_text += f"\n\n--- Page {idx + 1} ---\n{page_text}"

    # Clean up temporary images
    extractor.cleanup_images()
    return all_text


if __name__ == "__main__":
    pdf_path = "file/Notes.pdf"  # Update this to your PDF path
    output_text = process_pdf_with_gemma(pdf_path)

    # Save extracted text to a .txt file
    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    output_file = f"{base_name}.txt"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(output_text)

    print(f"\n✅ Extraction Complete! Text saved to {output_file}")
