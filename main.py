from playwright.sync_api import sync_playwright
import time
from urllib.parse import quote_plus, urlparse
import json
import csv
from dotenv import load_dotenv
import os
import pandas as pd
from datetime import datetime
import re

load_dotenv()
BASE_URL = "https://hermes.touramigo.com"
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")

USERNAME = "assistant"
PASSWORD= "kda.zhw6rwp!BNX0ftj"


def parse_file_to_json_list(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".csv":
        return csv_to_json_list(file_path)
    elif ext in [".xls", ".xlsx"]:
        df = pd.read_excel(file_path)
        # Output the items as a JSON file
        df.to_json("output.json", orient="records", force_ascii=False, indent=2)
        return df.fillna("").to_dict(orient="records")
    else:
        raise ValueError("Unsupported file extension. Only .csv, .xls, .xlsx are allowed.")

def csv_to_json_list(csv_file_path):
    """
    Reads a CSV file and returns a list of dictionaries,
    where each dictionary represents a row with column names as keys.
    """
    with open(csv_file_path, mode='r', encoding='utf-8', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        items = [dict(row) for row in reader]

        # Output the items as a JSON file
        with open("output.json", "w", encoding="utf-8") as jsonfile:
            json.dump(items, jsonfile, ensure_ascii=False, indent=2)
      
    return items

def login(context, page):
    page.goto(f"{BASE_URL}/login/form")
    page.fill("input[name='username']", USERNAME)
    page.fill("input[name='password']", PASSWORD)
    page.click("button[type='submit']")
    page.wait_for_load_state("networkidle")
    context.storage_state(path="session.json")
    print("Logged in and session saved.")
    time.sleep(2)  # Wait for 2 seconds to ensure the page is fully loaded

def is_logged_in(page):
    page.goto(BASE_URL)
    try:
        page.wait_for_selector("div.salutation-container", timeout=5000)
        return True
    except Exception:
        return False

def is_valid_url(url):
    """
    Check if the provided string is a valid URL
    """
    if not url or not isinstance(url, str):
        return False
    
    # Strip whitespace
    url = url.strip()
    
    # If empty after stripping, it's not valid
    if not url:
        return False
    
    try:
        result = urlparse(url)
        # Check if scheme and netloc are present (basic URL structure)
        return all([result.scheme, result.netloc])
    except Exception:
        return False

currency_map = {
    "AUD": "AUD",
    "Euro": "EUR",
    "New Zealand Dollar": "NZD",
    "UK": "GBP",
    "Yen": "JPY"
}

supplier_type_map = {
    "Accommodation": "017c35a25841670347fc90d62663d34b",
    "Activities and Excursions": "017c35a42cb196a6635039fe46a96142",
    "Airline": "017c35a481183b183deec19115845fbf",
    "Car Rental": "017c35a4abfdb8d6f59a7ee3c7de3fea",
    "Coach": "017c35a2d5ef8c1f4e623b917c293179",
    "Cruise": "017c35a274fc7f3358ac03a377e3b4e8",
    "Ground Handler": "017c35abacc5d6528af4ad978f7e19e1",
    "Guide": "0197885596074ed1f0fff2c7327b201a",
    "Insurance": "017c35a52a4c6caa592b7dacb46160b2",
    "Miscellaneous": "017c35a2b57bb993addc4bf61f5d1498",
    "Restaurant": "01899b129cf0c48a199ed258a3bf750c",
    "Tour Operator": "017a0c229cc45186d8e080572b7f582f",
    "Transport and Logistics": "017c35a28fb5fc7473061e834959db52"
}

gst_status_map = {
    "No GST": "NoTax",
    "Inclusive of GST": "Inclusive",
    "GST is Additional": "IsAdditional"
}


# Country mapping
country_map = {
    "Afghanistan": "01797f27ff672165c826f45d3bdd9a45",
    "Åland Islands": "01797f27ff671e4701ce0456f6fa1d63",
    "Albania": "01797f27ff678c7f4445526825240efa",
    "Algeria": "01797f27ff67bf52d21181b0b0448986",
    "American Samoa": "01797f27ff672356d85007553cb5e3a6",
    "Andorra": "01797f27ff67b50c1a62743312ae2350",
    "Angola": "01797f27ff67c9b287d32dd575a45f9a",
    "Anguilla": "01797f27ff67666713d26593b9299936",
    "Antarctica": "01797f27ff67cc2f95ba5170c50a97d6",
    "Antigua and Barbuda": "01797f27ff673e62104553fe56238c5c",
    "Argentina": "01797f27ff6784699431cac6b3f04093",
    "Armenia": "01797f27ff67641912484fa45426de75",
    "Aruba": "01797f27ff6731e8b866202dedca5b53",
    "Australia": "01797f27ff67abb13b970b9ce8a941a8",
    "Austria": "01797f27ff67f6cb8d775db74620a327",
    "Azerbaijan": "01797f27ff67834718fafd8de54021b0",
    "Bahamas": "01797f27ff6794b5292db5a6f2834eeb",
    "Bahrain": "01797f27ff6781466255a26a05466f47",
    "Bangladesh": "01797f27ff671a1fa0b3645ef1291f68",
    "Barbados": "01797f27ff67dff0edcaa50fcb005acc",
    "Belarus": "01797f27ff67d8225bc9e8be13ff9541",
    "Belgium": "01797f27ff67551f4f9f3bda035e1425",
    "Belize": "01797f27ff67e1046e585fa4f058e9c8",
    "Benin": "01797f27ff67113f9291fa19f3f53d82",
    "Bermuda": "01797f27ff674c09621448f26e498efb",
    "Bhutan": "01797f27ff676cbd128f3e81395a6b78",
    "Bolivia, Plurinational State of": "01797f27ff677fb3d09c7426ede6fb3d",
    "Bonaire, Sint Eustatius and Saba": "01797f27ff67ec13db5d370775bdcb68",
    "Bosnia and Herzegovina": "01797f27ff679d718126eaf284444066",
    "Botswana": "01797f27ff67ca8f57cdc5fb2f7fa721",
    "Bouvet Island": "01797f27ff672d046a33c6c5c0f4308b",
    "Brazil": "01797f27ff67a5c750d3c0a36872848e",
    "British Indian Ocean Territory": "01797f27ff679b3496cad9795bc234d9",
    "Brunei Darussalam": "01797f27ff6797a2a1f359e470714b6d",
    "Bulgaria": "01797f27ff670ff7b8021963c4a5518e",
    "Burkina Faso": "01797f27ff677dd17671d8b378689a16",
    "Burundi": "01797f27ff6724b482b23b25939f9770",
    "Cambodia": "01797f27ff67ed56c1e6634ef1a7fdbd",
    "Cameroon": "01797f27ff6792765c7885a1b079789e",
    "Canada": "01797f27ff67a28702a2948c31dddd69",
    "Cape Verde": "01797f27ff67c593e46aae1d6cb7b909",
    "Cayman Islands": "01797f27ff681cb3a98c3b35a1185e07",
    "Central African Republic": "01797f27ff68a07b63d2a4c65420ccf1",
    "Chad": "01797f27ff68c6e41a12ce22b759e0e5",
    "Chile": "01797f27ff68ab583f7631759c2eb5de",
    "China": "01797f27ff682af9ee8c19bf4427196f",
    "Christmas Island": "01797f27ff68917149af9a7666ae38d0",
    "Cocos (Keeling) Islands": "01797f27ff68186c5cebe0de2e8d06f2",
    "Colombia": "01797f27ff6847db7e6a352018a4cf5e",
    "Comoros": "01797f27ff68cde082f0bc9e07586942",
    "Congo": "01797f27ff68ddb24f4e35334d9557a2",
    "Congo, the Democratic Republic of the": "01797f27ff6820ae31461ebf37f8c38a",
    "Cook Islands": "01797f27ff689f294499288ee9dd9bbd",
    "Costa Rica": "01797f27ff685f1c8ef22d704df89dfb",
    "Côte d'Ivoire": "01797f27ff689bd9da83a5ddf2d8bbfb",
    "Croatia": "01797f27ff68a8db90c979da7e32d709",
    "Cuba": "01797f27ff68e3d45b8ea259d09c4685",
    "Curaçao": "01797f27ff6805015f00561a93a8d92a",
    "Cyprus": "01797f27ff68455cb29ce6dda1623c8d",
    "Czech Republic": "01797f27ff683e61022e101c2ca337ff",
    "Denmark": "01797f27ff68788c99e6af1a3a241ab2",
    "Djibouti": "01797f27ff68df64c691f8030c311346",
    "Dominica": "01797f27ff689573838c9510a2d4a6b6",
    "Dominican Republic": "01797f27ff680aca403d99f99889c6a8",
    "Ecuador": "01797f27ff684be16ce4da41aa5aeaf9",
    "Egypt": "01797f27ff6810e19dbdd7dd4f78f742",
    "El Salvador": "01797f27ff680660139c29b295ae299a",
    "Equatorial Guinea": "01797f27ff68e0220dcf5b7a7fdb5ee6",
    "Eritrea": "01797f27ff68cb9bd5e965713c7a8e92",
    "Estonia": "01797f27ff68c8781bf8b2262667808b",
    "Ethiopia": "01797f27ff68bf2bfd47a25a9366511b",
    "Falkland Islands (Malvinas)": "01797f27ff6855bac93984a5560a0874",
    "Faroe Islands": "01797f27ff68acba9f254a70fd9b03ad",
    "Fiji": "01797f27ff68d549daa9e219bde3afca",
    "Finland": "01797f27ff689e22f43dbcdc80f7fd36",
    "France": "01797f27ff68ba740558e65c746e18b3",
    "French Guiana": "01797f27ff6885e67208f9150fa8e854",
    "French Polynesia": "01797f27ff68ef92a5463d3b776999fb",
    "French Southern Territories": "01797f27ff68e8bf400b36452fdbf48b",
    "Gabon": "01797f27ff68b2158a16abe204cbdb7f",
    "Gambia": "01797f27ff689fe91b5d975d3b566a98",
    "Georgia": "01797f27ff68e96089b2fc80cf9c57ec",
    "Germany": "01797f27ff689374f6aa496edba96155",
    "Ghana": "01797f27ff68377265f0337eedf75b4c",
    "Gibraltar": "01797f27ff68709f4860812fa3e7b478",
    "Greece": "01797f27ff68f2dd03334ccf83fdf198",
    "Greenland": "01797f27ff682617e8de3657d299354d",
    "Grenada": "01797f27ff68b1d05abdc2c6f2d771ba",
    "Guadeloupe": "01797f27ff68a1719bba9b1fa21e01a1",
    "Guam": "01797f27ff686befe9806b39465e701b",
    "Guatemala": "01797f27ff68a50051e8d7a6195e22f6",
    "Guernsey": "01797f27ff68f6b018d925578af260db",
    "Guinea": "01797f27ff68b583b04a9b7b0ffa21bf",
    "Guinea-Bissau": "01797f27ff68fa08b00ccf320dcdee40",
    "Guyana": "01797f27ff6868dba1d2bad645da43d4",
    "Haiti": "01797f27ff688e503651f7d66221c76d",
    "Heard Island and McDonald Islands": "01797f27ff68b9faa42551cac47aac11",
    "Holy See (Vatican City State)": "01797f27ff68b4765f8708bdc119eb50",
    "Honduras": "01797f27ff68123e81ef074c5934cc58",
    "Hong Kong": "01797f27ff68b4f37fe60df24725ccec",
    "Hungary": "01797f27ff68ac15a06cdc3e0b051cec",
    "Iceland": "01797f27ff68ebb688715b126aad9bb3",
    "India": "01797f27ff68daf261d5af5d5541bf32",
    "Indonesia": "01797f27ff68de6e76defe164d525ab5",
    "Iran, Islamic Republic of": "01797f27ff68efe8cce493142adcde89",
    "Iraq": "01797f27ff68404f011f58564fc29a8a",
    "Ireland": "01797f27ff68357deb6069d649871ad9",
    "Isle of Man": "01797f27ff68b53bd72f83951c976cd8",
    "Israel": "01797f27ff689fb8c25ad8847f126cd4",
    "Italy": "01797f27ff68e67c120b771b4f28de5c",
    "Jamaica": "01797f27ff68068c448b0a3117af7bf6",
    "Japan": "01797f27ff68c527afb4474479c18983",
    "Jersey": "01797f27ff694cfe4cff80db69ddfc49",
    "Jordan": "01797f27ff69e35a1aded8574afc3f6e",
    "Kazakhstan": "01797f27ff6990185e836431656f961a",
    "Kenya": "01797f27ff69ff4a150248e5a1786792",
    "Kiribati": "01797f27ff69cce2c6f9006644e1f182",
    "Korea, Democratic People's Republic of": "01797f27ff69a37070af1e1c9b289429",
    "Korea, Republic of": "01797f27ff6909a8c56a646c7dacaf64",
    "Kuwait": "01797f27ff69db2220a9588365c56c6c",
    "Kyrgyzstan": "01797f27ff6969538d22f8be5e7377ff",
    "Lao People's Democratic Republic": "01797f27ff69ac559a737f1fecc0dabc",
    "Latvia": "01797f27ff6997eaeec1484ccd502343",
    "Lebanon": "01797f27ff6972028aebe2a4f370baf3",
    "Lesotho": "01797f27ff69ed96f5ae87134e921290",
    "Liberia": "01797f27ff694c8248d1036be3e815da",
    "Libya": "01797f27ff696bcd7c3b7eeca61a7f98",
    "Liechtenstein": "01797f27ff69e335ccbebe8bd60b0c4d",
    "Lithuania": "01797f27ff69809595e0a6cd7dd02480",
    "Luxembourg": "01797f27ff6973963d15e373359b8fba",
    "Macao": "01797f27ff69eefca733f5328d9b8aef",
    "Madagascar": "01797f27ff6913b233c7370a4687e2c7",
    "Malawi": "01797f27ff6997aa837bac3907c54850",
    "Malaysia": "01797f27ff690d89ca86436b0f03b664",
    "Maldives": "01797f27ff69af8d35e6060947c90ddc",
    "Mali": "01797f27ff695e652d5fa95165f9b09d",
    "Malta": "01797f27ff691d9d01a1b09aa012d708",
    "Marshall Islands": "01797f27ff69fb1aacc7ea2d6e90a0fe",
    "Martinique": "01797f27ff692beb719d5970ab902113",
    "Mauritania": "01797f27ff6911c5cc85d9c061db3103",
    "Mauritius": "01797f27ff69fa3f6038042c36461038",
    "Mayotte": "01797f27ff692e0a61893ac8d710f624",
    "Mexico": "01797f27ff698633a6df9a17d7b7279b",
    "Micronesia, Federated States of": "01797f27ff69bb996a9a536d5ea56d18",
    "Moldova, Republic of": "01797f27ff69ab42aea5fcbf0abbf2c0",
    "Monaco": "01797f27ff69427320ee9aa320e215bc",
    "Mongolia": "01797f27ff6965118be3b3dabdd7c1a4",
    "Montenegro": "01797f27ff69af96702e68cb9e62ad6c",
    "Montserrat": "01797f27ff6900ddc825e7afcde85381",
    "Morocco": "01797f27ff6915d7d6bd035af55715c5",
    "Mozambique": "01797f27ff69ee134c8854f49220f48a",
    "Myanmar": "01797f27ff6982746982e79fa9074c29",
    "Namibia": "01797f27ff69b00698ad9fcbb980f699",
    "Nauru": "01797f27ff6961743177cffdbf6e9607",
    "Nepal": "01797f27ff698bd12fb00b495cde6475",
    "Netherlands": "01797f27ff6944956ca1404b98642ecf",
    "New Caledonia": "01797f27ff698e6f149d9513a39a3173",
    "New Zealand": "01797f27ff699e07463ba7169e431b25",
    "Nicaragua": "01797f27ff69253c62c0a7fd3c4fc953",
    "Niger": "01797f27ff69e685e972ef1fd4c97582",
    "Nigeria": "01797f27ff69b5f309d52a9346129aad",
    "Niue": "01797f27ff690ab0f71e161be2ff06ef",
    "Norfolk Island": "01797f27ff69252792a44e82fc969e49",
    "North Macedonia": "01797f27ff69c38cde2d5ff1f3f8d225",
    "Northern Mariana Islands": "01797f27ff69eb94be13bd6d51ab4d68",
    "Norway": "01797f27ff691171f04bef239c3e70f8",
    "Oman": "01797f27ff696f235acd23a12778fa9d",
    "Pakistan": "01797f27ff69a234deebf725ac5ed755",
    "Palau": "01797f27ff69981e6f22ae81674195ad",
    "Palestine, State of": "01797f27ff69865c67e2fd20fa966786",
    "Panama": "01797f27ff69b113b7d70eaf85012ca5",
    "Papua New Guinea": "01797f27ff696614f006defd996fe94f",
    "Paraguay": "01797f27ff69c188712ca7c06711e011",
    "Peru": "01797f27ff69e9c6a3355356330311a9",
    "Philippines": "01797f27ff69982593d3ff5c1b31f6db",
    "Pitcairn": "01797f27ff69cd67d08f893e4b073df4",
    "Poland": "01797f27ff693661bfbbcc248f892a95",
    "Portugal": "01797f27ff69bbdd10035a50c7bed8f5",
    "Puerto Rico": "01797f27ff6936dd4125620bf2a797fa",
    "Qatar": "01797f27ff69dc7ca92da03e63b0aabb",
    "Réunion": "01797f27ff696294b1feb1cbcaa543a0",
    "Romania": "01797f27ff6909a0eff66017695cd3dd",
    "Russian Federation": "01797f27ff6963d1e769e09193db1b13",
    "Rwanda": "01797f27ff69e0bdf27fae989412bd65",
    "Saint Barthélemy": "01797f27ff6ab9a747060a04f43c404b",
    "Saint Helena, Ascension and Tristan da Cunha": "01797f27ff6a516a995c6aeeb48bd59f",
    "Saint Kitts and Nevis": "01797f27ff6ad2d33a8979d0ee7d0cc7",
    "Saint Lucia": "01797f27ff6a724033ec66e265d75272",
    "Saint Martin (French part)": "01797f27ff6ab57bc876c96594d5febc",
    "Saint Pierre and Miquelon": "01797f27ff6a44b9200595bd675f2c76",
    "Saint Vincent and the Grenadines": "01797f27ff6a409b509f8947c6bbdbd2",
    "Samoa": "01797f27ff6a0b809a7222ad3f0c28e1",
    "San Marino": "01797f27ff6ad4d28a83e6c880e9438b",
    "Sao Tome and Principe": "01797f27ff6a5cb7c830852233ff3adb",
    "Saudi Arabia": "01797f27ff6a79113ce66a7695556ad8",
    "Senegal": "01797f27ff6ae327ddd2e9db44338b1c",
    "Serbia": "01797f27ff6adf4bd4f90f954c905fbe",
    "Seychelles": "01797f27ff6abc89189c89493f5935dd",
    "Sierra Leone": "01797f27ff6a6915991998ca28850a47",
    "Singapore": "01797f27ff6af035aacaca454e1a3a8c",
    "Sint Maarten (Dutch part)": "01797f27ff6a751c5eca04f66c33d8c5",
    "Slovakia": "01797f27ff6aed12e9d60796b4d15b3e",
    "Slovenia": "01797f27ff6a9bb5b42a05a3ccfa7ff5",
    "Solomon Islands": "01797f27ff6a96cf2053c6f54c318266",
    "Somalia": "01797f27ff6af355e4303d887fa57861",
    "South Africa": "01797f27ff6aa6ad414fe879afc425e2",
    "South Georgia and the South Sandwich Islands": "01797f27ff6a4b0bec137961bd3302a9",
    "South Sudan": "01797f27ff6ae8be7bc95fa9a78eaebb",
    "Spain": "01797f27ff6a7cbce0591033bb2f0f30",
    "Sri Lanka": "01797f27ff6a0d497c651fe5c22aa34b",
    "Sudan": "01797f27ff6ad0cda5b10814bbea3df1",
    "Suriname": "01797f27ff6a3db739ab5286c4548fcc",
    "Svalbard and Jan Mayen": "01797f27ff6a07aad3e18d0a52ae4308",
    "Swaziland": "01797f27ff6a537dd569beacf463ff84",
    "Sweden": "01797f27ff6aeed5e498ee42b3fd98c8",
    "Switzerland": "01797f27ff6a347af4bbec99483e6029",
    "Syrian Arab Republic": "01797f27ff6a04b4976005d12755c7fb",
    "Taiwan, Province of China": "01797f27ff6adfd88349799d07056d2a",
    "Tajikistan": "01797f27ff6ae0f9028e6ff426d78dd8",
    "Tanzania, United Republic of": "01797f27ff6a42d3b1fc02b05961b76b",
    "Thailand": "01797f27ff6a8bd7f54f961b93f6f442",
    "Timor-Leste": "01797f27ff6a01954e4ae6f42658e421",
    "Togo": "01797f27ff6aafbfab8785c05d218c24",
    "Tokelau": "01797f27ff6a13188d9c550b371538fe",
    "Tonga": "01797f27ff6a186e8ef36ac32730312f",
    "Trinidad and Tobago": "01797f27ff6a46c2974051e8a5fda9ab",
    "Tunisia": "01797f27ff6ab533749a47b72ee69087",
    "Turkey": "01797f27ff6a8bf8c6b6a92b9cb463c5",
    "Turkmenistan": "01797f27ff6a902ecff210b5b36f911c",
    "Turks and Caicos Islands": "01797f27ff6a56dcb91ffc800dffea92",
    "Tuvalu": "01797f27ff6a18737ed2259f32a070c1",
    "Uganda": "01797f27ff6ae40807aeee016736fd49",
    "Ukraine": "01797f27ff6af02ef7c7ecd194f9a0b0",
    "United Arab Emirates": "01797f27ff6a57267e71a979c0bf8cd5",
    "United Kingdom": "01797f27ff6a0b55533d2aa0983debe0",
    "United States": "01797f27ff6a3b20e48f390d975de768",
    "United States Minor Outlying Islands": "01797f27ff6ad3b91fd6c60060424c53",
    "Uruguay": "01797f27ff6a4c03bceac20f3e1e7c85",
    "Uzbekistan": "01797f27ff6a2198cca3e12ad254f1df",
    "Vanuatu": "01797f27ff6af3140da05da37026c7f7",
    "Venezuela, Bolivarian Republic of": "01797f27ff6ac45ee67843a379572909",
    "Viet Nam": "01797f27ff6a570e277d5119e69c8949",
    "Virgin Islands, British": "01797f27ff6aee2345de8990165cd9ad",
    "Virgin Islands, U.S.": "01797f27ff6aa1425a30752dcaba41cc",
    "Wallis and Futuna": "01797f27ff6a3476ea62f2a4aee30ab2",
    "Western Sahara": "01797f27ff6a1eb9dfbb3c2bfa010432",
    "Yemen": "01797f27ff6af7cf5612334227ab326e",
    "Zambia": "01797f27ff6a4c566d08f4a830a3e723",
    "Zimbabwe": "01797f27ff6af8474bb516bbd4353c98"
}

# Simple email validation function
def is_valid_email(email):
    # Basic regex to check format like example@domain.com
    return bool(re.match(r"[^@]+@[^@]+\.[^@]+", email))

def fill_supplier_form(page, record, error_fields):
    page.goto(f"{BASE_URL}/partneradmin/suppliers/add")
    # Map CSV columns to form fields
    page.fill("input[name='name']", record.get("Name", ""))
        
    supplier_type_label = record.get("Supplier Type", "Restaurant")
    supplier_type_value = supplier_type_map.get(supplier_type_label, "01899b129cf0c48a199ed258a3bf750c")  # Default to Restaurant
    page.select_option("select[name='supplier_type_id']", value=supplier_type_value)
    
    # Dynamic currency selection
    currency_raw = record.get("Currencies", "").strip()
    if currency_raw == "":
        # add to error fields
        error_fields.append("Currencies replaced by AUD")
    mapped_currency = currency_map.get(currency_raw, "AUD")  # Default to AUD if not found
    page.check(f"input[name='currency'][value='{mapped_currency}']")

    # Status Active/Inactive based on CSV "Status" column
    status = record.get("Status", "Active").strip().lower()
    if status == "active":
        page.check("input[name='active']")
    else:
        page.uncheck("input[name='active']")
    
    # GST Status mapping

    gst_status_label = record.get("GST Status", "GST is Additional")
    gst_status_value = gst_status_map.get(gst_status_label, "IsAdditional")
    page.check(f"input[name='tax_status'][value='{gst_status_value}']")


    due_days_value = record.get("Due Days", "")
    due_days_value = str(due_days_value).strip() or "0"
    page.fill("input[name='due_days']", due_days_value)


    # Mapping for "When" radio buttons
    due_days_when_map = {
        "Not Set": "None",
        "Before": "Before",
        "After": "After"
    }
    due_days_when_label = record.get("Due Days When", "").strip() or "Not Set"
    due_days_when_value = str(due_days_when_map.get(due_days_when_label, "None")) or "None"
    #print("Due Days When Value:", due_days_when_value)  # Debugging line
    page.check(f"input[name='due_days_when'][value='{due_days_when_value}']")


    # Mapping for "Date Option" radio buttons
    due_days_date_option_map = {
        "Not Set": "None",
        "Booking Date": "BookingDate",
        "Start of Tour": "TourStart",
        "End of Tour": "TourEnd"
    }
    due_days_date_option_label = record.get("Due Days Date Option", "").strip() or "Not Set"
    due_days_date_option_value = str(due_days_date_option_map.get(due_days_date_option_label, "None")) or "None"
    #print("Due Days Date Option Value:", due_days_date_option_value)  # Debugging line
    page.check(f"input[name='due_days_date_option'][value='{due_days_date_option_value}']")
    
    # Handle "Exact Day" checkbox based on "Exact Day" field
    exact_day_value = record.get("Exact Day", "").strip()
    if not exact_day_value:
        page.uncheck("input[name='due_days_exact_day']")
    elif exact_day_value.lower() == "active":
        page.check("input[name='due_days_exact_day']")
    
    # About Us (TinyMCE)
    try:
        page.wait_for_selector("iframe#about_us_ifr", timeout=10000)
        frame = page.frame_locator("iframe#about_us_ifr")
        about_us_value = record.get("About Us", "").strip()
        notes_value = record.get("Notes", "").strip()
        joined_value = " ".join(filter(None, [about_us_value, notes_value])).strip()
        frame.locator("body").fill(joined_value)
    except Exception as e:
        print("Could not fill About Us:", e)


    # Address fields
    page.fill("input[name='address_1']", str(record.get("Address 1", "")))
    page.fill("input[name='address_2']", str(record.get("Address 2", "")))
    page.fill("input[name='address_3']", str(record.get("Address 3", "")))
    page.fill("input[name='city']", str(record.get("City", "")))
    page.fill("input[name='zip_code']", str(record.get("Zip Code", "")))
    page.fill("input[name='region']", str(record.get("State/Province/Region", "")))

    # Country selection
    country_label = record.get("Country", "Australia").strip()
    country_value = country_map.get(country_label, "01797f27ff67abb13b970b9ce8a941a8")  # Default to Australia
    page.select_option("select[name='country_id']", value=country_value)
    
   
    # page.fill("input[name='email']", record.get("Email", ""))

    # Get email from record
    email = record.get("Email", "").strip()

    if is_valid_email(email):
        page.fill("input[name='email']", email)
        #print(f"Using provided email: {email}")
    else:
        fallback_email = ""  # you can change this
        page.fill("input[name='email']", fallback_email)
        #print(f"Invalid or empty email provided, using fallback: {fallback_email}")
        # add email to error fields if original value exists
        if email != "":
            error_fields.append("email")


    page.fill("input[name='office_phone_1']", str(record.get("Office Phone 1", "")))
    page.fill("input[name='office_phone_2']", str(record.get("Office Phone 2", "")))

    # Website URL validation and filling
    website_url = record.get("Website URL", "").strip()
    if is_valid_url(website_url):
        page.fill("input[name='website_url']", website_url)
        #print(f"Using provided website URL: {website_url}")
    else:
        fallback_url = "https://tourdevines.com.au/"
        page.fill("input[name='website_url']", fallback_url)
        #print(f"Invalid or empty website URL provided, using fallback: {fallback_url}")
        # add website utl to error fields
        if website_url != "":
            error_fields.append("website_url")

    # Add more mappings as needed
    page.click("button[name='_submit']")
    page.wait_for_load_state("networkidle")
    time.sleep(5) #  Wait for 5 seconds to ensure processing

    # if submiteed successfully, return error fields as none
    try:

        success_element = page.locator("div.alert.alert-success", has_text="The new item has been added successfully.")
        success_element.wait_for(state="attached", timeout=2000)  # wait max 3s
        print(f"Submitted supplier: {record.get('Name', '')}")

        if success_element.is_visible():
            pass
            #print("✅ Success message found!")
        else:
            pass
            #print("❌ Success message not found.")
    except Exception as e:
        #print("❌ Could not verify success message:", e)
        return error_fields
    return error_fields

def fill_manifest_fields(page, manifest_data):
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
    for label, field_name in manifest_fields.items():
        if manifest_data.get(label, "").strip().lower() == "yes":
            try:
                checkbox = page.locator(f"input[name='{field_name}']")
                if not checkbox.is_checked():
                    checkbox.check()
                #print(f"Toggled '{label}' ON.")
            except Exception as e:
                
                #print(f"Could not toggle '{label}':", e)
                return False
    page.click("button[name='_submit']")
    page.wait_for_load_state("networkidle")
    time.sleep(6)  # Wait for 2 minutes to ensure processing
    print("Clicked 'Save Configuration' button and submitted manifest setup.")
    return True

def initialize_log_file():
    """Initialize the log CSV file with headers"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"logs_{timestamp}.csv"
    
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    log_filepath = os.path.join("logs", log_filename)
    
    # Write headers
    with open(log_filepath, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Supplier Name', 'Status', 'Timestamp', 'Error Message'])
    
    print(f"Log file initialized: {log_filepath}")
    return log_filepath

def log_record_status(log_filepath, supplier_name, status, error_message=""):
    """Log the status of a supplier record processing"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open(log_filepath, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([supplier_name, status, timestamp, error_message])
    
    print(f"Logged {status} for supplier: {supplier_name}")

def main():
    # Initialize logging
    log_filepath = initialize_log_file()

    # Path to the folder containing the CSV
    csv_folder = os.path.join(os.path.dirname(__file__), "csv")

    # Get the first file in the folder
    csv_files = [f for f in os.listdir(csv_folder) if f.endswith(".csv")]

    if not csv_files:
        raise FileNotFoundError("No CSV file found in the 'csv' folder.")
    CSV_FILE_PATH = os.path.join(csv_folder, csv_files[0])

    # CSV_FILE_PATH = "test.csv"  # Update with your CSV/Excel file name

    records = parse_file_to_json_list(CSV_FILE_PATH)
    error_fields = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=200)
        try:
            context = browser.new_context(storage_state="session.json")
        except Exception:
            context = browser.new_context()
        page = context.new_page()
        if not is_logged_in(page):
            login(context, page)
        
        for record in records:
            supplier_name = record.get("Name", "")
            name_exists = False
            if supplier_name != "" or supplier_name != "None":
                try:
                    # Process supplier form
                    error_fields = fill_supplier_form(page, record, error_fields)

                    #formgroup_name
                    try:

                        # Locate the parent
                        parent = page.locator("#formgroup_name")
                        parent.wait_for(state="attached", timeout=2000)  # wait max 3s
                        #print("✅ Parent found")

                        # Check if it has at least one matching child
                        has_invalid = parent.locator(".invalid-feedback.invalid-name", has_text="Supplier names must be unique.").count() > 0


                        if has_invalid:
                            #print("❌  Supplier names must be unique.")
                            name_exists = True
                            # log the error
                            log_record_status(log_filepath, supplier_name, "Failed", "Message: Supplier details already exist")
                            # go to next record
                            #continue

                    except Exception as e:
                        print("✅ No error checking in name field")



                    try:

                        # Locate the parent
                        parent = page.locator("#formgroup_office_phone_1")
                        parent.wait_for(state="attached", timeout=2000)  # wait max 3s
                        #print("✅ Parent found")

                        # Check if it has at least one matching child
                        has_invalid = parent.locator(".invalid-feedback.invalid-office_phone_1", has_text="That does not appear to be a valid").count() > 0

                        if has_invalid:
                            #print("❌ Invalid phone number feedback is present")
                            # fill the phone number with blank
                            page.fill("input[name='office_phone_1']", "")
                            # add office_phone_1 to array missing_fields
                            error_fields.append("office_phone_1")

                        else:
                            pass
                            #print("✅ No invalid feedback under formgroup_office_phone_1")

                    except Exception as e:
                        print("Exception checking phone number1 feedback:", e)

                    try:

                        # Locate the parent
                        parent = page.locator("#formgroup_office_phone_2")
                        parent.wait_for(state="attached", timeout=2000)  # wait max 3s
                        #print("✅ Parent found")

                        # Check if it has at least one matching child
                        has_invalid = parent.locator(".invalid-feedback.invalid-office_phone_2", has_text="That does not appear to be a valid").count() > 0

                        if has_invalid:
                            #print("❌ Invalid phone number feedback is present")
                            # fill the phone number with blank
                            page.fill("input[name='office_phone_2']", "")
                            # add office_phone_2 to array missing_fields
                            error_fields.append("office_phone_2")

                        else:
                            pass
                            #print("✅ No invalid feedback under formgroup_office_phone_2")

                    except Exception as e:
                        print("Exception checking phone number1 feedback:", e)
                   
                    # check if has an error
                  
                    if len(error_fields) > 0 and not name_exists:
                        # retry submission
                        #print(f"Retrying to Submit supplier: {record.get('Name', '')}")
                        page.click("button[name='_submit']")
                        page.wait_for_load_state("networkidle")
                        time.sleep(5)  # Wait for 5secs to ensure processing

                        # if submiteed successfully, 
                        try:

                            success_element = page.locator("div.alert.alert-success", has_text="The new item has been added successfully.")
                            success_element.wait_for(state="attached", timeout=2000)  # wait max 3s

                            if success_element.is_visible():
                                #print("✅ Success message found!")
                                log_record_status(log_filepath, supplier_name, "Success", "Supplier Details Added. No error fields found")
                            else:
                                #print("❌ Success message not found.")
                                log_record_status(log_filepath, supplier_name, "Failed", "Supplier Details not added. Error fields: " + ", ".join(error_fields))

                                error_fields = []
                                continue

                        except Exception as e:
                            print("Could not find success message after resubmission:", e)
                            log_record_status(log_filepath, supplier_name, "Failed", "Supplier Details not added. Error fields: " + ", ".join(error_fields))
                            error_fields = []
                            continue
                        


                    else:
                        print("✅ No error fields found")
                        
                       

                    # After supplier is added, go to search page and setup manifest
                    print(f"Setting up passenger for supplier: {supplier_name}")
                    supplier_name_query = quote_plus(supplier_name)
                    search_url = f"{BASE_URL}/partneradmin/suppliers?name={supplier_name_query}&_submit=Search"
                    page.goto(search_url)
                    page.wait_for_load_state("networkidle")

                    first_row_name = ""
                    if page.locator("#twdatatable").count() > 0:
                        #print("✅ Table exists")

                        # Get the first row's Name column (2nd <td>)
                        first_row_name = page.locator("#twdatatable tbody tr:first-child td:nth-child(2) a").inner_text()
                        #print("First row Name:", first_row_name)

                    else:
                        #print("❌ Table not found")
                        error_fields = []
                        continue



                    try:
                        passenger_list_link = page.locator('a:has-text("Passenger List Setup")').first
                        passenger_list_link.wait_for(state="attached", timeout=5000)  # wait max 3s

                        if not passenger_list_link:
                            #print("No 'Passenger List Setup' link found for supplier:", supplier_name)
                            log_record_status(log_filepath, supplier_name, "Failed", "Passenger details not updated")
                            error_fields = []
                            continue
                        else:
                            #print("'Passenger List Setup' link found.")
                            if first_row_name != supplier_name:
                                #print(f"Supplier name mismatch. Expected: {supplier_name}, Found: {first_row_name}")
                                log_record_status(log_filepath, supplier_name, "Failed", "Supplier name mismatch after search")
                                error_fields = []
                                continue
                            else:
                                #print("Supplier name matches the search result.")
                                passenger_list_link_href = passenger_list_link.get_attribute("href")
                                manifest_setup_url = f"{BASE_URL}{passenger_list_link_href}"
                                page.goto(manifest_setup_url)
                                page.wait_for_load_state("networkidle")
                                page.click("button#select-all")


                                if(fill_manifest_fields(page, record)):
                                    log_record_status(log_filepath, supplier_name, "Success", "Passsenger details updated successfully")
                                    #<div class="alert alert-success" role="alert">Manifest configuration was saved successfully.</div>
                                    if page.locator("div.alert.alert-success", has_text="Manifest configuration was saved successfully.").is_visible():
                                        pass
                                        #print("✅ Manifest setup success message found!")
                                        #log_record_status(log_filepath, supplier_name, "Success", "Passsenger details updated successfully")
                                        print(f"Manifest setup successful for supplier: {supplier_name}")
                                    else:
                                        pass
                                        #print("❌ Manifest setup success message not found.")
                                        #log_record_status(log_filepath, supplier_name, "Failed", "Passenger details not updated")
                                        #print(f"Manifest setup may have failed for supplier: {supplier_name}")
                                else:
                                    print(f"Manifest setup encountered issues for supplier: {supplier_name}")
                                    log_record_status(log_filepath, supplier_name, "Failed", "Passenger details not updated")
                                
                                error_fields = []
                       
                        
                    except Exception as e:
                        error_msg = f"Manifest setup failed: {str(e)}"
                        #print("Could not setup manifest for supplier:", supplier_name, e)
                        log_record_status(log_filepath, supplier_name, "Failed", "Passenger details not updated")
                        error_fields = []
                        
                except Exception as e:
                    error_msg = f"Supplier form processing failed: {str(e)}"
                    #print(f"Failed to process supplier {supplier_name}:", e)
                    log_record_status(log_filepath, supplier_name, "Failed", error_msg)
                    error_fields = []
            else:
                #(f"Supplier name is empty or None for record: {record}")
                log_record_status(log_filepath, supplier_name, "Failed", "Supplier name is empty or None")
                error_fields = []
                continue
        
        context.storage_state(path="session.json")
        print("All suppliers processed.")
        print(f"Log file saved at: {log_filepath}")
        browser.close()

if __name__ == "__main__":
    main()
