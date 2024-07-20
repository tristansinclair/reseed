import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import json
import usaddress
import math
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

address_seen = set()
units_seen = set()
apartments = []


headers = {
    "Content-Type": "application/json",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Sec-Fetch-Site": "same-origin",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Sec-Fetch-Mode": "cors",
    "Host": "www.apartments.com",
    "Origin": "https://www.apartments.com",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
    "Referer": "https://www.apartments.com/san-diego-ca/",
    "Connection": "keep-alive",
    "Sec-Fetch-Dest": "empty",
    # "X-CSRF-TOKEN": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJuYmYiOjE3MjEwNzUwMTcsImV4cCI6MTcyMTE2MTQxNywiaWF0IjoxNzIxMDc1MDE3LCJpc3MiOiJodHRwczovL3d3dy5hcGFydG1lbnRzLmNvbSIsImF1ZCI6Imh0dHBzOi8vd3d3LmFwYXJ0bWVudHMuY29tIn0.ygrHVFam7H-vx3SCut42BOs5Gho6yEWjsD8CrcVhUok",
    "Cookie": "sr=%7B%22Width%22%3A1228%2C%22Height%22%3A894%2C%22PixelRatio%22%3A2%7D; _pin_unauth=dWlkPU1UVXlZamhtWldRdFkyTTVPQzAwT0RFd0xXSXlOR1F0TnpJME1XWXdOVE5sT0RkbQ; _screload=; _uetsid=ddbb6720426f11ef805aadb057620a1d; _uetvid=38fee260f2ad11ee8f97c38113b98a47; bm_sv=35BC0D624A11DB41DA54C9AEF0956F86~YAAQSww0F8xc5rSQAQAArbEQuBhLUSgQOR1+NkOJz9RY2CIjiFAqilfOaGXOsyx+YmsKGwM/VVHG/NSVRk2at7n/frcm50Cp5czgprROClqikYYs9yPwOFR0T/9YuxT2wrW49TI4CUwu8x09EIa9q0OEJyvJIisLF4qnT3/780y1YdxfbkT+BVwPPV8kAWSK4vEr6rZDhg6kbumzm0X/UX6uiyAyNb74mstbu0WWYN9WUKjfkHDdDhDOR2nhiIzQrVvgYLU=~1; cto_bundle=Jxtan18lMkZMQlRucG1PZnQ5cGQ2aFBPem5hZlZ5OElHMkRNZlNCS3VYNzJNQzE3QzBMbW85R08zSzhEUVAzdHdFckZkVnZTWThmbDA1aTNleEhDbWR0NUVLVjgzVzhFT1FsN0RJOE9uZWh0aXppQVptSlVPMmNDa01tWUVoQ1Bpanl6WXc1; tfpsi=2c872130-d0bc-4ac4-817f-6838faf90fbd; cb=1; cul=en-US; OptanonConsent=isGpcEnabled=0&datestamp=Mon+Jul+15+2024+13%3A23%3A38+GMT-0700+(Pacific+Daylight+Time)&version=202401.2.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=30fed092-18a3-4ce0-a41b-0abe83bfe45f&interactionCount=0&landingPath=NotLandingPage&groups=C0001%3A1%2CC0003%3A1%2CC0002%3A1%2CC0004%3A1&AwaitingReconsent=false; _dpm_id.c51a=11d5ac65-3e8f-4893-b064-32f9f3f05d29.1712253630.15.1721075018.1721031197.a23e0bb4-b201-4cf8-a2a5-adee96acecba; _dpm_ses.c51a=*; _fbp=fb.1.1712253629442.1810098185; _ga=GA1.1.760150656.1712253629; _ga_X3LTX2PVM9=GS1.1.1721072799.19.1.1721075018.53.0.1613054028; _gcl_au=1.1.2089699608.1720029928; _gid=GA1.2.2008056232.1721023370; _scid_r=3073b147-2e94-4f10-b6f6-9540644d0cf1; lsc=%7B%22Map%22%3A%7B%22BoundingBox%22%3A%7B%22LowerRight%22%3A%7B%22Latitude%22%3A32.53479%2C%22Longitude%22%3A-116.90572%7D%2C%22UpperLeft%22%3A%7B%22Latitude%22%3A33.11425%2C%22Longitude%22%3A-117.2823%7D%7D%2C%22CountryCode%22%3A%22US%22%7D%2C%22Geography%22%3A%7B%22ID%22%3A%22h6emeh3%22%2C%22Display%22%3A%22San%20Diego%2C%20CA%22%2C%22GeographyType%22%3A2%2C%22Address%22%3A%7B%22City%22%3A%22San%20Diego%22%2C%22CountryCode%22%3A%22USA%22%2C%22County%22%3A%22San%20Diego%22%2C%22State%22%3A%22CA%22%2C%22MarketName%22%3A%22San%20Diego%22%2C%22DMA%22%3A%22San%20Diego%2C%20CA%22%7D%2C%22Location%22%3A%7B%22Latitude%22%3A32.825%2C%22Longitude%22%3A-117.094%7D%2C%22BoundingBox%22%3A%7B%22LowerRight%22%3A%7B%22Latitude%22%3A32.53479%2C%22Longitude%22%3A-116.90572%7D%2C%22UpperLeft%22%3A%7B%22Latitude%22%3A33.11425%2C%22Longitude%22%3A-117.2823%7D%7D%2C%22v%22%3A23508%2C%22IsPmcSearchByCityState%22%3Afalse%7D%2C%22Listing%22%3A%7B%22Style%22%3A2%7D%2C%22Paging%22%3A%7B%7D%2C%22ResultSeed%22%3A184765%2C%22Options%22%3A0%2C%22CountryAbbreviation%22%3A%22US%22%7D; _dd_s=rum=0&expire=1721075918913; RT='sl=d&ss=lynevtdx&tt=td9&z=1&dm=apartments.com&si=f75a506d-9abb-4885-b04a-0d10ed095a32&bcn=%2F%2F17de4c1a.akstat.io%2F'; uat=%7B%22VisitorId%22%3A%22a69d322d-dafe-4ee7-9e40-6123b6f5c2c2%22%2C%22VisitId%22%3A%2264fa7e76-570b-479e-82f9-657277df38c1%22%2C%22LastActivityDate%22%3A%222024-07-15T16%3A23%3A34.3887772-04%3A00%22%2C%22LastFrontDoor%22%3A%22APTS%22%2C%22LastSearchId%22%3A%228B02DDE1-3EC3-49D5-BDA7-D3445C917677%22%7D; btid=14kx7p4; _clsk=7ywstd%7C1721075015346%7C6%7C0%7Co.clarity.ms%2Fcollect; _gat=1; ak_bmsc=7A4FA2494DDC424E9DB152A713DB2D8A~000000000000000000000000000000~YAAQSww0F+oM3LSQAQAATCrutxhRA6DTx559W+7pc2pS8awb9n3Ylx1bcjaSGrvROGcHOxG8vT/lg55+Kw19hFdoSAo5Py/29LgDIkJp6bvZEKV+vYgpdcDK01ReoFjApO4xy5vzzO1tHcmfkQ8UefLZ+FV2vOPhswzcuASTis8Oh5O8vnhUPP8/Bxcp99oPBjxAZy8NHTFwxfIijZZLoOG+RqJkk1AW0Ygy2d0r8Q9kzSxNyxmxrfVcISwaDAaLbGROGezH++x9lmsNIVvyJdBx3jYsmv33HoKTMdizak/iB4opqdlKQH54pnoKbCwDuok4mcagVrZ1D9fSv7F6Xop1YS0qVVxB2FEpF8A8IxZ59czT4c1HJOV1UXwjE21ZBmYGJIOIj7eeJk95pofZzcLVOf+ARmnAJI2YwwBQoH6lTmVk8RsOUWUEx3z3rPDw4cseFfonaYmjfZeokXQgAFPJmA==; akaalb_www_apartments_com_main=1721076356~op=ap_rent_trends_exclusions:www_apartments_com_RESTON|apartments_Prd_Edge_US:www_apartments_com_RESTON|~rv=32~m=www_apartments_com_RESTON:0|~os=0847b47fe1c72dfaedb786f1e8b4b630~id=541b8ef0685b855f059bd42d1c9e79d9; gip=%7b%22Display%22%3a%22Santa+Clara%2c+CA%22%2c%22GeographyType%22%3a2%2c%22Address%22%3a%7b%22City%22%3a%22Santa+Clara%22%2c%22CountryCode%22%3a%22US%22%2c%22State%22%3a%22CA%22%7d%2c%22Location%22%3a%7b%22Latitude%22%3a37.3519%2c%22Longitude%22%3a-121.952%7d%2c%22IsPmcSearchByCityState%22%3afalse%7d; s=; _clck=6gqxxm%7C2%7Cfnh%7C0%7C1555; _sctr=1%7C1720940400000; ab=%7b%22e%22%3atrue%2c%22r%22%3a%5b%5d%7d; _scid=3073b147-2e94-4f10-b6f6-9540644d0cf1; _tt_enable_cookie=1; _ttp=34uuuFODtquELZLWjX1ldkQrjj6; afe=%7b%22e%22%3afalse%7d; fso=%7b%22e%22%3afalse%7d",
}


