import lib.constants as constants
from lib.types import *


class UknownHeatingCodeError(Exception): pass

def get_string_list(code_list):
  return [constants.HEATING_CODES_EN[code] for code in code_list]


RENEWABLE_LIST = get_string_list(["7410", "7411", "7420", "7421", "7501", "7510", "7511", "7512", "7513", "7540", "7541", "7542", "7543", "7550", "7570", "7580", "7581", "7582", "7610", "7620"])
NO_SYSTEM_REGISTERED_LIST = get_string_list(["7400", "7500", "7600"])
UNKNOWN_LIST = get_string_list(["7430", "7431", "7432", "7433", "7434", "7435", "7436", "7440", "7441", "7460", "7461", "7499", "7598", "7599", "7630", "7632", "7634", "7640", "7660", "7699"])
INEFFICIENT_LIST = get_string_list(["7450", "7451", "7452", "7560", "7650", "7651"])
NON_RENEWABLE_LIST = get_string_list(["7520", "7530"])



def get_quality_from_code(code: str) -> str:

  if code in RENEWABLE_LIST:
    return "renewable"
  elif code in NON_RENEWABLE_LIST:
    return "non-renewable"
  elif code in INEFFICIENT_LIST:
    return "renewable but inefficient"
  elif code in NO_SYSTEM_REGISTERED_LIST:
    return "no system registered"
  elif code in UNKNOWN_LIST:
    return "unknown"
  else:
    raise UknownHeatingCodeError("Unknown heating code: %s" %code)


def space_heating_classifier(space_heating_info: SpaceHeatingInfo) -> str | None:

  # for now only main device considered
  main_device = space_heating_info.main_device

  if main_device == None:
    return None

  heating_quality_energy_source = get_quality_from_code(main_device.energy_source)
  heating_quality_heat_generator = get_quality_from_code(main_device.heat_generator)

  if (heating_quality_energy_source in ["no system registered", "unknown"]) and \
    (heating_quality_heat_generator not in ["no system registered", "unknown"]):
    return heating_quality_heat_generator

  return heating_quality_energy_source


def hot_water_classifier(hot_water_info: DomesticHotWaterInfo) -> str | None:

  # for now only main device considered
  main_device = hot_water_info.main_device

  if main_device == None:
    return None

  heating_quality_energy_source = get_quality_from_code(main_device.energy_source)
  heating_quality_heat_generator = get_quality_from_code(main_device.heat_generator)

  if (heating_quality_energy_source in ["no system registered", "unknown"]) and \
    (heating_quality_heat_generator not in ["no system registered", "unknown"]):
    return heating_quality_heat_generator

  return heating_quality_energy_source


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
