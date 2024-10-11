import os
import google.generativeai as genai
from concurrent.futures import ThreadPoolExecutor
import itertools

# List of API keys to use
api_keys = [
    "AIzaSyAuBYlizr1yWnGPa_iWdfHviOqEJA-HTFs",
    "AIzaSyCqu-7n2S5_2ZZ5em5-V_EHPUEZ4w9yem0",
    "AIzaSyAwA_IGX-SdGu_b_lDMrVqSfzLGgYYYnKs",
    "AIzaSyC78kkApsW19kC8Pun6UhaszPxH7ERAU3E"
]

# Function to configure the Gemini API key
def configure_api_key(api_key):
    genai.configure(api_key=api_key)

# Function to upload and process a PDF file using Gemini API
def convert_pdf_to_text(pdf_file_path, api_key):
    configure_api_key(api_key)

    # Upload PDF file to Gemini
    try:
        uploaded_pdf = genai.upload_file(pdf_file_path)
    except Exception as e:
        print(f"Error uploading {pdf_file_path}: {e}")
        return None

    # Create a prompt for conversion
    prompt = "Convert this PDF to text, paying close attention to accuracy and ensuring that all information, including tables and lists, is correctly represented."

    # Use the Gemini API to generate content
    model = genai.GenerativeModel(model_name="gemini-1.5-pro")

    try:
        response = model.generate_content([prompt, uploaded_pdf])
    except Exception as e:
        print(f"Error processing {pdf_file_path}: {e}")
        return None

    return response.text

# Function to save text to a .txt file
def save_text_to_file(text, output_file_path):
    with open(output_file_path, 'w', encoding='utf-8') as text_file:
        text_file.write(text)

# Function to convert a single PDF file to text and save it
def process_single_pdf(pdf_file_path, output_folder, api_key):
    print(f"Converting {os.path.basename(pdf_file_path)} using API key {api_key}...")

    # Convert the PDF to text using the Gemini API
    text = convert_pdf_to_text(pdf_file_path, api_key)

    if text:
        # Save the converted text to a .txt file
        output_file_path = os.path.join(output_folder, f"{os.path.splitext(os.path.basename(pdf_file_path))[0]}.txt")
        save_text_to_file(text, output_file_path)
        print(f"Saved {output_file_path}")

# Function to convert a folder of PDFs to text files using parallel processing
def convert_folder_of_pdfs_to_text(folder_path, output_folder, api_keys):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Get all PDF files in the folder
    pdf_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.pdf')]

    # Cycle through the API keys
    api_key_cycle = itertools.cycle(api_keys)

    # Use ThreadPoolExecutor for parallel processing
    with ThreadPoolExecutor(max_workers=len(api_keys)) as executor:
        # Submit each PDF conversion task to the executor
        futures = [
            executor.submit(process_single_pdf, pdf_file, output_folder, next(api_key_cycle))
            for pdf_file in pdf_files
        ]

        # Wait for all tasks to complete
        for future in futures:
            future.result()  # This will raise exceptions if any occurred during processing

# Folder paths
pdf_folder = "handouts"
output_folder = "output"

# Run the conversion in parallel
convert_folder_of_pdfs_to_text(pdf_folder, output_folder, api_keys)
