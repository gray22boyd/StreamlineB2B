import os
import psycopg2
from dotenv import load_dotenv
from utils.supa import SupabaseClient

load_dotenv()

def test_connection():
    try:
        supabase = SupabaseClient(customer_schema="legends")
        cur = supabase.cur

        print(f"✅ Connected to {supabase.customer_schema} Supabase!")

        supabase.commit()
        supabase.close()
        print("✅ Table created successfully!")

    except Exception as e:
        print(f"❌ Connection failed: {e}")

def test_gather_tables():
    supabase = SupabaseClient(customer_schema="legends")
    cur = supabase.cur
    result = cur.fetchall()
    supabase.close()
    return result



bookings_data = [
    "id int4",
    "customer_id int4",
    "booking_number text",
    "booking_date date",
    "total_amount float8",
]

events_data = [
    "id int4",
    "event_name text",
    "event_date date",
]

inventory_data = [
    "id int4",
    "item_name text",
    "item_description text",
    "item_price float8",
    "item_quantity int4",
    "item_category text",
    "reorder_point int4",
]

maintenance_data = [
    "id int4",
    "course_id int4",
    "date date",
    "work_performed text",
    "cost float8",
    "staff_id int4",
]

customers_data = [
    "id int4",
    "name text",
    "email text",
    "phone text",
    "address text",
    "city text",
    "state text",
]

staff_data = [
    "id int4",
    "name text",
    "email text",
    "phone text",
    "address text",
    "city text",
    "state text",
    "role text",
    "salary float8",
    "hire_date date",
    "department text",
    "manager_id int4",
]



def create_table(table_name, columns):
    supabase = SupabaseClient(customer_schema="legends")
    cur = supabase.cur
    supabase.create_table(table_name=table_name, columns=columns)
    supabase.commit()
    supabase.close()
    print("✅ Table created successfully!")



if __name__ == "__main__":
    create_table("prop_staff_data", staff_data)
    create_table("prop_customers_data", customers_data)
    create_table("prop_inventory_data", inventory_data)
    create_table("prop_maintenance_data", maintenance_data)
    create_table("prop_events_data", events_data)
    create_table("prop_bookings_data", bookings_data)
