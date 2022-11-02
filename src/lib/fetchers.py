import requests
import xmltodict
import json
from typing import List, Union

import lib.constants as constants
from lib.types import *


class NoDataFoundError(Exception): pass



#######################################
# FROM LOCAL DATABASE
#######################################

def get_coordinates(connection, address):
	"""Gets EGID and coordinates from local database

	Parameters
	----------
	connection : psycopg2.connection
		postgres database connection
	address : str
		address string

	Returns
	-------
	Coordinates
		Coordinates class containing the EGID as well as the coordinates for the corresponding
		address

	Raises
	------
	NoDataFoundError
		raised in case no data was found for this address in the database
	"""

	# query database
	cursor = connection.cursor()
	cursor.execute("select \"EGID\", lat, lon, \"GKODE\", \"GKODN\" from gwr where \"CompleteAddress\"=%s", (address, ))
	query_result = cursor.fetchall()

	if len(query_result)==0:
		raise NoDataFoundError("No data found for the given address.")

	return Coordinates(
		query_result[0][0],
		query_result[0][1],
		query_result[0][2],
		query_result[0][3],
		query_result[0][4],
	)
	# return {
	# 	"EGID": query_result[0][0],
	# 	"lat": query_result[0][1],
	# 	"lon": query_result[0][2],
	# 	"GKODE": query_result[0][3],
	# 	"GKODN": query_result[0][4]
	# }




def get_gwr_data(connection, address) -> GWRInfo:


	# query database
	cursor = connection.cursor()
	# TODO! adapt SQL query
	cursor.execute("select \"EGID\", lat, lon, \"GKODE\", \"GKODN\" , \"GBAUJ\", \"GBAUP\", \"GEBF\", \"GAREA\", \"GASTW\" from gwr where \"CompleteAddress\"=%s", (address, ))
	query_result = cursor.fetchall()

	if len(query_result)==0:
		raise NoDataFoundError("No data found for the given address.")

	return GWRInfo(
		query_result[0][0],
		query_result[0][1],
		query_result[0][2],
		query_result[0][3],
		query_result[0][4],
		query_result[0][5],
		query_result[0][6],
		query_result[0][7],
		query_result[0][8],
		query_result[0][9],
	)





def get_electricity_production_info(connection, coordinates: Coordinates) -> List[PlantInfo]:
	"""Gets electricity production info from local database
	for the given address

	Parameters
	----------
	connection : psycopg2.connection
		database connection
	coordinates : dict
		coordinates as returned from fetchers.get_coordinates()

	Returns
	-------
	list[PlantInfo]
		list of PlantInfo containing information about electricity production
		for the given address

	Raises
	------
	NoDataFoundError
		raised in case no data was found for this address in the database
	"""

	egid = coordinates.EGID

	# fetch the production info
	cursor = connection.cursor()
	cursor.execute("select \"TotalPower\", \"PlantType\", \"MountingPlace\", \"BeginningOfOperation\" from electricity_production where \"EGID\"=%s", (egid, ))
	query_result = cursor.fetchall()

	if len(query_result)==0:
		print("No data found for the given address.")
		return []

	response = []

	for plant in query_result:
		response.append(
			PlantInfo(plant[0], plant[1], plant[2], plant[3])
		)

	return response



#####################################################
# PV GIS API (https://re.jrc.ec.europa.eu/api/PVcalc)
#####################################################

def get_pv_gis_data_single(lat, lon, peakpower, loss, mountingplace, angle, aspect) -> Union[int, float, None]:

	# loss: float between 0 and 100
	# mountingplace can be one of ["free", "building"]
	# aspect must be between -180 and 180, where 0 is South, -90 is East and 90 is West

	# if no lat/lon in database, take lat/lon of Bern
	if lat==None:
		lat = 46.94809
	if lon==None:
		lon = 7.44744
	if peakpower==None:
		peakpower=1
	if loss==None:
		loss=14
	if mountingplace==None:
		mountingplace="free"
	if angle==None:
		angle=35
	if aspect==None:
		aspect=60

	url = 'https://re.jrc.ec.europa.eu/api/PVcalc?' + \
				'lat=' + str(lat) + \
				'&lon=' + str(lon) + \
				'&peakpower=' + str(peakpower) + \
				'&loss=' + str(loss) + \
				'&mountingplace=' + mountingplace + \
				'&angle=' + str(angle) + \
				'&aspect=' + str(aspect) + \
				'&outputformat=json'

	try:
		return (requests.get(url).json()['outputs']['totals']['fixed']['E_y'])
	except Exception as e:
		print("Error while trying to get PV GIS data: ", e)
		return None

def add_pv_gis_data(coordinates: Coordinates, plants: list[PlantInfo], angle=35, aspect=60) -> List[PlantInfo]:

	lat = coordinates.lat
	lon = coordinates.lon

	response = []

	for plant in plants:

		if plant.plant_type=="PV":

			if plant.mountingplace=="integrated":
				mounting_place_query = "building"
			else:
				mounting_place_query = "free"

			estimated_annual_production = get_pv_gis_data_single(lat, lon, plant.total_power, None, mounting_place_query, angle, aspect)
			plant.estimated_annual_production_kWh = estimated_annual_production # set estimated_annual_production


		response.append(plant)

	return response




#####################################################
# Sonnendach API / SH & DHW demand
#####################################################


