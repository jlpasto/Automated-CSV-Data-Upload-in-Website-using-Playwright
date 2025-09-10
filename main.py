from playwright.sync_api import sync_playwright
import time
from urllib.parse import quote_plus
import json
import csv

BASE_URL = "https://hermes.touramigo.com"
USERNAME = "assistant"
PASSWORD = "kda.zhw6rwp!BNX0ftj"

def csv_to_json_list(csv_file_path):
    """
    Reads a CSV file and returns a list of dictionaries,
    where each dictionary represents a row with column names as keys.
    """
    with open(csv_file_path, mode='r', encoding='utf-8-sig', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        items = [dict(row) for row in reader]
    return items

def login_and_save_session():
    with sync_playwright() as p:
        # Launch headless browser
        
        #browser = p.chromium.launch(headless=True)
        browser = p.chromium.launch(headless=False, slow_mo=1000)
        context = browser.new_context()

        # Open new page
        page = context.new_page()

        # Go to login page
        page.goto("https://hermes.touramigo.com/login/form")

        # Fill credentials
        page.fill("input[name='username']", USERNAME)
        page.fill("input[name='password']", PASSWORD)

        # Click login button
        page.click("button[type='submit']")
        page.wait_for_load_state("networkidle")
        print("Login successful!")
        # Click Suppliers button and wait for menu
        page.click("button[name='collapsiblemenu-top-suppliers']")
        page.wait_for_selector("#suppliers-collapse", state="visible")
        # Navigate to Supplier Management
        page.goto(f"{BASE_URL}/partneradmin/suppliers")
        print("Navigated to Supplier Management!")
        # Save cookies & storage state for reuse after navigation
        context.storage_state(path="session.json")
        browser.close()

def reuse_session():
    with sync_playwright() as p:
        # Load session from file
        browser = p.chromium.launch(headless=False, slow_mo=1000)
        context = browser.new_context(storage_state="session.json")
        page = context.new_page()
        page.goto(BASE_URL)
        page.wait_for_load_state("networkidle")
        # Check if logged in by waiting for a logged-in element
        try:
            page.wait_for_selector("button[name='collapsiblemenu-top-suppliers']", timeout=5000)
            print("Session valid, logged in!")
            page.click("button[name='collapsiblemenu-top-suppliers']")
            page.wait_for_selector("#suppliers-collapse", state="visible")
            page.goto(f"{BASE_URL}/partneradmin/suppliers")
            print("Reused session and navigated to Supplier Management, title:", page.title())

           # Instruction: add this functionality
           # Fill in the form fields
            page.goto(f"{BASE_URL}/partneradmin/suppliers/add")
            # Fill in the form fields
            page.fill("input[name='name']", "Test Jhon3")
            page.select_option("select[name='supplier_type_id']", value="01899b129cf0c48a199ed258a3bf750c")  # Restaurant
            page.check("input[name='currency'][value='AUD']")
            page.check("input[name='active']")  # Status Active
            page.check("input[name='tax_status'][value='IsAdditional']")  # GST is Additional
            print("Filling due days field...")
            page.fill("input[name='due_days']", "0")
            page.check("input[name='due_days_when'][value='None']")
            page.check("input[name='due_days_date_option'][value='None']")
            #page.uncheck("input[name='due_days_exact_day']")
            page.uncheck("input[name='due_days_exact_day']")
            print("Due days field filled.")

            time.sleep(1)
            
            try:
                #page.wait_for_selector("textarea[name='about_us']", state="visible", timeout=10000)
                print("Filling about us and address fields...")
                # Wait for the TinyMCE iframe to be available
                page.wait_for_selector("iframe#about_us_ifr", timeout=10000)
                # Fill the TinyMCE editor via its iframe
                frame = page.frame_locator("iframe#about_us_ifr")
                frame.locator("body").fill("sample about")
                print("About Us field filled.")
            except Exception as e:
                print("Could not find About Us field:", e)
                # Output the page content in a txt file
                with open("page_content.txt", "w", encoding="utf-8") as f:
                    f.write(page.content())
                raise


            # Wait for address fields to be visible
            #page.click("input[name='address_1']") 
            #page.wait_for_selector("input[name='address_1']", timeout=5000)

            try:
                
                print("Filling address fields...")
                page.fill("input[name='address_1']", "91 Steinhardts Rd")
                page.fill("input[name='address_2']", "address line 2")
                page.fill("input[name='address_3']", "")
                page.fill("input[name='city']", "Moffatdale")
                page.fill("input[name='zip_code']", "4605")
                page.fill("input[name='region']", "QLD")
                page.select_option("select[name='country_id']", value="01797f27ff67abb13b970b9ce8a941a8")  # Australia
                page.fill("input[name='email']", "david@clovely.com.au")
                page.fill("input[name='office_phone_1']", "+61 405 298 285")
                page.fill("input[name='office_phone_2']", "")
                page.fill("input[name='website_url']", "https://www.clovely.com.au/")
               # page.fill("textarea[name='notes']", "Book for 1pm. Selection of platters and pizzas and a flight of 6 wine tastings")
                print("Address fields filled.")
            
            except Exception as e:
                print("Could not fill address fields:", e)
            
            page.click("button[name='_submit']")
            page.wait_for_load_state("networkidle")
            print("Clicked Add Item button and submitted the form.")

            time.sleep(1)
            # Add more fields as needed for your form structure
            # Submit the form
            #page.click("button.button-submit")
            print("Supplier form filled and submitted.")


            # if no error, proceed to Passenger List Setup
            # Provive error haandling here
            
            # Go to the supplier search page with the specified query parameters
            supplier_name = "Test Jhon3"
            supplier_name_query = quote_plus(supplier_name)
            search_url = f"{BASE_URL}/partneradmin/suppliers?name={supplier_name_query}&_submit=Search"
            page.goto(search_url)
            page.wait_for_load_state("networkidle")
            print("Navigated to supplier search page.")

            # Locate the first "Passenger List Setup" link
            passenger_list_link = page.locator('a:has-text("Passenger List Setup")').first

            # Get href attribute (URL)
            passenger_list_link_href = passenger_list_link.get_attribute("href")
            manifest_setup_url = f"{BASE_URL}{passenger_list_link_href}"
            print("First Passenger List Setup URL:", manifest_setup_url)        

            page.goto(manifest_setup_url)
            page.wait_for_load_state("networkidle")
            print("Navigated to Passenger List Setup page.")

            # Click the "Unselect All" button by its id
            page.click("button#select-all")
            print("Clicked 'Unselect All' button.")


            # JSON data as a string (replace with your actual source)
            json_data = '''
            {
                "Gender": "Yes",
                "Date of Birth": "No",
                "Weight": "No",
                "Medical Information": "No",
                "Age": "No",
                "Height": "No",
                "Dietary Requirements": "Yes",
                "Full Address": "No",
                "Contact Phone": "Yes",
                "Passport Information": "No",
                "Guide Notes": "No",
                "Contact Email": "No",
                "Emergency Contacts": "No",
                "Insurance Detail": "No",
                "Is Upgrade": "No",
                "Unit Number": "No",
                "Show Internal Rate Name": "No",
                "Duration": "No",
                "Include Package Name": "No",
                "Tour Extras": "No",
                "Include Sub Tours": "No",
                "Meeting Points": "No",
                "Insurance Policy": "No"
            }
            '''

            manifest_fields = {
                "Gender": "gender",
                "Date of Birth": "dob",
                "Weight": "weight",
                "Medical Information": "medical_information",
                "Age": "age",
                "Height": "height",
                "Dietary Requirements": "dietary_requirements",
                "Full Address": "full_address",
                "Contact Phone": "contact_phone",
                "Passport Information": "passport_information",
                "Guide Notes": "guide_notes",
                "Contact Email": "contact_email",
                "Emergency Contacts": "emergency_contacts",
                "Insurance Detail": "insurance_detail",
                "Is Upgrade": "is_upgrade",
                "Unit Number": "unit_number",
                "Show Internal Rate Name": "show_internal_rate_name",
                "Duration": "duration",
                "Include Package Name": "include_package_name",
                "Tour Extras": "tour_extras",
                "Include Sub Tours": "include_sub_tours",
                "Meeting Points": "meeting_points",
                "Insurance Policy": "insurance_policy"
            }

            data = json.loads(json_data)

            for label, field_name in manifest_fields.items():
                if data.get(label, "").strip().lower() == "yes":
                    try:
                        checkbox = page.locator(f"input[name='{field_name}']")
                        if not checkbox.is_checked():
                            checkbox.check()
                        print(f"Toggled '{label}' ON.")
                    except Exception as e:
                        print(f"Could not toggle '{label}':", e)

            # Click the "Save Configuration" button to submit the manifest setup form
            page.click("button[name='_submit']")
            page.wait_for_load_state("networkidle")
            print("Clicked 'Save Configuration' button and submitted manifest setup.")
            
        except Exception:
            print("Error: Failed to reuse session, or error in field filling.")
        context.storage_state(path="session.json")

        print("Waiting for 3 minutes before closing the browser...")
        time.sleep(180)
        browser.close()


if __name__ == "__main__":
    # First run login
    login_and_save_session()

    # Next run, reuse session
    reuse_session()
