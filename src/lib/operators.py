import lib.constants as constants
from lib.types import *

def get_string_list(code_list):
  return [constants.HEATING_CODES_EN[code] for code in code_list]


RENEWABLE_LIST = get_string_list(["7410", "7411", "7420", "7421", "7501", "7510", "7511", "7512", "7513", "7540", "7541", "7542", "7543", "7550", "7570", "7580", "7581", "7582", "7610", "7620"])
NO_SYSTEM_REGISTERED_LIST = get_string_list(["7400", "7500", "7600"])
UNKNOWN_LIST = get_string_list(["7430", "7431", "7432", "7433", "7434", "7435", "7436", "7440", "7441", "7460", "7461", "7499", "7598", "7599", "7630", "7632", "7634", "7640", "7660", "7699"])
INEFFICIENT_LIST = get_string_list(["7450", "7451", "7452", "7560", "7650", "7651"])




def space_heating_classifier(space_heating_info: dict) -> "not implemented":

  return "method unimplemented"


def hot_water_classifier(hot_water_info: dict) -> "not implemented":

  return "method unimplemented"


def electricity_production_exists(production_plants: list) -> str:
  if len(production_plants) > 0:
    return "existent"
  else:
    return "unknown"


def get_total_electricity_production(production_plants: list[PlantInfo]) -> float | int | None:

  if len(production_plants) > 0:
    total_production_kWh = 0
    for plant in production_plants:
      try:
        total_production_kWh += plant.estimated_annual_production_kWh
      except KeyError:
        pass
    return total_production_kWh

  else:
    return None



if __name__=="__main__":
	pass