def fetch_apartment_cards(coordinates):
    # {'UpperLeft': {'Latitude': 33.11425, 'Longitude': -117.2823}, 'LowerRight': {'Latitude': 33.07225, 'Longitude': -117.2403}}
    url = "https://www.apartments.com/services/search/"

    base_data = {
        "Map": {
            "BoundingBox": coordinates,
            "CountryCode": "US",
            "Shape": None,
        },
        "Geography": {
            "ID": "h6emeh3",
            "Display": "San Diego, CA",
            "GeographyType": 2,
            "Address": {
                "City": "San Diego",
                "CountryCode": "USA",
                "County": "San Diego",
                "State": "CA",
                "MarketName": "San Diego",
                "DMA": "San Diego, CA",
            },
            "Location": {"Latitude": 32.825, "Longitude": -117.094},
            # "BoundingBox": {
            #     "LowerRight": {"Latitude": 32.53479, "Longitude": -116.90572},
            #     "UpperLeft": {"Latitude": 33.11425, "Longitude": -117.2823},
            # },
            "v": 23508,
            "IsPmcSearchByCityState": False,
        },
        "Listing": {},
        "Paging": {"Page": None},
        "IsBoundedSearch": True,
        "ResultSeed": 969994,
        "Options": 0,
        "CountryAbbreviation": "US",
    }

    all_results = []

    current_page = 1
    while True:
        data = base_data.copy()
        data["Paging"] = {"Page": str(current_page)}

        response = requests.post(url, headers=headers, json=data, timeout=30)

        if response.status_code == 200:
            result = response.json()
            all_results.append(result)

            print(f"Page {current_page} fetched successfully.")

            if not result.get("MetaState").get("PageNextUrl"):
                print(f"Stopping at page {current_page} as there is no 'PageNextUrl'.")
                break
        else:
            print(
                f"Request failed for page {current_page} with status code {response.status_code}"
            )
            break

        current_page += 1

    property_urls = []
    for result in all_results:
        soup = BeautifulSoup(result["PlacardState"]["HTML"], "html.parser")

        # Find all the apartment listings
        listings = soup.find_all("article", class_="placard")

        # Extract the data
        for listing in listings:
            property_link = listing.get("data-url")
            # property_urls.append(property_link) first verify this exists
            if property_link:
                property_urls.append(property_link)

    return property_urls


