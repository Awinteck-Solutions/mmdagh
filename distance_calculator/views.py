import requests
from django.shortcuts import render
from django.conf import settings
import folium
from .models import Trip  # Make sure to import the Trip model

def distance_calculate(request):
    if request.method == 'POST':
        start_address = request.POST.get('start_address')
        end_address = request.POST.get('end_address')
        mode = request.POST.get('mode', 'driving-car')

        try:
            # Check if start_address is in coordinates format (Lat: x, Lon: y)
            if start_address.startswith('Lat:'):
                lat_lon = start_address.split(',')
                lat = float(lat_lon[0].split(':')[1].strip())
                lon = float(lat_lon[1].split(':')[1].strip())
                start_coords = [lon, lat]  # Store in [longitude, latitude]
            else:
                start_coords = geocode_address(start_address)
            
            end_coords = geocode_address(end_address)
        except (KeyError, IndexError, requests.exceptions.RequestException) as e:
            return render(request, 'calculator/error.html', {'message': f'Error with geocoding addresses: {e}'})

        try:
            start_weather = get_weather(start_coords)
            end_weather = get_weather(end_coords)
        except Exception as e:
            return render(request, 'calculator/error.html', {'message': f'Failed to fetch weather data: {e}'})

        api_key = settings.OPENROUTESERVICE_API_KEY
        url = f"https://api.openrouteservice.org/v2/directions/{mode}"
        headers = {'Authorization': api_key}

        payload = {
            'start': f"{start_coords[0]},{start_coords[1]}",
            'end': f"{end_coords[0]},{end_coords[1]}",
            'alternatives': 3
        }

        try:
            response = requests.get(url, headers=headers, params=payload)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException as e:
            return render(request, 'calculator/error.html', {'message': f'Error fetching route: {e}'})

        alternative_routes = []
        for feature in data.get('features', []):
            alternative_distance = feature['properties']['segments'][0]['distance'] / 1000
            alternative_time = feature['properties']['segments'][0]['duration'] / 60
            coordinates = feature['geometry']['coordinates']
            alternative_routes.append({
                'distance': round(alternative_distance, 2),
                'time': round(alternative_time, 2),
                'coordinates': coordinates
            })

        main_route = alternative_routes[0] if alternative_routes else None
        if main_route:
            distance = main_route['distance']
            travel_time = main_route['time']
            coordinates = main_route['coordinates']
        else:
            return render(request, 'calculator/error.html', {'message': 'No valid routes found. Please try again.'})

        # Generate map
        average_lat = (start_coords[1] + end_coords[1]) / 2
        average_lon = (start_coords[0] + end_coords[0]) / 2
        m = folium.Map(location=[average_lat, average_lon], zoom_start=12)

        folium.Marker([start_coords[1], start_coords[0]], popup='Start').add_to(m)
        folium.Marker([end_coords[1], end_coords[0]], popup='End').add_to(m)

        # Draw routes
        route_points = [[point[1], point[0]] for point in coordinates]
        folium.PolyLine(route_points, color='blue', weight=5).add_to(m)

        for i, alt_route in enumerate(alternative_routes[1:]):
            alt_points = [[point[1], point[0]] for point in alt_route['coordinates']]
            polyline = folium.PolyLine(alt_points, color='red', weight=5, opacity=0.6).add_to(m)
            polyline.add_child(folium.Popup(f"Route {i+1}: {alt_route['distance']} km, {alt_route['time']} mins"))

        map_html = m._repr_html_()

        # Save trip details
        Trip.objects.create(
            start_address=start_address,
            end_address=end_address,
            distance=round(distance, 2),
            travel_time=round(travel_time, 2),
            mode=mode
        )

        # Context for rendering
        share_url = request.build_absolute_uri(f'/calculator/distance_result/?start={start_address}&end={end_address}&mode={mode}')
        context = {
            'start_address': start_address,
            'end_address': end_address,
            'distance': round(distance, 2),
            'travel_time': round(travel_time, 2),
            'map_html': map_html,
            'start_weather': start_weather,
            'end_weather': end_weather,
            'mode': mode,
            'alternative_routes': alternative_routes,
            'share_url': share_url
        }

        return render(request, 'calculator/distance_result.html', context)

    return render(request, 'calculator/distance_calculator.html')





def geocode_address(address):
    """Function to get coordinates (longitude, latitude) for a given address."""
    geocode_url = "https://api.openrouteservice.org/geocode/search"
    params = {
        'api_key': settings.OPENROUTESERVICE_API_KEY,
        'text': address,
    }
    response = requests.get(geocode_url, params=params).json()
    coords = response['features'][0]['geometry']['coordinates']  # [longitude, latitude]
    return coords


def get_weather(coords):
    """Function to fetch weather data for given coordinates."""
    weather_url = f"http://api.openweathermap.org/data/2.5/weather"
    params = {
        'lat': coords[1],
        'lon': coords[0],
        'appid': settings.OPENWEATHER_API_KEY,
        'units': 'metric',  # Temperature in Celsius
    }
    response = requests.get(weather_url, params=params).json()
    return {
        'temperature': response['main']['temp'],
        'description': response['weather'][0]['description'],
    }




def trip_history(request):
    trips = Trip.objects.all().order_by('-created_at')
    return render(request, 'calculator/trip_history.html', {'trips': trips})



def google_map_search(request):
    """
    Renders the Google Maps search template.
    """
    context = {
        'title': 'Google Map Search',  # Set the title for the page
    }
    return render(request, 'calculator/google_map_search.html', context)



def leaflet_map(request):
    return render(request, 'calculator/leaflet_map.html')



