import os
import json
import re

class MCQTextToJSON:
    """Convert raw MCQ text to structured JSON format."""

    def __init__(self, raw_mcq_file: str, output_folder: str = "output"):
        self.raw_mcq_file = raw_mcq_file
        self.output_folder = output_folder

    def load_raw_mcqs(self):
        """Load the raw MCQ text from the file."""
        if not os.path.exists(self.raw_mcq_file):
            raise FileNotFoundError(f"Raw MCQ file '{self.raw_mcq_file}' not found.")
        
        with open(self.raw_mcq_file, "r", encoding="utf-8") as file:
            return file.read()

    def parse_mcqs(self, raw_text):
        """Parse the raw MCQ text into structured format."""
        mcqs = []
        
        # Regular expression pattern for MCQ parsing
        mcq_pattern = re.compile(
            r"Question No:\s*(?P<question_no>\d+)\s*"
            r"Question:\s*(?P<question>.*?)\s*"
            r"Options:\s*"
            r"A\.\s*(?P<option_a>.*?)\s*"
            r"B\.\s*(?P<option_b>.*?)\s*"
            r"C\.\s*(?P<option_c>.*?)\s*"
            r"D\.\s*(?P<option_d>.*?)\s*"
            r"Correct Answer:\s*(?P<correct_answer>[A-D])\s*"
            r"Description:\s*(?P<description>.*?)\s*",
            re.DOTALL
        )

        # Match the raw MCQ text against the pattern
        matches = mcq_pattern.finditer(raw_text)

        for match in matches:
            mcq = {
                "question_no": int(match.group("question_no")),
                "question": match.group("question").strip(),
                "options": {
                    "A": match.group("option_a").strip(),
                    "B": match.group("option_b").strip(),
                    "C": match.group("option_c").strip(),
                    "D": match.group("option_d").strip(),
                },
                "correct_answer": match.group("correct_answer"),
                "description": match.group("description").strip(),
            }
            mcqs.append(mcq)
        
        return mcqs

    def save_as_json(self, mcqs, output_file="mcqs.json"):
        """Save the parsed MCQs to a JSON file."""
        os.makedirs(self.output_folder, exist_ok=True)
        
        output_path = os.path.join(self.output_folder, output_file)
        with open(output_path, "w", encoding="utf-8") as file:
            json.dump(mcqs, file, indent=4)
        
        print(f"✅ Saved MCQs as JSON to {output_path}")

    def process(self):
        """Full pipeline to load raw MCQs, parse them, and save as JSON."""
        raw_text = self.load_raw_mcqs()
        mcqs = self.parse_mcqs(raw_text)
        self.save_as_json(mcqs)


# --- Running the pipeline ---
if __name__ == "__main__":
    raw_mcq_file = "output/mcqs_raw.txt"  # Path to the raw MCQ file
    mcq_json_processor = MCQTextToJSON(raw_mcq_file, output_folder="output")
    mcq_json_processor.process()
