"""
This module initializes the business locator blueprint and defines its routes and helper functions.
"""
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
    """
    Handle the index route for the business locator blueprint.

    This function renders the search form and processes the form submission.
    If the form is valid, it generates an Excel file with the search results
    and sends it as a downloadable file.

    Returns:
        Response: The rendered template or the generated Excel file.
    """
    form = SearchForm()
    if form.validate_on_submit():
        workbook = generate_xlsx_file(form)
        output = BytesIO()
        workbook.save(output)
        output.seek(0)
        return send_file(output, download_name="search_results.xlsx", as_attachment=True)
    return render_template('index.html', form=form)


def get_location_coordinates(client: Client, address: str) -> Union[Tuple[float, float], Tuple[None, None]]:
    """
    Get the coordinates (latitude and longitude) for a given address.

    Args:
        client (Client): The Google Maps client.
        address (str): The address to geocode.

    Returns:
        Union[Tuple[float, float], Tuple[None, None]]: The coordinates of the address or (None, None) if not found.
    """
    try:
        geocode_result = client.geocode(address)
        if geocode_result:
            location_data = geocode_result[0]['geometry']['location']
            return location_data['lat'], location_data['lng']
    except googlemaps.exceptions.ApiError as e:
        logging.error(f"An error occurred invoking the geocode API: {e}")
    logging.warning("Could not find coordinates for %s." % (address,))
    return None, None


def search_places(client: Client, query: str, location: str, radius: Optional[float] = None,
                  max_drive_time: Optional[float] = None) -> List[Dict[str, Union[str, float]]]:
    """
    Search for places based on the query, location, radius, and maximum drive time.

    Args:
        client (Client): The Google Maps client.
        query (str): The search query.
        location (str): The location to search around.
        radius (Optional[float]): The search radius in miles. Defaults to None.
        max_drive_time (Optional[float]): The maximum drive time in minutes. Defaults to None.

    Returns:
        List[Dict[str, Union[str, float]]]: A list of search results with place details.
    """
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
                client.distance_matrix(origins=[(lat, lng)], destinations=[place['geometry']['location']],
                                       mode="driving")[
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
    """
    Perform searches for all search terms and aggregate the results.

    Args:
        client (Client): The Google Maps client.
        search_terms (List[str]): The list of search terms.
        address (str): The location to search around.
        radius (int): The search radius in miles.
        max_drive_time (int): The maximum drive time in minutes.

    Returns:
        List[Dict[str, Union[str, float]]]: A list of aggregated search results.
    """
    all_results = []
    for term in search_terms:
        all_results.extend(search_places(client, term, address, radius=radius, max_drive_time=max_drive_time))
    return all_results


def generate_xlsx_file(search_command: SearchForm) -> Workbook:
    """
    Generate an Excel file with the search results based on the search form input.

    Args:
        search_command (SearchForm): The search form containing the search criteria.

    Returns:
        Workbook: The generated Excel workbook with the search results.
    """

    gmaps = googlemaps.Client(key=os.environ['API_KEY'])
    search_terms = [term for term in search_command.search_terms.data.lower().split(",") if term]

    all_results = all_searches(client=gmaps, search_terms=search_terms, address=search_command.location.data,
                               radius=search_command.radius.data, max_drive_time=search_command.max_drive_time.data)

    wb = Workbook()
    ws = wb.active
    ws.append(["Name", "Address", "Phone", "Website", "Google Maps URL", "Drive Time (min)", "Distance (miles)",
               "Search Term"])

    result_key = lambda x: "/".join([x["Name"], x["Address"], x["Phone"], x["Website"]])
    filtered_results: dict = dict()
    for result in all_results:
        if result_key(result) in filtered_results:
            filtered_results[result_key(result)]["Search Term"] += f", {result['Search Term']}"
        else:
            filtered_results[result_key(result)] = result

    for key in  filtered_results:
        ws.append([filtered_results[key]["Name"], filtered_results[key]["Address"], filtered_results[key]["Phone"], filtered_results[key]["Website"], filtered_results[key]["Google Maps URL"],
                   filtered_results[key]["Drive Time (min)"], filtered_results[key]["Distance (miles)"], filtered_results[key]["Search Term"]])
    return wb
