# views.py
from django.shortcuts import render
from django.conf import settings as django_settings # For API Key
import requests #type:ignore


API_KEY = django_settings.WEATHER_API_KEY

def _get_weather_data_for_location(location_name: str):
    """
    Fetches current weather, forecast, and air quality for a given location.
    Returns a dictionary containing 'weather', 'forecast', and 'air_quality'.
    Each key might hold data or an error dictionary.
    """
    if not location_name:
        return {
            'weather': {'error': 'Location not provided.'},
            'forecast': None,
            'air_quality': None,
            'location_name': location_name
        }

    weather_data = None
    forecast_data = None
    air_quality_data = None

    # Get Current Weather (and coordinates)
    current_weather_url = f'https://api.openweathermap.org/data/2.5/weather?q={location_name}&appid={API_KEY}&units=metric'
    try:
        response = requests.get(current_weather_url)
        response.raise_for_status() # Raises an HTTPError for bad responses (4XX or 5XX)
        weather_data = response.json()
    except requests.exceptions.RequestException as e:
        weather_data = {'error': f'Could not retrieve weather data: {e}'}
    except ValueError: # Includes JSONDecodeError
        weather_data = {'error': 'Invalid weather data format from API.'}


    # Get Forecast and Air Quality Data if current weather was fetched successfully
    if weather_data and not weather_data.get('error'):
        try:
            lat = weather_data['coord']['lat']
            lon = weather_data['coord']['lon']

            # Get 5-day/3-hour Forecast
            forecast_url = f'https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={API_KEY}&units=metric'
            forecast_response = requests.get(forecast_url)
            forecast_response.raise_for_status()
            forecast_data = forecast_response.json()

            # Get Air Quality
            air_url = f'https://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={API_KEY}'
            air_response = requests.get(air_url)
            air_response.raise_for_status()
            air_quality_data = air_response.json()

        except requests.exceptions.RequestException as e:
            if not forecast_data:
                 forecast_data = {'error': f'Could not retrieve forecast data: {e}'}
            if not air_quality_data:
                air_quality_data = {'error': f'Could not retrieve air quality data: {e}'}
        except ValueError: # Includes JSONDecodeError
            if not forecast_data:
                forecast_data = {'error': 'Invalid forecast data format from API.'}
            if not air_quality_data:
                air_quality_data = {'error': 'Invalid air quality data format from API.'}
        except KeyError:
            # This handles cases where 'coord', 'lat', or 'lon' might be missing
            error_message = "Coordinates missing in weather data, cannot fetch forecast or AQI."
            forecast_data = {'error': error_message}
            air_quality_data = {'error': error_message}
    else:
        # If weather_data itself has an error or is None
        error_msg = weather_data.get('error', 'Weather data not available.') if isinstance(weather_data, dict) else 'Weather data not available.'
        forecast_data = {'error': f'Cannot fetch forecast: {error_msg}'}
        air_quality_data = {'error': f'Cannot fetch AQI: {error_msg}'}


    return {
        'weather': weather_data,
        'forecast': forecast_data,
        'air_quality': air_quality_data,
        'location_name': location_name # Keep track of the original searched location name
    }

def home(request):
    return render(request, 'home.html', {})

def about(request):
    
    return render(request, 'about.html', {})

