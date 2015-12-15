import requests

from xml.etree import ElementTree
import config

token = config.token
params = {'token': token, 'agencyName': 'SF-MUNI'}
response = requests.get('http://services.my511.org/Transit2.0/GetRoutesForAgency.aspx', params=params)
response_xml = ElementTree.fromstring(response.content)

agency_list = response_xml.find('AgencyList')
agency = agency_list.find("Agency")
route_list = agency.find("RouteList")

all_routes = [route.get("Name") for route in list(route_list.iter("Route"))]

print "Welcome to the Muni Script!"

valid_route = False
while not valid_route:
    route_answer = raw_input("Enter the muni route you want: ")

    if route_answer == "" or route_answer == "?":
        print '\n'.join(all_routes)
    elif route_answer in all_routes:
        valid_route = True
        print "Nice!"
