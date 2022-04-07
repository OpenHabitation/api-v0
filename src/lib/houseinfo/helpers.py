import requests


# ---------------------------------------------
# FROM DATABASE



def get_house_info(connection, address, angle=35, aspect=60):
    """
    Getting info for a house from the PostgreSQL databases

    Parameters
    ----------
    address : str
        address of the house to get the info for
    angle : str, int or None, optional
        angle of the PV panel (if any), by default 60
    aspect : str, int or None, optional
        aspect of the PV panel (if any), by default 35

    Returns
    -------
    dict or None
        dictionary containing the information about the house or 'None' if no results
        found for the given address
    """

    response_dict = {}
    response_dict["address"] = address
    response_dict["coordinates"] = {}
    response_dict["summary"] = {}
    response_dict["installations"] = {}
    response_dict["installations"]["electricity_production"] = []
    response_dict["installations"]["space_heating"] = []
    response_dict["installations"]["domestic_hot_water"] = []

    # extract EGID
    cursor = connection.cursor()
    cursor.execute("select \"EGID\", lat, lon, \"GKODE\", \"GKODN\" from gwr where \"CompleteAddress\"=%s", (address, ))
    result = cursor.fetchall()

    if len(result)==0:
        return None

    else:
        egid = result[0][0]
        lat = result[0][1]
        lon = result[0][2]
        gkode = result[0][3]
        gkodn = result[0][4]

    response_dict["coordinates"]["lat"] = lat
    response_dict["coordinates"]["lon"] = lon

    # search production plant info
    cursor.execute("select \"TotalPower\", \"PlantType\", \"MountingPlace\", \"BeginningOfOperation\" from electricity_production where \"EGID\"=%s", (egid, ))
    production = cursor.fetchall()
    for plant in production:
        mountingplace = plant[2]
        if mountingplace=="integrated":
            mountingplace_query="building"
        else:
            mountingplace_query="free"
        total_power = plant[0]
        estimated_annual_production = get_pv_gis_data(lat, lon, total_power, None, mountingplace_query, angle, aspect)
        plant_dict = {"plant_type":plant[1], "total_power":total_power, "mountingplace":mountingplace, "estimated_annual_production_kWh": estimated_annual_production, "beginning_of_operation":plant[3]}
        response_dict["installations"]["electricity_production"].append(plant_dict)

    # search space_heating info
    cursor.execute("SELECT \"HeatingType\", \"ConstructionYear\" FROM heating_info where \"EGID\"=%s AND (\"InstallationType\"='SH' OR \"InstallationType\"='combined')", (egid, ))
    space_heating = cursor.fetchall()
    # print("HEATING RESULT: ", space_heating)
    for heating in space_heating:
        space_heating_dict = {"heating_type":heating[0], "construction_year":heating[1]}
        response_dict["installations"]["space_heating"].append(space_heating_dict)

    # search hotwater info
    cursor.execute("SELECT \"HeatingType\", \"ConstructionYear\" FROM heating_info WHERE \"EGID\"=%s AND (\"InstallationType\"='DHW' OR \"InstallationType\"='combined')", (egid, ))
    hot_water = cursor.fetchall()
    # print("HOTWATER RESULT: ", hot_water)
    for heating in hot_water:
        hot_water_dict = {"heating_type":heating[0], "construction_year":heating[1]}
        response_dict["installations"]["domestic_hot_water"].append(hot_water_dict)

    summary = get_summary(response_dict)

    response_dict["summary"] = summary

    space_heating_demand, domestic_hot_water_demand = get_heating_demands(gkode, gkodn)
    if space_heating_demand == 0:
        space_heating_demand = "unknown or zero"
    if domestic_hot_water_demand == 0:
        domestic_hot_water_demand = "unknown or zero"

    response_dict["summary"]["space_heating_demand_kWh"] = space_heating_demand
    response_dict["summary"]["domestic_hot_water_demand_kWh"] = domestic_hot_water_demand

    return response_dict


def get_summary(response_dict):
    """
    Determining the summary of house info

    Parameters
    ----------
    response_dict : dict
        dictionary containing info about the production and heating/hot water of a house

    Returns
    -------
    dict
        dictionary containing the summary parameters
    """
    summary = {}

    # calculate total production power if any
    production_plants = response_dict["installations"]["electricity_production"]
    if len(production_plants) > 0:
        total_production_kWh = 0
        for plant in production_plants:
            try:
                total_production_kWh += plant["estimated_annual_production_kWh"]
            except KeyError:
                pass
        summary["estimated_annual_total_production_kWh"] = total_production_kWh
    else:
        summary["estimated_annual_total_production_kWh"] = None

    # classify space-heating
    space_heatings = response_dict["installations"]["space_heating"]
    space_heating_quality = classify_heating_quality(space_heatings)
    summary["space_heating"] = space_heating_quality

    # classify hot water
    domestic_hot_water = response_dict["installations"]["domestic_hot_water"]
    domestic_hot_water_quality = classify_heating_quality(domestic_hot_water)
    summary["domestic_hot_water"] = domestic_hot_water_quality

    return summary


def classify_heating_quality(heatings: list):
    """Classifies heating type into "renewable" or "non-renewable"

    Parameters
    ----------
    heatings : list
        list containing dicts of heating installation info

    Returns
    -------
    str
        "renewable" or "non-renewable"
    """
    heating_types = []
    for heating in heatings:
        try:
            heating_types.append(heating["heating_type"])
        except KeyError:
            pass

    if len(heatings) > 1:
        if "wood (a)" in heating_types:
            heating_types = list(filter(("wood (a)").__ne__, heating_types)) # remove occurrences of "wood (a)"

    heating_qualities = []

    for heating_type in heating_types:
        heating_qualities.append(classify_heating_type(heating_type))

    if "unknown" in heating_qualities:
        return "unknown"
    elif "renewable" in heating_qualities and "non-renewable" in heating_qualities:
        return "unknown"
    elif "renewable" in heating_qualities:
        return "renewable"
    elif "non-renewable" in heating_qualities:
        return "non-renewable"
    else:
        return "unknown"


def classify_heating_type(heating_type: str):
    """
    Classifies the heating type in "renewable", "non-renewable" or unknown

    Parameters
    ----------
    heating_type : str
        heating type
    Returns
    -------
    str
        quality of heating type, one of ["renewable", "non-renewable", "unknown"]
    """

    if heating_type in ["wood (a)", "wood (b)", "wood (c)", "district_heating", "geothermal", "heatpump (air)", "heatpump (water)", "heatpump (geothermal)", "solar"]:
        return "renewable"
    elif heating_type in ["gas", "oil", "biogas", "electricity (resistive)", "heavy oil", "coal"]:
        return "non-renewable"
    else:
        return "unknown"


# ---------------------------------------------
# FROM EXTERNAL API's

def get_pv_gis_data(lat, lon, peakpower, loss, mountingplace, angle, aspect):

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
    except Exception:
        return None


def get_heating_demands(gkode, gkodn):
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




if __name__=="__main__":

    address = "Hallenbadweg 15, 8610 Uster"
    # address = "Schlossstrasse 15, 4147 Aesch BL"

    response = get_house_info(address)
    print(response)