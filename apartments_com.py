import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import json
import usaddress
import time
import random


"""
this store the apartment data which looks like this:

{
        "name": "Pinnacle on The Park",
        "neighborhood": "East Village",
        "address": "424 15th St, San Diego, CA 92101",
        "city": "San Diego",
        "state": "CA",
        "zip_code": "92101",

        
        "phone": "(619) 773-0335",
        "manager": null,
        "property_link": "https://www.apartments.com/pinnacle-on-the-park-san-diego-ca/9r6e3y6/",

        "monthly_rent_range": "$1,995 - $10,730",
        "bedrooms": "Studio - 3 beds",
        "bathrooms": "1 - 3 baths",
        "beds_min": 0, # 0 for studio
        "beds_max": 3, # 3 for 3 beds
        "baths_min": 1.0, # float for 0.5 baths in places
        "baths_max": 3.5,
        "square_feet_range": "575 - 1,969 sq ft",
        "year_built": "2015",
        "units": 484,
        "stories": 45,
        "unit_data": [
            {
                "unique_id": "SPIRE 1B-1006",
                "floor_plan": "SPIRE 1B",
                "beds": 1,
                "baths": 1.0,
                "unit": "1006",
                "price": 2455,
                "sq_ft": 600
            },
            ...
"""


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
    "Referer": "https://www.apartments.com/san-diego-ca/3/?bb=w-6873v64M7upziI",
    "Connection": "keep-alive",
    "Sec-Fetch-Dest": "empty",
    "Cookie": "your-cookie-values",
    "X-Requested-With": "XMLHttpRequest",
    "X-CSRF-TOKEN": "your-csrf-token",
}


def fetch_apartment_cards():
    """
    This function fetches the apartment cards from the apartments.com website.
    These cards include general information listing.
    """
    pass


def fetch_building_data(listing_url):
    """
    @param listing_url: URL of the apartment building listing

    This function fetches the page of the listing URL and extracts the building data.
    It then determines which type of building it is (apartment, condo, townhouse) and
    processes the HTML accordingly.

    Then it returns the complete building data.
    """

    # Fetch the page of the listing URL
    response = requests.get(listing_url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    """
    if the html class pricingGridTitleBlock in it:
    <div class="pricingGridTitleBlock">
        <h2 class="availabilityTitle sectionTitle">Pricing &amp; Floor Plans</h2>
    </div>

    then we know this listing is for a building with different units in it.
    """

    if soup.find("div", class_="pricingGridTitleBlock"):
        # This is a building with multiple units in it
        process_building_listing_html(soup)
    else:
        # This is a single unit listing
        process_single_listing_html(soup)


def process_bedroom_range(bedrooms):
    # Handle a none case
    if bedrooms is None:
        return None, None, None

    # Handle variations and convert 'Studio' to 0
    if "Studio" in bedrooms:
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
    """
    Given the html content of a building listing, this function extracts the unit data.
    """
    unit_data = []

    return unit_data


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

    data = {
        "name": name,
        "neighborhood": neighborhood,
        "address": full_address,
        "city": city,
        "state": state,
        "zip_code": zip_code,
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
        # unit_data: TODO
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

    # create a new building with the unit data
    building = {
        "name": name,
        "neighborhood": neighborhood,
        "address": full_address,
        "city": city,
        "state": state,
        "zip_code": zip_code,
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
        beds_match = re.search(r"(\d+)", bedrooms)
        baths_match = re.search(r"(\d+)", bathrooms)
        sq_ft_match = re.search(r"(\d+)", square_feet)
        rent_match = re.search(r"\$(\d+)", monthly_rent.replace(",", ""))

        # Extract and convert the values, handling None cases
        beds = int(beds_match.group(1)) if beds_match else None
        baths = int(baths_match.group(1)) if baths_match else None
        sq_ft = int(sq_ft_match.group(1)) if sq_ft_match else None
        rent = int(rent_match.group(1)) if rent_match else None

    else:
        beds = None
        baths = None
        sq_ft = None
        rent = None

    # Extract the unit id and floor plan
    unit_id = address_data.get("OccupancyIdentifier")
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


test = fetch_building_data(
    "https://www.apartments.com/pinnacle-on-the-park-san-diego-ca/9r6e3y6/"
)
fetch_building_data(
    "https://www.apartments.com/675-ninth-ave-san-diego-ca-unit-1906/78mqscx/"
)
fetch_building_data(
    "https://www.apartments.com/675-ninth-ave-san-diego-ca-unit-1906/78mqscx/"
)
fetch_building_data("https://www.apartments.com/alx-san-diego-ca/z2bg8dz/")

# json print the data
print(json.dumps(apartments, indent=4))
