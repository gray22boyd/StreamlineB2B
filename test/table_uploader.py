from utils.pdf_chunker import upload_to_supabase
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

def main():
    print("Starting PDF chunker")

    # Change this to your file OR directory
    target_path = Path(r"C:\Users\LukeH\Desktop\Python Project\StreamlineB2B\pdfs\Customer_Service Agent.pdf")

    try:
        pdf_file = target_path
    except Exception as e:
        print(f"Error: {e}")
        return
    
    print("Uploading to Supabase...")
    upload_to_supabase(pdf_file)
    print("Uploaded to Supabase")

    # Optionally upload to database
    # upload_to_supabase(pdf_file)

if __name__ == "__main__":
    main()