def get_heating_demands(gkode, gkodn) -> (SpaceHeatingDemand, DomesticHotWaterDemand):
    """
    Fetching space heating and hotwater demand from sonnandach API (https://github.com/SFOE/geo-api-documentation)

    Parameters
    ----------
    gkode : str
        x coordinate (swiss coordinate system, as used in Gebaeude- und Wohnregister)
    gkodn : str
        y coordinate (swiss coordinate systen, as used in Gebaeude- und Wohnregister)
    """

    space_heating_demand = None
    domestic_hot_water_demand = None

    url = f"https://api3.geo.admin.ch//rest/services/api/MapServer/identify?\
geometryType=esriGeometryPoint&\
returnGeometry=true&\
layers=all:ch.bfe.solarenergie-eignung-daecher&\
geometry={gkode},{gkodn}&\
tolerance=0&\
order=distance&\
sr=2056"

    # try:
    #     return (requests.get(url).json()['outputs']['totals']['fixed']['E_y'])
    # except Exception:
    #     return None
    try:
        response = requests.get(url)
    except Exception as e:
        print("Calling sonnendach API failed:")
        print(e)
        return space_heating_demand, domestic_hot_water_demand
    try:
        response = response.json()
    except Exception as e:
        print("Conversion to json failed:")
        print(e)
        print(url)
        return space_heating_demand, domestic_hot_water_demand

    try:
        space_heating_demand = response["results"][0]["attributes"]["bedarf_heizung"]
    except Exception as e:
        print("Could not extract space heating demand:")
        print(e)

    try:
        domestic_hot_water_demand = response["results"][0]["attributes"]["bedarf_warmwasser"]
    except Exception as e:
        print("Could not extract space heating demand:")
        print(e)

    return space_heating_demand, domestic_hot_water_demand






#####################################################
# MADD BFS API / SH & DHW devices and energy sources
#####################################################

def get_heating_info(egid: str) -> (SpaceHeatingInfo, DomesticHotWaterInfo):
	"""Getting heating info from BFS MADD API

	Parameters
	----------
	egid : str
			EGID number

	Returns
	-------
	[SpaceHeatingInfo, DomesticHotWaterInfo]
			space heating info and hot water info
	"""

	space_heating = SpaceHeatingInfo()
	domestic_hot_water = DomesticHotWaterInfo()


	url = "https://madd.bfs.admin.ch/eCH-0206?egid={}".format(egid)
	api_response = requests.get(url)


	try:
		api_response = xmltodict.parse(api_response.text)
	except Exception as e:
		print("Parsing of MADD response failed: ", e)


	# HEATING
	try:
		heating_device_1 = api_response["maddResponse"]['buildingList']["buildingItem"]["building"]["thermotechnicalDeviceForHeating1"]
		space_heating.main_device = HeatingDevice(
			constants.HEATING_CODES_EN[heating_device_1["heatGeneratorHeating"]],
			constants.HEATING_CODES_EN[heating_device_1["energySourceHeating"]],
			constants.HEATING_CODES_EN[heating_device_1["informationSourceHeating"]],
			heating_device_1["revisionDate"]
		)
	except Exception as e:
		print("Error when trying to extract information of heating device 1: ", e)

	try:
		heating_device_2 = api_response["maddResponse"]['buildingList']["buildingItem"]["building"]["thermotechnicalDeviceForHeating2"]
		if heating_device_2["heatGeneratorHeating"] != "7400":
			space_heating.secondary_device = HeatingDevice(
				constants.HEATING_CODES_EN[heating_device_2["heatGeneratorHeating"]],
				constants.HEATING_CODES_EN[heating_device_2["energySourceHeating"]],
				constants.HEATING_CODES_EN[heating_device_2["informationSourceHeating"]],
				heating_device_2["revisionDate"]
			)
	except Exception as e:
		pass

	# HOT WATER
	try:
		hot_water_device_1 = api_response["maddResponse"]['buildingList']["buildingItem"]["building"]["thermotechnicalDeviceForWarmWater1"]
		domestic_hot_water.main_device = HeatingDevice(
			constants.HEATING_CODES_EN[hot_water_device_1["heatGeneratorHotWater"]],
			constants.HEATING_CODES_EN[hot_water_device_1["energySourceHeating"]],
			constants.HEATING_CODES_EN[hot_water_device_1["informationSourceHeating"]],
			hot_water_device_1["revisionDate"]
		)
	except Exception as e:
		print("Error when trying to extract information of hotwater device 1: ", e)

	try:
		hot_water_device_2 = api_response["maddResponse"]['buildingList']["buildingItem"]["building"]["thermotechnicalDeviceForWarmWater2"]
		if heating_device_2.heatGeneratorHeating != "7600":
			domestic_hot_water.secondary_device = HeatingDevice(
				constants.HEATING_CODES_EN[hot_water_device_2["heatGeneratorHotWater"]],
				constants.HEATING_CODES_EN[hot_water_device_2["energySourceHeating"]],
				constants.HEATING_CODES_EN[hot_water_device_2["informationSourceHeating"]],
				hot_water_device_2["revisionDate"]
			)
	except Exception as e:
		pass

	return space_heating, domestic_hot_water




#####################################################
# Electricity production info from API
#####################################################

# Not in use currently
def get_electricity_production_info_remote(street, nr=None, zipcode=None, city=None):

    search_input = [street]

    if nr != None:
        search_input.append(str(nr))
    if zipcode != None:
        search_input.append(str(zipcode))
    if city != None:
        search_input.append(city)

    searchText = " ".join(search_input)
    print(searchText)
    url = "https://api3.geo.admin.ch/rest/services/api/MapServer/find?layer=ch.bfe.elektrizitaetsproduktionsanlagen&searchText=%s&searchField=address&contains=true" % (searchText)

    return requests.get(url)





if __name__=="__main__":
	pass
