import lib.fetchers as fetchers
import lib.operators as operators


class NoDataFoundError(Exception): pass

def get_summary(coordinates: dict, production_plants: dict, space_heating: dict, domestic_hot_water: dict):

  summary = {}

  space_heating_demand, domestic_hot_water_demand = fetchers.get_heating_demands(coordinates.GKODE, coordinates.GKODN)

  return {
    "electricity_production_system": operators.electricity_production_exists(production_plants),
    "estimated_annual_electricity_production_kWh": operators.get_total_electricity_production(production_plants),
    "space_heating": operators.space_heating_classifier(space_heating),
    "domestic_hot_water": operators.hot_water_classifier(domestic_hot_water),
    "space_heating_demand_kWh": space_heating_demand,
    "domestic_hot_water_demand_kWh": domestic_hot_water_demand
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
    },
    "summary": summary,
    "installations": {
      "electricity_production": [plant_info.to_dict() for plant_info in el_production_info_extended],
      "space_heating": space_heating.to_dict(),
      "domestic_hot_water": domestic_hot_water.to_dict(),
    }
  }






if __name__=="__main__":
	pass
