from operator import truediv
from typing import Union
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


def get_pv_requirement(gwr_info: GWRInfo) -> bool:
  """Gets pv requirements for building

  Parameters
  ----------
  gwr_info : GWRInfo
      _description_

  Returns
  -------
  bool
      pv required or not
  """

  if gwr_info.GBAUJ != None:
    if gwr_info.GBAUJ >= 2015:
      return True
    else:
      return False

  elif gwr_info.GBAUP != None:
    if gwr_info.GBAUP >= 8023:
      return True
    else:
      return False

  # At the moment we return False if both year and period are not provided.
  else:
    return False




def pv_requirement_satisfied(plants: List[PlantInfo], gwr_info: GWRInfo) -> str:
  """Is the pv requirement of EcoHabitas satisfied?

  Parameters
  ----------
  plants : List[PlantInfo]
      production plants of the building
  gwr_info : GWRInfo
      _description_

  Returns
  -------
  str
      _description_
  """

  pv_required = get_pv_requirement(gwr_info)
  has_pv = len(plants) > 0

  if has_pv:
    return "complies with photovoltaics requirement by EcoHabitas"

  else:
    if pv_required == False:
      return "no photovoltaics requirement by EcoHabitas"
    else:
      return "may not comply with photovoltaics requirement by EcoHabitas"



def get_gebf_estimated(gwr_info: GWRInfo) -> float | None:
  """Estimates the Energiebezugsfläche based on buidling area and number of floors

  Parameters
  ----------
  gwr_info : GWRInfo
      _description_

  Returns
  -------
  float
      estimated GEBF
  """
  if gwr_info.GEBF != None:
    return gwr_info.GEBF

  elif gwr_info.GAREA != None and gwr_info.GASTW != None:
    return gwr_info.GAREA * gwr_info.GASTW

  else:
    return None



def get_pv_index_1(gwr_info: GWRInfo, plants: list[PlantInfo]) -> Union[float, None]:
  """
  Kennzahl 1: PV-Leistung («total_power») dividiert durch
  «energy_reference_area_EBF_m2» bzw. «energy_reference_area_EBF_m2_estimated»
  multipliziert mit Faktor 1'000 → Wiedergabe «pvpower_to_EBF_W_m2» [W/m2]

  Parameters
  ----------
  gwr_info : GWRInfo
      _description_
  plants : list[PlantInfo]
      _description_

  Returns
  -------
  Union[float, None]
      PV Kennzahl 1 [W/m2]
  """

  total_production = get_total_pv_power(plants)
  gebf_estimated = get_gebf_estimated(gwr_info)

  if gebf_estimated != None:
    return total_production / gebf_estimated * 1000
  else:
    return None



def get_pv_index_2(gwr_info: GWRInfo, plants: list[PlantInfo]) -> Union[float, None]:
  """
  Kennzahl 2: PV-Leistung («total_power») dividiert durch GAREA (Gebäudefläche)
  multipliziert mit Faktor 1'000 → Wiedergabe «pvpower_to_building_area_W_m2» [W/m2]
  [[[Vielleicht können wir in einem späteren Schritt GAREA mit der Information
  «Grundstückfläche» austauschen. Die «Grundstückfläche» gibt es im GWR aber leider nicht
  und wir müssten dazu Daten aus einer anderen Datenquelle holen]]]

  Parameters
  ----------
  gwr_info : GWRInfo
      _description_
  plants : list[PlantInfo]
      _description_

  Returns
  -------
  Union[float, None]
      PV Kennzahl 2 [W/m2]
  """

  total_production = get_total_pv_power(plants)

  if gwr_info.GAREA != None:
    return total_production / gwr_info.GAREA * 1000
  else:
    return None



def get_heating_demand_index_1(gwr_info: GWRInfo, space_heating_demand: SpaceHeatingDemand) -> Union[float, None]:
  """
  Kennzahl 1: Raumwärmebedarf («space_heating_demand_kwh) dividiert durch
  «energy_reference_area_EBF_m2» bzw. «energy_reference_area_EBF_m2_estimated» →
  Wiedergabe «energy_index_space_heating_kWh_m2a» [kWh/(m2*a)]

  Parameters
  ----------
  gwr_info : GWRInfo
      _description_
  space_heating_demand: SpaceHeatingDemand
      _description_

  Returns
  -------
  Union[float, None]
      Raumwärmebedarf Kennzahl 1 [kWh/(m2*a)]
  """

  gebf_estimated = get_gebf_estimated(gwr_info)

  if gebf_estimated != None and space_heating_demand != None:
    return space_heating_demand / gebf_estimated
  else:
    return None




def get_hot_water_demand_index_1(gwr_info: GWRInfo, hot_water_demand: DomesticHotWaterDemand) -> Union[float, None]:
  """
  Kennzahl 1: Warmwasserbedarf («domestic_hot_water_demand_kwh) dividiert durch
  «energy_reference_area_EBF_m2» bzw. «energy_reference_area_EBF_m2_estimated»
  Wiedergabe «energy_index_domestic_hot_water_kWh_m2a» [kWh/(m2*a)]

  Parameters
  ----------
  gwr_info : GWRInfo
      _description_
  hot_water_demand: DomesticHotWaterDemand
      _description_

  Returns
  -------
  Union[float, None]
      Warmwasserbedarf Kennzahl 1 [kWh/(m2*a)]
  """

  gebf_estimated = get_gebf_estimated(gwr_info)

  if gebf_estimated != None and hot_water_demand != None:
    return hot_water_demand / gebf_estimated
  else:
    return None


def space_heating_classifier(space_heating_info: SpaceHeatingInfo) -> Union[str, None]:
  """_summary_

  Parameters
  ----------
  space_heating_info : SpaceHeatingInfo
      _description_

  Returns
  -------
  Union[str, None]
      _description_
  """

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



def hot_water_classifier(hot_water_info: DomesticHotWaterInfo) -> Union[str, None]:

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


def get_total_electricity_production(production_plants: list[PlantInfo]) -> Union[float, int, None]:

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


def get_total_pv_power(production_plants: list[PlantInfo]):

  total_power = 0

  for plant in production_plants:
    if plant.plant_type == "PV":
      total_power += plant.total_power

  return total_power



if __name__=="__main__":
	pass