def fetch_building_data(listing_url):
    """
    @param listing_url: URL of the apartment building listing

    This function fetches the page of the listing URL and extracts the building data.
    It then determines which type of building it is (apartment, condo, townhouse) and
    processes the HTML accordingly.

    Then it returns the complete building data.
    """
    try:
        response = requests.get(listing_url, headers=headers, timeout=30)
    except requests.exceptions.RequestException as e:
        print(f"Request failed for {listing_url} with exception: {e}")
        return

    soup = BeautifulSoup(response.text, "html.parser")

    if soup.find("div", class_="pricingGridTitleBlock"):
        # This is a building with multiple units in it
        try:
            process_building_listing_html(soup)
        except Exception as e:
            print(f"---Failed to process building listing: {e}---")
            print(listing_url)
    else:
        # This is a single unit listing
        try:
            process_single_listing_html(soup)
        except Exception as e:
            print(f"---Failed to process single listing: {e}---")
            # Show more detail about where the error occurred
            print(listing_url)


def process_bedroom_range(bedrooms):
    # Handle a none case
    if bedrooms is None:
        return None, None, None

    # Handle variations and convert 'Studio' to 0
    if "Studio" in bedrooms or "Studio bd" in bedrooms or "Studio bed" in bedrooms:
        beds_min = 0
    else:
        beds_min = None

    # Match for ranges like '1 - 3 bd' or '1 - 3 beds' or '1 - 3 bedrooms'
    bedrooms_match = re.findall(r"(\d+)", bedrooms)

    if bedrooms_match:
        if beds_min is None:
            beds_min = int(bedrooms_match[0])
        beds_max = int(bedrooms_match[-1])
    else:
        beds_max = beds_min

    if beds_min is not None and beds_max is not None:
        beds_string = f"{beds_min} - {beds_max} beds"
        # replace 0 with 'Studio'
        if beds_min == 0:
            beds_string = beds_string.replace("0", "Studio")
    else:
        beds_string = None

    return beds_min, beds_max, beds_string


def process_bathroom_range(bathrooms):
    # Handle a none case
    if bathrooms is None:
        return None, None, None

    # Match for ranges like '1.5 - 3 baths' or '1 - 3 ba'
    bathrooms_match = re.findall(r"(\d+\.?\d*)", bathrooms)

    if bathrooms_match:
        baths_min = float(bathrooms_match[0])
        baths_max = float(bathrooms_match[-1])
    else:
        baths_min = None
        baths_max = None

    if baths_min is not None and baths_max is not None:
        baths_string = f"{baths_min} - {baths_max} baths"
        baths_string = baths_string.replace(".0", "")
    else:
        baths_string = None

    return baths_min, baths_max, baths_string


