


def space_heating_classifier(space_heating_info: dict):

  return "method unimplemented"


def hot_water_classifier(hot_water_info: dict):

  return "method unimplemented"


def electricity_production_exists(production_plants: list):
  if len(production_plants) > 0:
    return "existent"
  else:
    return "unknown"

def get_total_electricity_production(production_plants: list):

  if len(production_plants) > 0:
    total_production_kWh = 0
    for plant in production_plants:
      try:
        total_production_kWh += plant["estimated_annual_production_kWh"]
      except KeyError:
        pass
    return total_production_kWh

  else:
    return None



if __name__=="__main__":
	pass
