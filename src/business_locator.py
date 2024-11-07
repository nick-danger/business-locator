"""
This module provides functions to interact with the Google Maps API for geocoding and searching places.
"""
import os
import time

import googlemaps
from dotenv import load_dotenv

# Initialize the Google Maps client
load_dotenv()
gmaps = googlemaps.Client(key=os.environ['API_KEY'])


def get_location_coordinates(address):
    geocode_result = gmaps.geocode(address)
    if geocode_result:
        location_data = geocode_result[0]['geometry']['location']
        return location_data['lat'], location_data['lng']
    print(f"Could not find coordinates for {address}.")
    return None, None


def search_places(query, location, radius=None, max_drive_time=None):
    lat, lng = get_location_coordinates(location)
    if lat is None or lng is None:
        return []

    results = []

    if radius:
        radius_meters = radius * 1609.34  # Convert miles to meters
        places_result = gmaps.places(query=query, location=(lat, lng), radius=radius_meters)['results']
    else:
        places_result = gmaps.places(query=query, location=(lat, lng), radius=20000)['results']

    if max_drive_time:
        destination_addresses = [place['geometry']['location'] for place in places_result]
        drive_times = \
            gmaps.distance_matrix(origins=[(lat, lng)], destinations=destination_addresses, mode="driving")['rows'][0][
                'elements']

        for idx, element in enumerate(drive_times):
            if element['status'] == 'OK':
                duration = element['duration']['value']  # Duration in seconds
                distance = element['distance']['value']  # Distance in meters
                if duration <= max_drive_time * 60:  # Convert minutes to seconds
                    place_id = places_result[idx]['place_id']
                    details = gmaps.place(place_id=place_id)

                    results.append({
                        "Name": places_result[idx].get('name', 'N/A'),
                        "Address": places_result[idx].get('formatted_address', 'N/A'),
                        "Phone": details['result'].get('formatted_phone_number', 'N/A'),
                        "Website": details['result'].get('website', 'N/A'),
                        "Google Maps URL": f"https://www.google.com/maps/place/?q=place_id:{place_id}",
                        "Drive Time (min)": duration / 60,
                        "Distance (miles)": distance / 1609.34,
                        "Search Term": query
                    })
    else:
        for place in places_result:
            place_id = place['place_id']
            details = gmaps.place(place_id=place_id)

            distance_matrix_result = \
                gmaps.distance_matrix(origins=[(lat, lng)], destinations=[place['geometry']['location']],
                                      mode="driving")[
                    'rows'][0]['elements'][0]
            duration = distance_matrix_result['duration']['value']  # Duration in seconds
            distance = distance_matrix_result['distance']['value']  # Distance in meters

            results.append({
                "Name": place.get('name', 'N/A'),
                "Address": place.get('formatted_address', 'N/A'),
                "Phone": details['result'].get('formatted_phone_number', 'N/A'),
                "Website": details['result'].get('website', 'N/A'),
                "Google Maps URL": f"https://www.google.com/maps/place/?q=place_id:{place_id}",
                "Drive Time (min)": duration / 60,
                "Distance (miles)": distance / 1609.34,
                "Search Term": query
            })

    return results


def main():
    search_name = input("Please enter a name for this search (used for the output file): ")
    address = input("Please enter the address: ")

    search_mode = input("Do you want to search by radius, drive time, or both? (r/d/b): ").strip().lower()

    radius = None
    max_drive_time = None

    if search_mode in ['r', 'b']:
        radius = float(input("Enter the radius in miles: "))

    if search_mode in ['d', 'b']:
        max_drive_time = int(input("Enter the maximum drive time in minutes: "))

    search_terms = os.environ['DEFAULT_SEARCH_TERMS'].strip().split(',')
    print(f"\nCurrent search terms: {', '.join(search_terms)}")
    additional_terms = input("Would you like to add additional search terms? (y/n): ").strip().lower()

    if additional_terms == 'y':
        while True:
            new_term = input("Enter a new search term (or press Enter to finish): ").strip()
            if not new_term:
                break
            search_terms.append(new_term)

    # Show the current output location and ask if the user wants to change it
    current_output_directory = os.getcwd()  # Get the current working directory
    print(f"\nCurrent output location: {current_output_directory}")
    change_output_directory = input("Would you like to change the output location? (y/n): ").strip().lower()

    if change_output_directory == 'y':
        new_output_directory = input("Please enter the new output directory: ").strip()
        if os.path.isdir(new_output_directory):
            output_directory = new_output_directory
        else:
            print("Invalid directory. Using the current directory instead.")
            output_directory = current_output_directory
    else:
        output_directory = current_output_directory

    all_results = []

    for term in search_terms:
        print(f"\nSearching for '{term}' near {address}...")
        results = search_places(term, address, radius=radius, max_drive_time=max_drive_time)
        all_results.extend(results)

        for idx, result in enumerate(results, start=1):
            print(f"{idx}. Name: {result['Name']}, Address: {result['Address']}, Phone: {result['Phone']}, "
                  f"Website: {result['Website']}, URL: {result['Google Maps URL']}, "
                  f"Drive Time: {result['Drive Time (min)']:.2f} minutes, Distance: {result['Distance (miles)']:.2f} miles, "
                  f"Search Term: {result['Search Term']}")

        time.sleep(2)  # Respectful pause to avoid overwhelming the API

    output_file_name = f"{search_name.replace(' ', '_').lower()}_search_results.xlsx"
    output_file_path = os.path.join(output_directory, output_file_name)

    from openpyxl import Workbook

    wb = Workbook()
    ws = wb.active
    ws.append(["Name", "Address", "Phone", "Website", "Google Maps URL", "Drive Time (min)", "Distance (miles)",
               "Search Term"])

    for result in all_results:
        ws.append([result["Name"], result["Address"], result["Phone"], result["Website"], result["Google Maps URL"],
                   result["Drive Time (min)"], result["Distance (miles)"], result["Search Term"]])

    wb.save(output_file_path)
    print(f"\nSearch completed and results saved to '{output_file_path}'")


if __name__ == "__main__":
    main()