def process_square_feet_range(square_feet):
    # Handle a none case
    if square_feet is None:
        return None, None, None

    # Match for ranges like '575 - 1,969 sq ft'
    square_feet_match = re.findall(r"(\d{1,3}(,\d{3})?)", square_feet)

    if square_feet_match:
        sq_ft_min = int(square_feet_match[0][0].replace(",", ""))
        sq_ft_max = int(square_feet_match[-1][0].replace(",", ""))
    else:
        sq_ft_min = None
        sq_ft_max = None

    if sq_ft_min is not None and sq_ft_max is not None:
        sq_ft_string = f"{sq_ft_min} - {sq_ft_max} sq ft"
    else:
        sq_ft_string = None

    return sq_ft_min, sq_ft_max, sq_ft_string


def process_rent_range(rent_range):
    # Handle a none case
    if rent_range is None:
        return None, None, None

    # Match for ranges like '$1,995 - $10,730'
    rent_match = re.findall(r"\$\d{1,3}(,\d{3})?", rent_range)

    if rent_match:
        rent_min = int(rent_match[0].replace(",", ""))
        rent_max = int(rent_match[-1].replace(",", ""))
    else:
        rent_min = None
        rent_max = None

    if rent_min is not None and rent_max is not None:
        rent_string = f"${rent_min} - ${rent_max}"
    else:
        rent_string = None

    return rent_min, rent_max, rent_string


def extract_unit_data(soup):
    units = []
    pricing_grid_items = soup.find_all(
        "div", class_="pricingGridItem multiFamily hasUnitGrid"
    )

    for grid_item in pricing_grid_items:
        floor_plan = grid_item.find("span", class_="modelName").text.strip()
        rent_range = grid_item.find("span", class_="rentLabel").text.strip()
        details = grid_item.find("h4", class_="detailsLabel").text.strip().split(",")
        beds = details[0].strip()
        baths = details[1].strip()
        # sq_ft = details[2].strip()

        unit_list = grid_item.find_all("li", class_="unitContainer js-unitContainer")

        for unit in unit_list:
            unit_number = unit.find("span", title=True).text.strip()
            price_element = unit.find("span", {"data-monetaryunittype": "USD"})
            if price_element:
                price = price_element.text.strip()
            else:
                price = None
            sq_ft_unit = unit.find("div", class_="sqftColumn column").text.strip()

            availability_element = unit.find("span", class_="dateAvailable")
            if availability_element:
                availability = availability_element.text.strip()
            else:
                availability = None

            # Ensure no duplication by creating a unique identifier for each unit
            unique_id = f"{floor_plan}-{unit_number}"
            if unique_id not in [u["unique_id"] for u in units]:
                units.append(
                    {
                        "unique_id": unique_id,
                        "floor_plan": floor_plan,
                        "beds": "Studio" if beds == "Studio" else int(beds.split()[0]),
                        "baths": float(baths.split()[0]),
                        "unit": unit_number,
                        "price": (
                            None
                            if price == "Call for Rent"
                            else int(price.replace("$", "").replace(",", ""))
                        ),
                        "sq_ft": int(sq_ft_unit.split("\n")[1].replace(",", "")),
                    }
                )

    return units

def clean_address(address):
        # standardize all street, circles, courts, etc
        # handle all upper/lower cases, iterate through them in a list
        address = address.lower()
        address = address.replace("st", "street")
        address = address.replace("rd", "road")
        address = address.replace("ave", "avenue")
        address = address.replace("blvd", "boulevard")
        address = address.replace("dr", "drive")
        address = address.replace("ln", "lane")
        address = address.replace("ct", "court")
        address = address.replace("pl", "place")
        address = address.replace("cir", "circle")
        address = address.replace("sq", "square")
        address = address.replace("trl", "trail")
        address = address.replace("ter", "terrace")
        address = address.replace("pkwy", "parkway")
        address = address.replace("hwy", "highway")
        address = address.replace("expwy", "expressway")
        address = address.replace("st.", "street")
        address = address.replace("rd.", "road")
        address = address.replace("ave.", "avenue")
        address = address.replace("blvd.", "boulevard")
        address = address.replace("dr.", "drive")
        address = address.replace("ln.", "lane")
        address = address.replace("ct.", "court")
        address = address.replace("pl.", "place")
        address = address.replace("cir.", "circle")
        address = address.replace("sq.", "square")
        address = address.replace("trl.", "trail")
        address = address.replace("ter.", "terrace")
        address = address.replace("pkwy.", "parkway")
        address = address.replace("hwy.", "highway")

        pattern = r"(\b[\w\s]+(?:\b\w+\b))(?=.*\1)"
        cleaned_address = re.sub(pattern, '', address).strip(', ')

        return cleaned_address

