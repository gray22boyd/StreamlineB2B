from utils.pdf_chunker import upload_to_supabase
from pathlib import Path
from dotenv import load_dotenv
from utils.supa import SupabaseClient
from data import staff_data, customers_data, inventory_data, maintenance_data, events_data, bookings_data

load_dotenv()

def uploade_pdf():
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
def upload_to_table(table_name, data):
    supabase = SupabaseClient(customer_schema="legends")
    supabase.upload_to_table(table_name=table_name, data=data)
    supabase.commit()
    supabase.close()
    print("Uploaded to table")

    # Upload all table data
def upload_all_table_data():
    upload_to_table(table_name="prop_staff_data", data=staff_data)
    upload_to_table(table_name="prop_customers_data", data=customers_data)
    upload_to_table(table_name="prop_inventory_data", data=inventory_data)
    upload_to_table(table_name="prop_maintenance_data", data=maintenance_data)
    upload_to_table(table_name="prop_events_data", data=events_data)
    upload_to_table(table_name="prop_bookings_data", data=bookings_data)

if __name__ == "__main__":
    upload_all_table_data()

