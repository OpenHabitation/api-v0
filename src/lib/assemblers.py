import lib.fetchers as fetchers
import lib.operators as operators
from lib.types import *


class NoDataFoundError(Exception): pass



# def get_summary(coordinates: dict, production_plants: dict, space_heating: dict, domestic_hot_water: dict) -> dict:

#   summary = {}

#   space_heating_demand, domestic_hot_water_demand = fetchers.get_heating_demands(coordinates.GKODE, coordinates.GKODN)

#   return {
#     "building_information": {
#       "energy_reference_area": [...],
#       "building_year"
#       "",
#     },
#     "electricity_production_system": {
#       "value": operators.electricity_production_exists(production_plants),
#       "source": ELECTRICITY_PRODUCTION_SOURCE if operators.electricity_production_exists(production_plants) == "existent" else None,
#     },
#     "estimated_annual_electricity_production_kWh": {
#       "value": operators.get_total_electricity_production(production_plants),
#       "source": ANNUAL_PRODUCTION_SOURCE,
#     },
#     "space_heating": {
#       "value": operators.space_heating_classifier(space_heating),
#       "source": "EcoHabitas"
#     },
#     "domestic_hot_water": {
#       "value": operators.hot_water_classifier(domestic_hot_water),
#       "source": "EcoHabitas",
#     },
#     "space_heating_demand_kWh": {
#       "value": space_heating_demand,
#       "source": SPACE_HEATING_DEMAND_KWH_SOURCE,
#     },
#     "domestic_hot_water_demand_kWh": {
#       "value": domestic_hot_water_demand,
#       "source": DOMESTIC_HOT_WATER_DEMAND_KWH_SOURCE,
#     }
#   }




def get_house_info(connection, address, angle, aspect):

  try:
    coordinates = fetchers.get_coordinates(connection, address)
  except NoDataFoundError:
    return None

  gwr_info = fetchers.get_gwr_data(connection, address)


  space_heating_demand, domestic_hot_water_demand = fetchers.get_heating_demands(coordinates.GKODE, coordinates.GKODN)


  el_production_info = fetchers.get_electricity_production_info(connection, coordinates)
  el_production_info_extended = fetchers.add_pv_gis_data(coordinates, el_production_info)



  space_heating, domestic_hot_water = fetchers.get_heating_info(coordinates.EGID)

  # TODO add error handling


  return {
    "address": address,
    "EGID": coordinates.EGID,
    "coordinates": {
      "lat": coordinates.lat,
      "lon": coordinates.lon,
      "GKODN": coordinates.GKODN,
      "GKODE": coordinates.GKODE,
      "source": COORDINATES_SOURCE,
    },
    "building_info": {
      "energy_reference_area_m2": {
        "value": operators.get_gebf_estimated(gwr_info),
        "source": "estimated based on data from Bundesamt für Statistik, Eidg. Gebäude- und Wohnungsregister GWR"
      },
      "construction_year": {
        "value": gwr_info.GBAUJ,
        "source": "Bundesamt für Statistik, Eidg. Gebäude- und Wohnungsregister GWR"
      },
      # "construction_period": {
      #   "value": gwr_info.GBAUP,
      #   "source": "Bundesamt für Statistik, Eidg. Gebäude- und Wohnungsregister GWR"
      # },
    },
    "space_heating": {
      "classification": {
        "value": operators.space_heating_classifier(space_heating),
        "source": "EcoHabitas"
      },
      "space_heating_index_1": {
        "value": operators.get_heating_demand_index_1(gwr_info, space_heating_demand),
        "source": "EcoHabitas"
      },
      "yearly_energy_demand_kWh": {
        "value": space_heating_demand,
        "source": SPACE_HEATING_DEMAND_KWH_SOURCE,
      },
      "installations": {
        "info": space_heating.to_dict(),
        "source": SPACE_HEATING_SOURCE,
      },
    },
    "hot_water": {
      "classification": {
        "value": operators.hot_water_classifier(domestic_hot_water),
        "source": "EcoHabitas",
      },
      "hot_water_index_1": {
        "value": operators.get_hot_water_demand_index_1(gwr_info, domestic_hot_water_demand),
        "source": "EcoHabitas"
      },
      "yearly_energy_demand_kWh": {
        "value": domestic_hot_water_demand,
        "source": DOMESTIC_HOT_WATER_DEMAND_KWH_SOURCE,
      },
      "installations": {
        "info": domestic_hot_water.to_dict(),
        "source": DOMESTIC_HOT_WATER_SOURCE,
      }
    },
    "electricity_production": {
      "pv_requirement": {
        "value": operators.get_pv_requirement(gwr_info),
        "source": "EcoHabitas"
      },
      "electricity_production_system": {
        "value": operators.electricity_production_exists(el_production_info_extended),
        "source": ELECTRICITY_PRODUCTION_SOURCE if operators.electricity_production_exists(el_production_info_extended) == "existent" else None,
      },
      "pv_index_1": {
        "value": operators.get_pv_index_1(gwr_info, el_production_info_extended),
        "source": "EcoHabitas"
      },
      "pv_index_2": {
        "value": operators.get_pv_index_1(gwr_info, el_production_info_extended),
        "source": "EcoHabitas"
      },
      "estimated_annual_electricity_production_kWh": {
        "value": operators.get_total_electricity_production(el_production_info_extended),
        "source": ANNUAL_PRODUCTION_SOURCE,
      },
      "total_pv_power_kW": {
        "value": operators.get_total_pv_power(el_production_info_extended),
        "source": ELECTRICITY_PRODUCTION_SOURCE,
      },
      "installations": [{
        "info": plant_info.to_dict(),
        "source": ELECTRICITY_PRODUCTION_SOURCE
        } for plant_info in el_production_info_extended
      ]
    }
  }




if __name__=="__main__":
	pass