def process_building_listing_html(soup):
    """
    Given the html content of a building listing, this function extracts the building data.

    Handles all errors and exceptions of missing data.
    """

    # Extract the building name
    name = soup.find("h1", class_="propertyName").text.strip()

    # Extract the neighborhood
    neighborhood = soup.find("a", class_="neighborhood").text.strip()

    full_address = soup.find("div", class_="propertyAddress").text.strip()
    full_address = full_address.replace("Property Address:", "").strip()
    full_address = re.sub(r"\s+", " ", full_address)
    full_address = clean_address(full_address)

    # use usaddress to parse the address into its components
    address_data = usaddress.tag(full_address)[0]
    zip_code = address_data["ZipCode"]
    city = address_data["PlaceName"]
    state = address_data["StateName"]

    # check to make sure we don't double add this building
    if full_address in address_seen:
        print(f"Skipping {full_address} as we have already seen it.")
        return
    else:
        address_seen.add(full_address)

    # Extract monthly rent, bedrooms, bathrooms, square feet RANGES
    price_bed_range_info = soup.find("ul", class_="priceBedRangeInfo")
    if price_bed_range_info:
        for item in price_bed_range_info.find_all("li", class_="column"):
            label = item.find("p", class_="rentInfoLabel")
            detail = item.find("p", class_="rentInfoDetail")
            if label and detail:
                label_text = label.text.strip()
                detail_text = detail.text.strip()
                if label_text == "Monthly Rent":
                    monthly_rent = detail_text
                elif label_text == "Bedrooms":
                    bedrooms = detail_text
                elif label_text == "Bathrooms":
                    bathrooms = detail_text
                elif label_text == "Square Feet":
                    square_feet = detail_text

        # process the bedroom, bathroom,
        beds_min, beds_max, beds_string = process_bedroom_range(bedrooms)
        baths_min, baths_max, baths_string = process_bathroom_range(bathrooms)
        sq_ft_min, sq_ft_max, sq_ft_string = process_square_feet_range(square_feet)
        rent_min, rent_max, rent_string = process_rent_range(monthly_rent)
    else:
        beds_min = None
        beds_max = None
        beds_string = None
        baths_min = None
        baths_max = None
        baths_string = None
        sq_ft_min = None
        sq_ft_max = None
        sq_ft_string = None
        rent_min = None
        rent_max = None
        rent_string = None

    # Extract year built, units, and stories using regex
    details_container = soup.find("div", id="profileV2FeesWrapper")
    if details_container:
        details_text = details_container.text
        year_built_match = re.search(r"Built in (\d{4})", details_text)
        units_stories_match = re.search(r"(\d+) units/(\d+) stories", details_text)

        if year_built_match:
            year_built = year_built_match.group(1)
        else:
            year_built = None
        if units_stories_match:
            units = units_stories_match.group(1)
            stories = units_stories_match.group(2)
            # convert these to integers if they can be converted
            try:
                units = int(units)
                stories = int(stories)
            except ValueError:
                units = None
                stories = None
        else:
            units = None
            stories = None

    # Extract the unit data
    unit_data = extract_unit_data(soup)

    # get the coordinates for the address
    print(f"Getting coordinates for {full_address}")
    lat, lon = get_lat_lon_from_address(full_address)
    print(f"Coordinates for {full_address}: {lat}, {lon}")

    data = {
        "name": name,
        "neighborhood": neighborhood,
        "address": full_address,
        "city": city,
        "state": state,
        "zip_code": zip_code,
        "coordinates": {"lat": lat, "lon": lon},
        "extracted_from": "building_listing",
        "rent": rent_string,  # "$1,995 - $10,730
        "rent_min": rent_min,  # 1995
        "rent_max": rent_max,  # 10730
        "beds": beds_string,  # "Studio - 3 beds"
        "beds_min": beds_min,  # 0 for studio
        "beds_max": beds_max,  # 3 for 3 beds
        "baths": baths_string,
        "baths_min": baths_min,
        "baths_max": baths_max,
        "sq_ft": sq_ft_string,
        "sq_ft_min": sq_ft_min,
        "sq_ft_max": sq_ft_max,
        "year_built": year_built,
        "units": units,
        "stories": stories,
        "unit_data": unit_data,
    }

    print(f"Successfully added building: {full_address} with {len(unit_data)} units.")

    apartments.append(data)