# New helper to make error messages friendlier for the weather_result context
def _make_weather_result_errors_user_friendly(weather_data, forecast_data, air_quality_data, location_name_raw):
    user_friendly_errors = []

    if not location_name_raw.strip(): # Check if the original input was empty or just spaces
        user_friendly_errors.append("Please enter a location to get weather information.")
        # If location is empty, subsequent errors are less relevant to show individually
        return user_friendly_errors, True # True indicates a critical input error

    # Check weather_data for errors
    if weather_data and weather_data.get('error'):
        error_message = weather_data['error']
        if 'Location not provided' in error_message: # Should be caught above, but as a fallback
             user_friendly_errors.append("Please enter a location to get weather information.")
        elif 'Could not retrieve weather data' in error_message or '404' in error_message: # Typically location not found
            user_friendly_errors.append(f"Sorry, we couldn't find weather data for '{location_name_raw}'. Please check the spelling and try again.")
        elif 'too long' in error_message: # From our input validation
            user_friendly_errors.append(error_message)
        else:
            user_friendly_errors.append("An error occurred while fetching weather data. Please try again later.")
        # If weather data fails, forecast and AQI will likely also have errors or be None
        # We can decide if we want to show separate messages for them or just the primary one.
        # For now, let's focus on the primary error from weather_data if it exists.

    # If no critical error yet, check forecast and AQI for specific, non-cascading errors
    # (This part can be refined based on how much detail you want)
    if not user_friendly_errors: # Only if no major weather data error
        if forecast_data and forecast_data.get('error'):
            # Avoid showing if it's just a consequence of weather_data failing
            if not (weather_data and weather_data.get('error')):
                 user_friendly_errors.append("Could not retrieve the forecast at this time.")
        
        if air_quality_data and air_quality_data.get('error'):
            if not (weather_data and weather_data.get('error')):
                user_friendly_errors.append("Could not retrieve air quality information at this time.")
    
    return user_friendly_errors, bool(user_friendly_errors and "Please enter a location" in user_friendly_errors[0] or "too long" in user_friendly_errors[0] if user_friendly_errors else False)


MAX_LOCATION_LENGTH = 100 

def weather_result(request):
    location_name_raw = request.GET.get('location', '')
    location_name_trimmed = location_name_raw.strip() # Trim whitespace

    # Initial input validation (empty or too long)
    if not location_name_trimmed:
        all_data = {'weather': {'error': 'Location not provided.'}, 'forecast': None, 'air_quality': None, 'location_name': location_name_trimmed}
    elif len(location_name_trimmed) > MAX_LOCATION_LENGTH:
        all_data = {
            'weather': {'error': f'Location name is too long. Please use less than {MAX_LOCATION_LENGTH} characters.'},
            'forecast': None, 'air_quality': None, 'location_name': location_name_trimmed
        }
    else:
        all_data = _get_weather_data_for_location(location_name_trimmed)

    user_friendly_errors, has_critical_input_error = _make_weather_result_errors_user_friendly(
        all_data.get('weather'),
        all_data.get('forecast'),
        all_data.get('air_quality'),
        location_name_raw, # Pass raw name for use in error messages if needed
    )

    context = {
        'location_searched': location_name_raw, # What the user actually typed
        'weather_data': all_data.get('weather') if not has_critical_input_error else None,
        'forecast_data': all_data.get('forecast') if not has_critical_input_error else None,
        'air_quality': all_data.get('air_quality') if not has_critical_input_error else None,
        'user_errors': user_friendly_errors,
        'show_results': not user_friendly_errors and (all_data.get('weather') and not all_data.get('weather').get('error'))
    }
    return render(request, 'weather_result.html', context)

