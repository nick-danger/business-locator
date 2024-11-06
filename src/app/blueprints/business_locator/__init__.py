import logging
import os
from io import BytesIO
from typing import Optional, List, Dict, Tuple, Union

import googlemaps
from flask import Blueprint, render_template, send_file
from googlemaps import Client
from openpyxl import Workbook

from .forms import SearchForm

# Define the blueprint
business_locator = Blueprint('business_locator', __name__, template_folder='templates')


@business_locator.route('/', methods=['GET', 'POST'])
def index():
    form = SearchForm()
    if form.validate_on_submit():
        workbook = generate_xlsx_file(form)
        output = BytesIO()
        workbook.save(output)
        output.seek(0)
        return send_file(output, download_name="search_results.xlsx", as_attachment=True)
    return render_template('index.html', form=form, default_search_terms=os.environ['DEFAULT_SEARCH_TERMS'])


def get_location_coordinates(client: Client, address: str) -> Union[Tuple[float, float], Tuple[None, None]]:
    geocode_result = client.geocode(address)
    if geocode_result:
        location_data = geocode_result[0]['geometry']['location']
        return location_data['lat'], location_data['lng']
    logging.warning(f"Could not find coordinates for {address}.")
    return None, None


def search_places(client: Client, query: str, location: str, radius: Optional[float] = None,
                  max_drive_time: Optional[float] = None) -> List[Dict[str, Union[str, float]]]:
    lat, lng = get_location_coordinates(client, location)
    if lat is None or lng is None:
        return []

    radius_meters = radius * 1_609.34 if radius else 20_000
    places_result = client.places(query=query, location=(lat, lng), radius=radius_meters)['results']
    results = []

    if max_drive_time:
        destination_addresses = [place['geometry']['location'] for place in places_result]
        drive_times = \
        client.distance_matrix(origins=[(lat, lng)], destinations=destination_addresses, mode="driving")['rows'][0][
            'elements']

        for idx, element in enumerate(drive_times):
            if element['status'] == 'OK' and element['duration']['value'] <= max_drive_time * 60:
                place_id = places_result[idx]['place_id']
                details = client.place(place_id=place_id)
                results.append({
                    "Name": places_result[idx].get('name', 'N/A'),
                    "Address": places_result[idx].get('formatted_address', 'N/A'),
                    "Phone": details['result'].get('formatted_phone_number', 'N/A'),
                    "Website": details['result'].get('website', 'N/A'),
                    "Google Maps URL": f"https://www.google.com/maps/place/?q=place_id:{place_id}",
                    "Drive Time (min)": element['duration']['value'] / 60,
                    "Distance (miles)": element['distance']['value'] / 1609.34,
                    "Search Term": query
                })
    else:
        for place in places_result:
            place_id = place['place_id']
            details = client.place(place_id=place_id)
            distance_matrix_result = \
            client.distance_matrix(origins=[(lat, lng)], destinations=[place['geometry']['location']], mode="driving")[
                'rows'][0]['elements'][0]
            results.append({
                "Name": place.get('name', 'N/A'),
                "Address": place.get('formatted_address', 'N/A'),
                "Phone": details['result'].get('formatted_phone_number', 'N/A'),
                "Website": details['result'].get('website', 'N/A'),
                "Google Maps URL": f"https://www.google.com/maps/place/?q=place_id:{place_id}",
                "Drive Time (min)": distance_matrix_result['duration']['value'] / 60,
                "Distance (miles)": distance_matrix_result['distance']['value'] / 1609.34,
                "Search Term": query
            })

    return results


def all_searches(client: Client, search_terms: List[str], address: str, radius: int, max_drive_time: int) -> List[
    Dict[str, Union[str, float]]]:
    all_results = []
    for term in search_terms:
        all_results.extend(search_places(client, term, address, radius=radius, max_drive_time=max_drive_time))
    return all_results


def generate_xlsx_file(search_command: SearchForm) -> Workbook:
    gmaps = googlemaps.Client(key=os.environ['API_KEY'])
    search_terms = os.environ['DEFAULT_SEARCH_TERMS'].lower().split(",")
    search_terms.extend([term for term in search_command.additional_search_terms.data.lower().split(",") if term])

    all_results = all_searches(client=gmaps, search_terms=search_terms, address=search_command.location.data,
                               radius=search_command.radius.data, max_drive_time=search_command.max_drive_time.data)

    wb = Workbook()
    ws = wb.active
    ws.append(["Name", "Address", "Phone", "Website", "Google Maps URL", "Drive Time (min)", "Distance (miles)",
               "Search Term"])
    for result in all_results:
        ws.append([result["Name"], result["Address"], result["Phone"], result["Website"], result["Google Maps URL"],
                   result["Drive Time (min)"], result["Distance (miles)"], result["Search Term"]])
    return wb