def update_building(
    building_name, unit_uuid, unit_id, unit_rent, unit_beds, unit_baths, unit_sq_ft
):
    """
    This function updates the building data with the new unit data.
    """

    building = None
    for i, apartment in enumerate(apartments):
        if apartment["name"] == building_name:
            building = apartments.pop(i)
            break

    # if we found the building, then we can update the data for the ranges, such as the mins maxes etc
    if building:
        # update the building using the rent, beds, baths, sq_ft, neighborhood, etc
        # only if they need to be updated
        if unit_rent < building["rent_min"]:
            building["rent_min"] = unit_rent
        if unit_rent > building["rent_max"]:
            building["rent_max"] = unit_rent
        if unit_beds < building["beds_min"]:
            building["beds_min"] = unit_beds
        if unit_beds > building["beds_max"]:
            building["beds_max"] = unit_beds
        if unit_baths < building["baths_min"]:
            building["baths_min"] = unit_baths
        if unit_baths > building["baths_max"]:
            building["baths_max"] = unit_baths
        if unit_sq_ft < building["sq_ft_min"]:
            building["sq_ft_min"] = unit_sq_ft
        if unit_sq_ft > building["sq_ft_max"]:
            building["sq_ft_max"] = unit_sq_ft

        # update the building data with the new unit data
        building["unit_data"].append(
            {
                "unique_id": unit_uuid,
                "unit": unit_id,
                "floor_plan": None,
                "beds": unit_beds,
                "baths": unit_baths,
                "price": unit_rent,
                "sq_ft": unit_sq_ft,
            }
        )

        # add the building back to the apartments list
        apartments.append(building)

    else:
        print(
            f"Could not find building {building_name} to update with unit {unit_uuid}"
        )

def add_building_and_unit(
    name,
    neighborhood,
    full_address,
    city,
    state,
    zip_code,
    unit_uuid,
    unit_id,
    unit_floor_plan,
    unit_rent,
    unit_beds,
    unit_baths,
    unit_sq_ft,
):
    """
    This function adds a new building and unit to the apartments list.
    """

    # get coordinates for the address
    lat, lon = get_lat_lon_from_address(full_address)

    # create a new building with the unit data
    building = {
        "name": name,
        "neighborhood": neighborhood,
        "address": full_address,
        "city": city,
        "state": state,
        "zip_code": zip_code,
        "coordinates": {"lat": lat, "lon": lon},
        "extracted_from": "individual_listings",
        "phone": None,
        "manager": None,
        "property_link": None,
        "monthly_rent_range": f"${unit_rent} - ${unit_rent}",
        "bedrooms": f"{unit_beds} beds",  # "Studio - 3 beds
        "bathrooms": f"{unit_baths} baths",
        "beds_min": unit_beds,
        "beds_max": unit_beds,
        "baths_min": unit_baths,
        "baths_max": unit_baths,
        "rent_min": unit_rent,
        "rent_max": unit_rent,
        "square_feet_range": f"{unit_sq_ft} - {unit_sq_ft} sq ft",
        "sq_ft_min": unit_sq_ft,
        "sq_ft_max": unit_sq_ft,
        "year_built": None,
        "units": None,
        "stories": None,
        "unit_data": [
            {
                "unique_id": unit_uuid,
                "unit": unit_id,
                "floor_plan": unit_floor_plan,
                "beds": unit_beds,
                "baths": unit_baths,
                "price": unit_rent,
                "sq_ft": unit_sq_ft,
            }
        ],
    }

    address_seen.add(full_address)
    units_seen.add(unit_uuid)

    # add the building to the apartments list
    apartments.append(building)

