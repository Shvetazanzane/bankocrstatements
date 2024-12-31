import subprocess  # Run external processes
import os  # Interact with the OS
import pandas as pd  # Work with tabular data
import gradio as gr  # Create interactive interfaces
import matplotlib.pyplot as plt  # Plot visualizations
import re  # Regular expression operations
from dotenv import load_dotenv  # Load environment variables
import cloudinary
from cloudinary.api import resources

# Load environment variables from a .env file
load_dotenv()
api_key = os.getenv('apiKey')  # Retrieve the API key from environment variables

# Cloudinary configuration
cloudinary.config(
    cloud_name="dtw4m0kkb",  # Replace with your Cloudinary cloud name
    api_key="814949254963882",  # Replace with your Cloudinary API key
    api_secret="E8eA1PQ40RZU1BRZUShZvDZePfU"  # Replace with your Cloudinary API secret
)

# Folder options
FOLDERS = [
    "Salary_Slip",
    "Bank_Statement",
    "Balance_sheet",
    "Invoice"
]

# Fetch images from Cloudinary
def fetch_images(folder, limit):
    try:
        result = cloudinary.Search().expression(f"folder:{folder}").max_results(limit).execute()
        image_urls = [resource['secure_url'] for resource in result.get('resources', [])]
        if not image_urls:
            return "No images found for the selected folder.", []
        return f"Fetched {len(image_urls)} images from folder '{folder}'", image_urls
    except Exception as e:
        return f"Error fetching images: {str(e)}", []

# Extract numeric values from text
def extract_numeric_values(text):
    text = re.sub(r'[\u20B9$,]', '', text)  # Remove currency symbols and commas
    numbers = re.findall(r'\d+\.?\d*', text)  # Find all numeric patterns
    try:
        return [float(num) for num in numbers]
    except:
        return []

# Sanitize text by removing unwanted symbols
def sanitize_text(text):
    return re.sub(r'[\*\u201A\u20B9]', '', str(text)).strip()

# Perform OCR using the Node.js script
def run_ocr_with_prompt(file_path, prompt):
    try:
        result = subprocess.run(
            ['node', 'ocrScript.js', file_path, api_key, prompt],
            capture_output=True,
            text=True,
            timeout=60
        )
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        return "Error: OCR process timed out"
    except Exception as e:
        return f"Error: {str(e)}"

# Extract fields based on document type
def extract_fields(document_type, file_path):
    prompts = {
        "Salary_Slip": "Extract Salary_Slip details.",
        "Bank_Statement": "Extract Bank_Statement details.",
        "Balance_sheet": "Extract Balance_sheet details.",
        "Invoice": "Extract invoice details."
    
    }
    prompt_response = run_ocr_with_prompt(file_path, prompts.get(document_type, ""))
    extracted_data = {}
    try:
        for line in prompt_response.split("\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                key = key.strip()
                value = value.strip()
                numeric_values = extract_numeric_values(value)
                extracted_data[key] = numeric_values[0] if numeric_values else value
        df = pd.DataFrame.from_dict(extracted_data, orient='index', columns=['Value']).reset_index()
        df.columns = ['Field', 'Value']
        return df
    except Exception as e:
        return pd.DataFrame(columns=['Field', 'Value'])

# Generate visualizations
def generate_visualizations(df, document_type):
    plt.close('all')
    if df.empty or len(df) < 2:
        return None
    try:
        df['Value'] = pd.to_numeric(df['Value'], errors='coerce').dropna()
        df['Field'] = df['Field'].str.replace(r'[\*]', '', regex=True)
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
        df.plot(kind='pie', y='Value', labels=df['Field'], ax=ax1, autopct='%1.1f%%', startangle=90, legend=False)
        ax1.set_title(f'{document_type} Distribution')
        df.plot(kind='bar', x='Field', y='Value', ax=ax2, color='skyblue', rot=45, legend=False)
        ax2.set_title('Numeric Values')
        ax2.set_xlabel('Fields')
        ax2.set_ylabel('Amount')
        plt.tight_layout()
        chart_path = "visualization_charts.png"
        plt.savefig(chart_path)
        plt.close()
        return chart_path
    except Exception as e:
        return None

# Process OCR for multiple images
def process_ocr_for_images(document_type, image_urls):
    all_raw_data = []
    all_extracted_data = []
    for url in image_urls:
        file_path = "temp_image.png"  # Download image locally
        os.system(f"curl -o {file_path} {url}")
        raw_text = run_ocr_with_prompt(file_path, "Extract the full text from the document.")
        for line in raw_text.split("\n"):
            sanitized_line = sanitize_text(line.strip())
            if sanitized_line:
                all_raw_data.append({"Line": sanitized_line})
        extracted_fields_df = extract_fields(document_type, file_path)
        all_extracted_data.append(extracted_fields_df)
    raw_data_df = pd.DataFrame(all_raw_data)
    extracted_data_df = pd.concat(all_extracted_data, ignore_index=True) if all_extracted_data else pd.DataFrame()
    return raw_data_df, extracted_data_df

# Gradio interface
def interface(folder, limit, document_type):
    message, image_urls = fetch_images(folder, limit)
    if not image_urls:
        return pd.DataFrame(), pd.DataFrame(), None, message
    raw_data_df, extracted_data_df = process_ocr_for_images(document_type, image_urls)
    chart_path = generate_visualizations(extracted_data_df, document_type) if not extracted_data_df.empty else None
    return raw_data_df, extracted_data_df, chart_path, message

# Create the UI
with gr.Blocks() as ui:
    gr.Markdown("# Cloudinary OCR Integration")
    folder_input = gr.Dropdown(choices=FOLDERS, label="Select Folder")
    limit_input = gr.Number(label="Number of Images", value=5, precision=0)
    document_type_input = gr.Dropdown(choices=["Salary_Slip", "Bank_Statement", "Balance_sheet", "Invoice"], label="Document Type")
    fetch_button = gr.Button("Fetch and Process Images")
    output_message = gr.Textbox(label="Output Message", interactive=False)
    output_raw_data = gr.Dataframe(label="Full Extracted Text (Raw Data)")
    output_extracted_data = gr.Dataframe(label="Specific Extracted Data")
    output_chart = gr.Image(label="Charts (Pie & Bar)")
    fetch_button.click(interface, inputs=[folder_input, limit_input, document_type_input], outputs=[output_raw_data, output_extracted_data, output_chart, output_message])
ui.launch()
