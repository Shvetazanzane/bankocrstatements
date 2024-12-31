import os
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Cloudinary configuration
cloudinary.config(
    cloud_name="dtw4m0kkb",
    api_key="814949254963882",
    api_secret="E8eA1PQ40RZU1BRZUShZvDZePfU"
)

# Function to upload files from a local folder to Cloudinary folder
def upload_images_from_folder(local_folder, cloud_folder):
    # Get all image files from the local folder
    for filename in os.listdir(local_folder):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
            local_file_path = os.path.join(local_folder, filename)

            try:
                # Upload the image to Cloudinary
                print(f"Uploading {filename} from '{local_folder}' to Cloudinary folder '{cloud_folder}'...")
                response = cloudinary.uploader.upload(local_file_path, folder=cloud_folder)
                print(f"Uploaded: {response['secure_url']}")

            except Exception as e:
                print(f"Error uploading {filename}: {e}")

# List of folders to upload from and to
folders = {
    r'C:\Users\dell\Desktop\bankimages\SalarySlip': 'Salary_Slip',
    r'C:\Users\dell\Desktop\bankimages\BalanceSheet': 'Balance_sheet',
    r'C:\Users\dell\Desktop\bankimages\BankStatement': 'Bank_Statement',
    r'C:\Users\dell\Desktop\bankimages\Invoice': 'Invoice'
}

# Upload images from each folder to corresponding Cloudinary folder one by one
for local_folder, cloud_folder in folders.items():
    upload_images_from_folder(local_folder, cloud_folder)