def process_single_listing_html(soup):
    """
    Given the html content of a single listing, this function extracts the listing data.
    """
    # Extract the neighborhood
    neighborhood = soup.find("a", class_="neighborhood").text.strip()

    unit_address = soup.find("h1", class_="propertyName").text.strip()
    property_address_container = soup.find("div", class_="propertyAddressContainer")
    city = property_address_container.find("span").text.strip()
    state = (
        property_address_container.find("span", class_="stateZipContainer")
        .find_all("span")[0]
        .text.strip()
    )
    zip_code = (
        property_address_container.find("span", class_="stateZipContainer")
        .find_all("span")[1]
        .text.strip()
    )

    full_address = f"{unit_address}, {city}, {state} {zip_code}"

    building_address = soup.find("div", class_="propertyAddress").text.strip()
    building_address = building_address.replace("Property Address:", "").strip()
    building_address = re.sub(r"\s+", " ", building_address)

    full_address = clean_address(full_address)

    # use usaddress to parse the address into its components
    address_data = usaddress.tag(full_address)[0]
    zip_code = address_data["ZipCode"]
    city = address_data["PlaceName"]
    state = address_data["StateName"]

    # Extract the building name
    name = f"{address_data['AddressNumber']} {address_data['StreetName']} {address_data['StreetNamePostType']}"

    # Extract monthly rent, bedrooms, bathrooms, square feet
    price_bed_range_info = soup.find("ul", class_="priceBedRangeInfo")
    if price_bed_range_info:
        for item in price_bed_range_info.find_all("li", class_="column"):
            label = item.find("p", class_="rentInfoLabel")
            detail = item.find("p", class_="rentInfoDetail")
            if label and detail:
                label_text = label.text.strip()
                detail_text = detail.text.strip()
                if label_text == "Monthly Rent":
                    monthly_rent = detail_text
                elif label_text == "Bedrooms":
                    bedrooms = detail_text
                elif label_text == "Bathrooms":
                    bathrooms = detail_text
                elif label_text == "Square Feet":
                    square_feet = detail_text

        # Process the bedroom, bathroom, rent, and sq footage for an individual listing
        # beds_match = re.search(r"(\d+)", bedrooms)
        baths_match = re.search(r"(\d+)", bathrooms)
        sq_ft_match = re.search(r"(\d+)", square_feet)
        rent_match = re.search(r"\$(\d+)", monthly_rent.replace(",", ""))

        # Process the bedroom, bathroom, rent, and sq footage for an individual listing
        if bedrooms.lower() == "studio" or bedrooms.lower() == "studio bd" or bedrooms.lower() == "studio bed":
            beds = 0
        else:
            beds_match = re.search(r"(\d+)", bedrooms)
            beds = int(beds_match.group(1)) if beds_match else None


        # Extract and convert the values, handling None cases
        # beds = int(beds_match.group(1)) if beds_match else None
        baths = int(baths_match.group(1)) if baths_match else None
        sq_ft = int(sq_ft_match.group(1)) if sq_ft_match else None
        rent = int(rent_match.group(1)) if rent_match else None

    else:
        beds = None
        baths = None
        sq_ft = None
        rent = None

    # Extract the unit id and floor plan
    # Extract the unit id and floor plan
    unit_id = address_data.get("OccupancyIdentifier") or address_data.get("AddressNumber")
    # print(address_data)
    unit_uuid = f"{name}-{unit_id}"

    # if we don't have beds, baths, sq_ft, rent, unit_id then we can't process this listing
    if (
        beds is None
        or baths is None
        or sq_ft is None
        or rent is None
        or unit_id is None
    ):
        # print out which data items were missing and the link to the listing
        # first find out which data items are missing
        missing_data = []
        if beds is None:
            missing_data.append("beds")
        if baths is None:
            missing_data.append("baths")
        if sq_ft is None:
            missing_data.append("sq_ft")
        if rent is None:
            missing_data.append("rent")
        if unit_id is None:
            missing_data.append("unit_id")

        print(f"Missing data for {full_address}, {unit_id}: {', '.join(missing_data)}")
        return

    if full_address in address_seen and unit_uuid not in units_seen:
        update_building(
            building_name=name,
            unit_uuid=unit_uuid,
            unit_id=unit_id,
            unit_rent=rent,
            unit_beds=beds,
            unit_baths=baths,
            unit_sq_ft=sq_ft,
        )
        units_seen.add(unit_uuid)
        print(f"Updated building: {full_address} with unit {unit_uuid}")

    elif unit_uuid not in units_seen:
        add_building_and_unit(
            name,
            neighborhood,
            building_address,
            city,
            state,
            zip_code,
            unit_uuid,
            unit_id,
            None,
            rent,
            beds,
            baths,
            sq_ft,
        )
        print(f"Added new building: {full_address} with unit {unit_uuid}")
    else:
        print(f"Building and Unit already seen: {unit_uuid}")

def split_bounding_box(bounding_box, max_grid_width=0.05, max_grid_height=0.05):
    lat_change = (
        bounding_box["UpperLeft"]["Latitude"] - bounding_box["LowerRight"]["Latitude"]
    )
    long_change = (
        bounding_box["UpperLeft"]["Longitude"] - bounding_box["LowerRight"]["Longitude"]
    )

    num_lat_grids = math.ceil(abs(lat_change) / max_grid_height)
    num_long_grids = math.ceil(abs(long_change) / max_grid_width)

    grids = []

    for lat_num in range(num_lat_grids):
        for long_num in range(num_long_grids):
            if bounding_box["UpperLeft"]["Latitude"] > 0:
                upper_left_lat = bounding_box["UpperLeft"]["Latitude"] - (
                    lat_num * max_grid_height
                )
                lower_right_lat = upper_left_lat - max_grid_height
            else:
                upper_left_lat = bounding_box["UpperLeft"]["Latitude"] + (
                    lat_num * max_grid_height
                )
                lower_right_lat = upper_left_lat + max_grid_height

            if bounding_box["UpperLeft"]["Longitude"] > 0:
                upper_left_long = bounding_box["UpperLeft"]["Longitude"] - (
                    long_num * max_grid_width
                )
                lower_right_long = upper_left_long - max_grid_width
            else:
                upper_left_long = bounding_box["UpperLeft"]["Longitude"] + (
                    long_num * max_grid_width
                )
                lower_right_long = upper_left_long + max_grid_width

            grids.append(
                {
                    "UpperLeft": {
                        "Latitude": upper_left_lat,
                        "Longitude": upper_left_long,
                    },
                    "LowerRight": {
                        "Latitude": lower_right_lat,
                        "Longitude": lower_right_long,
                    },
                }
            )

    return grids


