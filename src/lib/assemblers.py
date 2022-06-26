

import fetchers


def get_summary(coordinates):

  space_heating_demand, domestic_hot_water_demand = fetchers.get_heating_demands(coordinates["GKODE"], coordinates["GKODN"])
  pass



def get_house_info(connection, address, angle, aspect):

  coordinates = fetchers.get_coordinates(connection, address)
  el_production_info = fetchers.get_electricity_production_info(connection, coordinates)
  el_production_info_extended = fetchers.add_pv_gis_data(coordinates, el_production_info)


  space_heating = None #TODO
  domestic_hot_water = None #TODO

  summary = None #TODO

  # TODO add error handling


  return {
    "address": address,
    "coordinates": {
      "lat": coordinates["lat"],
      "lon": coordinates["lon"]
    },
    "summary": summary,
    "installations": {
      "electricity_production": el_production_info_extended,
      "space_heating": space_heating,
      "domestic_hot_water": domestinc_hot_water
    }
  }



