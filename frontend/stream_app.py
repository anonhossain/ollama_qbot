import streamlit as st
import requests
import time

# FastAPI endpoint URL for file upload and MCQ generation
FASTAPI_UPLOAD_URL = "http://localhost:8080/api/upload-files/"
FASTAPI_DELETE_URL = "http://localhost:8080/api/delete-pdfs/"
FASTAPI_GENERATE_MCQS_URL = "http://localhost:8080/api/generate-mcqs/"

# Function to upload files to FastAPI
def upload_pdf_to_fastapi(pdf_files):
    try:
        # Prepare the files to be sent in the request
        files = [('files', (file.name, file)) for file in pdf_files]
        
        # Send POST request to FastAPI to upload the files
        response = requests.post(FASTAPI_UPLOAD_URL, files=files)
        
        if response.status_code == 200:
            st.success("Files successfully uploaded!")
        else:
            st.error(f"Error uploading files: {response.json().get('message', 'Unknown error')}")
    except Exception as e:
        st.error(f"An error occurred while uploading files: {e}")

# Function to delete files from the FastAPI backend
def delete_pdfs():
    try:
        response = requests.delete(FASTAPI_DELETE_URL)
        if response.status_code == 200:
            st.success("PDFs successfully deleted!")
        else:
            st.error("Error deleting PDFs.")
    except Exception as e:
        st.error(f"An error occurred while deleting PDFs: {e}")

# Function to generate MCQs
def generate_mcqs():
    try:
        # Send POST request to generate MCQs
        response = requests.post(FASTAPI_GENERATE_MCQS_URL)
        if response.status_code == 200:
            st.success("MCQs generated successfully!")
            return response.json()  # Return the result from the FastAPI response (e.g., file location)
        else:
            st.error(f"Error generating MCQs: {response.json().get('message', 'Unknown error')}")
            return None
    except Exception as e:
        st.error(f"An error occurred while generating MCQs: {e}")
        return None

# Main Streamlit app
def mcq_bot():
    # File uploader for PDF
    st.title("PDF Upload and MCQ Generation")
    uploaded_files = st.file_uploader("Choose PDF files", type="pdf", accept_multiple_files=True)

    # Upload button
    if uploaded_files:
        st.write("You uploaded:")
        for file in uploaded_files:
            st.write(file.name)

        if st.button("Upload Files to FastAPI"):
            upload_pdf_to_fastapi(uploaded_files)

    # Delete button
    if st.button("Delete PDFs"):
        delete_pdfs()

    # MCQ Generation Button
    generate_button = st.button("Generate Questions")

    if generate_button:
        # Show a processing indicator
        with st.spinner("Generating MCQs... This might take a few moments."):
            # Generate MCQs by calling FastAPI
            result = generate_mcqs()

        if result:
            st.success("MCQs are ready!")
            show_mcqs(result)

# Show the MCQs once they are ready
def show_mcqs(result):
    # Assuming the MCQs are returned as a list of questions with options
    questions = result.get("mcqs", [])  # Modify according to your API response
    if questions:
        user_answers = []
        descriptions = []  # To store descriptions for each question

        # Loop through each question
        for idx, question_data in enumerate(questions):
            question = question_data["question"]
            options = question_data["options"]
            description = question_data["description"]
            correct_answer = question_data["correct_answer"]

            descriptions.append(description)

            # Display the question
            st.write(f"### {question}")

            # User's answer input
            options_list = ["Select an option"] + list(options.values())
            user_answer = st.radio(f"Choose your answer for Q{idx + 1}:", options=options_list, key=idx)

            user_answers.append((user_answer, correct_answer))

        # Show the submit button
        if st.button("Submit Answers"):
            score = 0
            results = []

            # Compare answers with correct answers
            for idx, (user_answer, correct_answer) in enumerate(user_answers):
                if user_answer != "Select an option":
                    if user_answer == correct_answer:
                        score += 1
                        results.append(f"Q{idx + 1}: Correct ✅")
                    else:
                        results.append(f"Q{idx + 1}: Incorrect ❌ (Correct answer: {correct_answer})")
                else:
                    results.append(f"Q{idx + 1}: No option selected 🧐")

            # Display the results
            st.write(f"### Your Final Score: {score}/{len(questions)}")
            st.write("### Results:")
            for idx, res in enumerate(results):
                st.write(res)
                st.write(f"**Description:** {descriptions[idx]}")

# Run the app
if __name__ == "__main__":
    mcq_bot()