def get_lat_lon_from_address(address):
    """
    This function takes an address as input and returns the latitude and longitude
    using the Nominatim geocoder from the geopy library.

    Parameters:
    address (str): The address to geocode.

    Returns:
    tuple: A tuple containing the latitude and longitude of the address.
    """
    geolocator = Nominatim(user_agent="Geopy Library")
    try:
        location = geolocator.geocode(address)
        if location:
            return location.latitude, location.longitude
        else:
            return None, None
    except GeocoderTimedOut:
        print(f"Geocoder Timed Out for address: {address}")
        return None, None

def fetch_san_diego_data():
    current_time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

    # bounding_box = {
    #     "LowerRight": {"Latitude": 32.53479, "Longitude": -116.90572},
    #     "UpperLeft": {"Latitude": 33.11425, "Longitude": -117.2823},
    # }

    # grids = split_bounding_box(bounding_box)

    # # fetch the data for each grid
    # apartment_urls = []
    # for grid in grids:
    #     new_urls = fetch_apartment_cards(grid)
    #     apartment_urls.append(new_urls)

    # # take the urls and remove duplicates
    # apartment_urls = [list(set(urls)) for urls in apartment_urls]

    # # save the current data of apartment urls
    # with open(f"data/apartment_urls_{current_time}.json", "w") as f:
    #     json.dump(apartment_urls, f, indent=4)

    # read in apartment_urls from apartments_urls_test.json:
    # [
    #    "https://www.apartments.com/675-ninth-ave-san-diego-ca-unit-1906/78mqscx/",,...
    # ]

    with open("data/apartment_urls_test.json", "r") as f:
        apartment_urls = json.load(f)


    # fetch the data for each apartment save every 100 listings
    for i, url in enumerate(apartment_urls):
        fetch_building_data(url)
        if i % 100 == 0:
            with open(f"data/apartments_{current_time}.json", "w") as f:
                json.dump(apartments, f, indent=4)


    with open(f"data/apartments_COMPLETE_{current_time}.json", "w") as f:
        json.dump(apartments, f, indent=4)

    print(f"Successfully fetched data for {len(apartments)} listings.")


# test = fetch_building_data(
#     "https://www.apartments.com/pinnacle-on-the-park-san-diego-ca/9r6e3y6/"
# )
# fetch_building_data(
#     "https://www.apartments.com/675-ninth-ave-san-diego-ca-unit-1906/78mqscx/"
# )
# fetch_building_data(
#     "https://www.apartments.com/675-ninth-ave-san-diego-ca-unit-1906/78mqscx/"
# )
# fetch_building_data("https://www.apartments.com/alx-san-diego-ca/z2bg8dz/")


def test_fetch_two_grids():
    bounding_box = {
        "LowerRight": {"Latitude": 32.53479, "Longitude": -116.90572},
        "UpperLeft": {"Latitude": 33.11425, "Longitude": -117.2823},
    }

    grids = split_bounding_box(bounding_box)

    # fetch the data for each grid
    apartment_urls = []
    for grid in grids:
        new_urls = fetch_apartment_cards(grid)
        apartment_urls.append(new_urls)

    # take the urls and remove duplicates
    # apartment_urls = [list(set(urls)) for urls in apartment_urls]

    # apartments is a list of lists, convert to a single list
    apartment_urls = [url for urls in apartment_urls for url in urls]
    # remove duplicates
    apartment_urls = list(set(apartment_urls))
    # save as a test file:
    with open("data/apartment_urls_test.json", "w") as f:
        json.dump(apartment_urls, f, indent=4)



fetch_san_diego_data()

# fetch_building_data("https://www.apartments.com/3034-beech-st-san-diego-ca-unit-3034-beech-st/mm816kj/")
# fetch_building_data("https://www.apartments.com/6545-oakridge-road-san-diego-ca/14kx7p4/")


current_time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

with open(f"data/apartments_{current_time}.json", "w") as f:
    json.dump(apartments, f, indent=4)