def compare_weather(request):
    location1_name_raw = request.GET.get('location1', '').strip()
    location2_name_raw = request.GET.get('location2', '').strip()

    if not location1_name_raw and not location2_name_raw:
        return render(request, 'compare_form.html', {})
    
    if not location1_name_raw or not location2_name_raw:
        context = {
            'location1_name_raw': request.GET.get('location1', ''),
            'location2_name_raw': request.GET.get('location2', ''),
            'form_error': 'Both locations are required for comparison.'
        }
        return render(request, 'compare_form.html', context)

    data1_results = {'weather': None, 'forecast': None, 'air_quality': None, 'location_name': location1_name_raw}
    data2_results = {'weather': None, 'forecast': None, 'air_quality': None, 'location_name': location2_name_raw}
    comparison_summary = {}
    page_errors = []

    # Input validation (length)
    if len(location1_name_raw) > MAX_LOCATION_LENGTH:
        msg = f'Name for Location 1 ("{location1_name_raw}") is too long (max {MAX_LOCATION_LENGTH} chars).'
        page_errors.append(msg)
        data1_results['weather'] = {'error': msg} # Store user-friendly error
    if len(location2_name_raw) > MAX_LOCATION_LENGTH:
        msg = f'Name for Location 2 ("{location2_name_raw}") is too long (max {MAX_LOCATION_LENGTH} chars).'
        page_errors.append(msg)
        data2_results['weather'] = {'error': msg} # Store user-friendly error

    # Fetch data if no initial validation errors
    # Location 1
    if not (data1_results['weather'] and data1_results['weather'].get('error')): # Check if error already set by length validation
        data1_results = _get_weather_data_for_location(location1_name_raw)
        if data1_results['weather'] and data1_results['weather'].get('error'):
            error_detail = data1_results['weather'].get('error')
            if 'Could not retrieve weather data' in error_detail or '404' in error_detail:
                page_errors.append(f"Sorry, we couldn't find weather data for '{location1_name_raw}'. Please check the spelling.")
            elif 'Invalid weather data format' in error_detail:
                 page_errors.append(f"The data format for '{location1_name_raw}' seems invalid. Please try again.")
            else: # Generic fallback for other errors
                page_errors.append(f"An error occurred fetching data for '{location1_name_raw}'.")
    
    # Location 2
    if not (data2_results['weather'] and data2_results['weather'].get('error')): # Check if error already set by length validation
        data2_results = _get_weather_data_for_location(location2_name_raw)
        if data2_results['weather'] and data2_results['weather'].get('error'):
            error_detail = data2_results['weather'].get('error')
            if 'Could not retrieve weather data' in error_detail or '404' in error_detail:
                page_errors.append(f"Sorry, we couldn't find weather data for '{location2_name_raw}'. Please check the spelling.")
            elif 'Invalid weather data format' in error_detail:
                page_errors.append(f"The data format for '{location2_name_raw}' seems invalid. Please try again.")
            else:
                page_errors.append(f"An error occurred fetching data for '{location2_name_raw}'.")

    # Perform comparison if both main weather data sets are valid
    weather1_valid = data1_results['weather'] and not data1_results['weather'].get('error')
    weather2_valid = data2_results['weather'] and not data2_results['weather'].get('error')

    if weather1_valid and weather2_valid:
        comp_loc1_name = data1_results['weather'].get('name', location1_name_raw) or "Location 1"
        comp_loc2_name = data2_results['weather'].get('name', location2_name_raw) or "Location 2"
        comparison_summary['temp'] = compare_temperature(
            data1_results['weather']['main']['temp'], data2_results['weather']['main']['temp'], comp_loc1_name, comp_loc2_name
        )
        comparison_summary['humidity'] = compare_humidity(
            data1_results['weather']['main']['humidity'], data2_results['weather']['main']['humidity'], comp_loc1_name, comp_loc2_name
        )
        comparison_summary['wind'] = compare_wind(
            data1_results['weather']['wind']['speed'], data2_results['weather']['wind']['speed'], comp_loc1_name, comp_loc2_name
        )
    
    context = {
        'location1': location1_name_raw,
        'location2': location2_name_raw,
        'weather1': data1_results['weather'],
        'forecast1': data1_results['forecast'],
        'air_quality1': data1_results['air_quality'],
        'weather2': data2_results['weather'],
        'forecast2': data2_results['forecast'],
        'air_quality2': data2_results['air_quality'],
        'comparison': comparison_summary,
        'page_errors': page_errors # This list now contains more user-friendly messages
    }
    return render(request, 'compare_results_display.html', context)

def compare_temperature(temp1, temp2, loc1, loc2):
    if temp1 > temp2:
        return f"{loc1.title()} is warmer than {loc2.title()} by {temp1 - temp2:.1f}°C."
    elif temp1 < temp2:
        return f"{loc2.title()} is warmer than {loc1.title()} by {temp2 - temp1:.1f}°C."
    else:
        return "Both locations have the same temperature."

def compare_humidity(hum1, hum2, loc1, loc2):
    if hum1 > hum2:
        return f"{loc1.title()} is more humid than {loc2.title()} by {hum1 - hum2}% humidity."
    elif hum1 < hum2:
        return f"{loc2.title()} is more humid than {loc1.title()} by {hum2 - hum1}% humidity."
    else:
        return "Both locations have the same humidity."

def compare_wind(wind1, wind2, loc1, loc2):
    if wind1 > wind2:
        return f"{loc1.title()} is windier than {loc2.title()} by {wind1 - wind2:.1f} m/s."
    elif wind1 < wind2:
        return f"{loc2.title()} is windier than {loc1.title()} by {wind2 - wind1:.1f} m/s."
    else:
        return "Both locations have the same wind speed."