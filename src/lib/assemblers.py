import lib.fetchers as fetchers
import lib.operators as operators
from lib.types import *

class NoDataFoundError(Exception): pass

def get_summary(coordinates: dict, production_plants: dict, space_heating: dict, domestic_hot_water: dict) -> dict:

  summary = {}

  space_heating_demand, domestic_hot_water_demand = fetchers.get_heating_demands(coordinates.GKODE, coordinates.GKODN)

  return {
    "electricity_production_system": {
      "value": operators.electricity_production_exists(production_plants),
      "source": ELECTRICITY_PRODUCTION_SOURCE if operators.electricity_production_exists(production_plants) == "existent" else None,
    },
    "estimated_annual_electricity_production_kWh": {
      "value": operators.get_total_electricity_production(production_plants),
      "source": ANNUAL_PRODUCTION_SOURCE,
    },
    "space_heating": {
      "value": operators.space_heating_classifier(space_heating),
      "source": "EcoHabitas",
    },
    "domestic_hot_water": {
      "value": operators.hot_water_classifier(domestic_hot_water),
      "source": "EcoHabitas",
    },
    "space_heating_demand_kWh": {
      "value": space_heating_demand,
      "source": SPACE_HEATING_DEMAND_KWH_SOURCE,
    },
    "domestic_hot_water_demand_kWh": {
      "value": domestic_hot_water_demand,
      "source": DOMESTIC_HOT_WATER_DEMAND_KWH_SOURCE,
    }
  }




def get_house_info(connection, address, angle, aspect):

  try:
    coordinates = fetchers.get_coordinates(connection, address)
  except NoDataFoundError:
    return None


  el_production_info = fetchers.get_electricity_production_info(connection, coordinates)
  el_production_info_extended = fetchers.add_pv_gis_data(coordinates, el_production_info)


  space_heating, domestic_hot_water = fetchers.get_heating_info(coordinates.EGID)
  summary = get_summary(coordinates, el_production_info_extended, space_heating, domestic_hot_water)

  # TODO add error handling


  return {
    "address": address,
    "EGID": coordinates.EGID,
    "coordinates": {
      "lat": coordinates.lat,
      "lon": coordinates.lon,
      "source": COORDINATES_SOURCE,
    },
    "summary": summary,
    "installations": {
      "electricity_production": [{
        "info": plant_info.to_dict(),
        "source": ELECTRICITY_PRODUCTION_SOURCE
        } for plant_info in el_production_info_extended]
      },
      "space_heating": {
        "info": space_heating.to_dict(),
        "source": SPACE_HEATING_SOURCE,
      },
      "domestic_hot_water": {
        "info": domestic_hot_water.to_dict(),
        "source": DOMESTIC_HOT_WATER_SOURCE,
      }
    }






if __name__=="__main__":
	pass
