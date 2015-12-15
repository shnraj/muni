import config
import requests
from xml.etree import ElementTree


def main():
    print "Welcome to the Muni Script!"

    valid_route = False
    all_routes = get_muni_routes()
    while not valid_route:
        route_answer = raw_input("Enter the muni route you want: ")

        if route_answer == "" or route_answer == "?":
            print '\n'.join(all_routes)
        elif route_answer in all_routes:
            valid_route = True
            print "Nice!"


def get_muni_routes():
    params = {'token': config.token, 'agencyName': 'SF-MUNI'}
    response = requests.get('http://services.my511.org/Transit2.0/GetRoutesForAgency.aspx', params=params)
    response_xml = ElementTree.fromstring(response.content)

    agency_list = response_xml.find('AgencyList')
    agency = agency_list.find("Agency")
    route_list = agency.find("RouteList")

    all_routes = [route.get("Name") for route in list(route_list.iter("Route"))]
    return all_routes


if __name__ == "__main__":
    # execute only if run as a script
    main()
