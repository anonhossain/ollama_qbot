import re
import json

def parse_mcq_file(input_file, output_file):
    with open(input_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Split questions (each starts with "Question No:")
    raw_questions = re.split(r"Question No:\s*\d+", content)
    mcqs = []
    q_id = 1

    for block in raw_questions:
        block = block.strip()
        if not block:
            continue

        # Extract Question
        question_match = re.search(r"Question:\s*(.*)", block)
        question = question_match.group(1).strip() if question_match else ""

        # Extract Options
        options = {}
        for opt in ["A", "B", "C", "D"]:
            match = re.search(rf"{opt}\.\s*(.*)", block)
            if match:
                options[opt] = match.group(1).strip()

        # Extract Correct Answer
        correct_match = re.search(r"Correct Answer:\s*([A-D])", block)
        correct_answer = correct_match.group(1) if correct_match else ""

        # Extract Description
        desc_match = re.search(r"Description:\s*(.*)", block, re.DOTALL)
        explanation = desc_match.group(1).strip() if desc_match else ""

        mcqs.append({
            "id": q_id,
            "question": question,
            "options": [{k: v} for k, v in options.items()],
            "correct_answer": correct_answer,
            "explanation": explanation
        })
        q_id += 1

    # Save JSON
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(mcqs, f, indent=4, ensure_ascii=False)

    print(f"✅ Saved {len(mcqs)} questions to {output_file}")


if __name__ == "__main__":
    parse_mcq_file("mcqs_raw.txt", "mcq_raw.json")