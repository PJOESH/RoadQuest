import requests
from django.conf import settings

SEARCH_RADIUS = 20000

# convert location to [latitude, longitude]
# using OpenStreetMap Nominatim API
def location_to_coords(location_name):
    #test
    base_url = "http://api.openweathermap.org/geo/1.0/direct"

    params = {
        "q": f"{location_name}",
        "limit": 1,
        "appid": settings.OWM_KEY
    }

    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        data = response.json()
        if data:
            # extract latitude and longitude
            latitude = data[0]["lat"]
            longitude = data[0]["lon"]
            print(latitude)
            print(longitude)
            return latitude, longitude
        else:
            print("No results found for the location:", location_name)
            return None, None
    else:
        print("Error:", response.status_code)
        return None, None

# send api request to route given start and end coordinates
# start_coords: [latitude, longitude]
# using OSRM API
def routing(start_coords, end_coords):

    # Mapbox Directions API endpoint
    base_url = f"https://api.mapbox.com/directions/v5/mapbox/driving/{start_coords[1]},{start_coords[0]};{end_coords[1]},{end_coords[0]}"
    print(f"attempting https://api.mapbox.com/directions/v5/mapbox/driving/{start_coords[1]},{start_coords[0]};{end_coords[1]},{end_coords[0]}")

    # parameters
    params = {
        'access_token': settings.MAPBOX_KEY, 
        'geometries': 'geojson',  
        'annotations': 'distance',
        'overview': 'full'
          
    }

    # send the GET request to Mapbox API
    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        # parse the JSON response
        data = response.json()

        if 'routes' in data and data['routes']:
            # extract the first route
            route = data['routes'][0]

            # extract waypoints from the route
            waypoints = route['geometry']['coordinates']

            distances = []

            for leg in route.get('legs', []):
                if 'annotation' in leg and 'distance' in leg['annotation']:
                    distances.extend(leg['annotation']['distance'])

            refined_waypoints = [waypoints[0]]
            refined_distances = [0.0]
            current_distance = 0.0
            last_added_index = 0

            for i in range(1, len(waypoints)):
                segment_distance = distances[i - 1]
                current_distance += segment_distance

                # refines waypoints so they are decently spaced out
                if current_distance >= SEARCH_RADIUS * 2.0:
                    refined_waypoints.append(waypoints[i])
                    refined_distances.append(current_distance)
                    current_distance = 0.0
                    last_added_index = i

            if last_added_index != len(waypoints) - 1:
                refined_waypoints.append(waypoints[-1])
                refined_distances.append(sum(distances[last_added_index:]))

            return refined_waypoints

        else:
            print("No routes found.")
    else:
        data = response.json()
        print("API Message:", data['message'])
        print("Error:", response.status_code)

def get_pois(coordinate):
    api_key = settings.GOOGLE_KEY
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?"

    params = {
        "location": f"{coordinate[1]},{coordinate[0]}" ,
        "radius": SEARCH_RADIUS,
        "key": api_key
    }
    
    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        pois = []
        for google_poi in data.get("results", []):
            poi = {
                "name": google_poi.get("name"),
                "address": google_poi.get("vicinity"),
                "latitude": google_poi["geometry"]["location"]["lat"],
                "longitude": google_poi["geometry"]["location"]["lng"],
                "price_level": google_poi.get("price_level"),
                "rating": google_poi.get("rating"),
                "review_count": google_poi.get("user_ratings_total"),
                "type": ', '.join([t.replace('_', ' ').title() for t in google_poi.get("types", [])]),
            }
            pois.append(poi)
        # print(pois)

    else:
        print("Error:", response.status_code)

    return pois
