import config  # file that contains my API token
import os
import requests  # used to make the API request
import shelve  # simple persistent storage option
import time
from xml.etree import ElementTree  # used to parse XML


def main():
    print "Welcome to the Muni Script!"

    route_answer = ''
    favorite_answer = ''
    all_routes = get_muni_routes()
    while not route_answer or not favorite_answer:
        answer = raw_input("Enter the muni route or favorite: ")

        if answer in all_routes.keys():
            route_answer = answer
            print "Got it!"
            break
        elif answer in all_favorites():
            favorite_answer = answer
            print "Got it!"
            break
        else:
            print "Favorites: "
            print ", ".join(all_favorites())
            print "Routes: "
            print ", ".join(all_routes.keys())

    if route_answer:
        direction_answer = ""
        while direction_answer not in ["Inbound", "Outbound"]:
            direction_answer = raw_input("Inbound or Outbound? ")

        valid_stop = False
        all_stops = get_route_stops(all_routes[route_answer], direction_answer)
        while not valid_stop:
            stop_answer = raw_input("Enter the stop you want: ")

            if stop_answer in all_stops.keys():
                valid_stop = True
                print "Got it!"
                break
            else:
                print "Pick one of these: "
                print ", ".join(all_stops.keys())
        stop_code = all_stops[stop_answer]

    if favorite_answer:
        stop_code = get_favorite_info(favorite_answer)['stop_code']

    while True:
        all_times = get_next_departures(stop_code)
        print "Next departure times: "
        for route, next_time in all_times.items():
            result_string = route + ": " + next_time
            print result_string
            os.system("say %s minutes" % (result_string))
        time.sleep(60)

    if route_answer:
        create_favorite_answer = ""
        while create_favorite_answer not in ["Yes", "No"]:
            create_favorite_answer = raw_input(
                "Want to save this stop as a favorite? (Yes or No) ")

        if create_favorite_answer == "Yes":
            favorite_name_answer = raw_input("Name this favorite: ")
            save_favorite(favorite_name_answer, stop_code)
            print "Saved!"
            print "Favorites:"
            print ", ".join(all_favorites())
            print "All done!"


def get_muni_routes():
    """ Returns a dictionary of all muni routes mapped to their route codes """

    params = {'token': config.token, 'agencyName': 'SF-MUNI'}
    end_point = 'http://services.my511.org/Transit2.0/GetRoutesForAgency.aspx'
    response_xml = get_xml_response(end_point, params)

    agency_list = response_xml.find("AgencyList")
    agency = agency_list.find("Agency")
    route_list = agency.find("RouteList")

    all_routes = {route.get("Name"): route.get("Code")
                  for route in list(route_list.iter("Route"))}
    return all_routes


def get_route_stops(route_code, direction):
    """ Returns a dictionary of all muni stops, for a certain route and direction,
    mapped to their stop codes """

    params = {'token': config.token,
              'routeIDF': 'SF-MUNI~' + route_code + '~' + direction}
    end_point = 'http://services.my511.org/Transit2.0/GetStopsForRoutes.aspx'
    response_xml = get_xml_response(end_point, params)

    agency_list = response_xml.find("AgencyList")
    agency = agency_list.find("Agency")
    route_list = agency.find("RouteList")
    route = route_list.find("Route")
    route_direction_list = route.find("RouteDirectionList")
    route_direction = route_direction_list.find("RouteDirection")
    stop_list = route_direction.find("StopList")

    all_stops = {stop.get("name"): stop.get("StopCode")
                 for stop in list(stop_list.iter("Stop"))}
    return all_stops


def get_next_departures(stop_code):
    """ Returns a list of all departure times for a given stop """

    params = {'token': config.token, 'stopcode': stop_code}
    end_point = 'http://services.my511.org/Transit2.0/GetNextDeparturesByStopCode.aspx'
    response_xml = get_xml_response(end_point, params)

    agency_list = response_xml.find("AgencyList")
    agency = agency_list.find("Agency")
    route_list = agency.find("RouteList")
    route = route_list.find("Route")
    route_direction_list = route.find("RouteDirectionList")
    route_direction = route_direction_list.find("RouteDirection")
    stop_list = route_direction.find("StopList")
    stop = stop_list.find("Stop")
    departure_time_list = stop.find("DepartureTimeList")

    return {route.get("Name"): time.text
            for route, time in zip(list(route_list.iter("Route")),
            list(departure_time_list.iter("DepartureTime")))}


def get_xml_response(end_point, params):
    """ Given API end-point and params, function parses response
    XML string and returns an Element object """

    response = requests.get(end_point, params=params)
    return ElementTree.fromstring(response.content)


def save_favorite(favorite_name, stop_code):
    s = shelve.open('favorites')
    try:
        s[favorite_name] = {'stop_code': stop_code}
    finally:
        s.close()


def get_favorite_info(favorite_name):
    s = shelve.open('favorites')
    try:
        favorite_info = s[favorite_name]
    finally:
        s.close()
    return favorite_info


def all_favorites():
    s = shelve.open('favorites')
    try:
        favorite_names = s.keys()
    finally:
        s.close()
    return favorite_names

if __name__ == "__main__":
    # execute only if run as a script
    main()
