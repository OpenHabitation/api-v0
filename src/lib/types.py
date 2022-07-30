from typing import Union


COORDINATES_SOURCE = "Bundesamt für Statistik, Eidg. Gebäude- und Wohnungsregister GWR, https://opendata.swiss/de/dataset/eidg-gebaude-und-wohnungsregister-gwr"

ANNUAL_PRODUCTION_SOURCE = "Calculated based on 'Bundesamt für Energie BFE Schweiz, Elektrizitätsproduktionsanlagen, https://opendata.swiss/de/dataset/elektrizitatsproduktionsanlagen' and 'European Union, Photovoltaic Geographical Information System PVGIS, https://re.jrc.ec.europa.eu/pvg_tools/en/'"

SPACE_HEATING_SOURCE = "Bundesamt für Statistik, Eidg. Gebäude- und Wohnungsregister GWR, https://opendata.swiss/de/dataset/eidg-gebaude-und-wohnungsregister-gwr"
DOMESTIC_HOT_WATER_SOURCE = "Bundesamt für Statistik, Eidg. Gebäude- und Wohnungsregister GWR, https://opendata.swiss/de/dataset/eidg-gebaude-und-wohnungsregister-gwr"

SPACE_HEATING_DEMAND_KWH_SOURCE = "Bundesamt für Energie BFE Schweiz, Eignung von Hausdächern für die Nutzung von Sonnenenergie, https://opendata.swiss/de/dataset/eignung-von-hausdachern-fur-die-nutzung-von-sonnenenergie"
DOMESTIC_HOT_WATER_DEMAND_KWH_SOURCE = "Bundesamt für Energie BFE Schweiz, Eignung von Hausdächern für die Nutzung von Sonnenenergie, https://opendata.swiss/de/dataset/eignung-von-hausdachern-fur-die-nutzung-von-sonnenenergie"

ELECTRICITY_PRODUCTION_SOURCE = "Bundesamt für Energie BFE Schweiz, Elektrizitätsproduktionsanlagen, https://opendata.swiss/de/dataset/elektrizitatsproduktionsanlagen"




class Coordinates():
  def __init__(self, egid, lat, lon, gkode, gkodn):
    self.EGID = egid
    self.lat = lat
    self.lon = lon
    self.GKODE = gkode
    self.GKODN = gkodn


  def to_dict(self):
    return {
      "EGID": self.EGID,
      "lat": self.lat,
      "lon": self.lon,
      "GKODE": self.GKODE,
      "GKODN": self.GKODN,
    }




class PlantInfo():
  def __init__(self, total_power, plant_type, mountingplace, beginning_of_operation, estimated_annual_production_kWh=None):
    self.total_power = total_power
    self.plant_type = plant_type
    self.mountingplace = mountingplace
    self.beginning_of_operation = beginning_of_operation
    self.estimated_annual_production_kWh = estimated_annual_production_kWh

  def to_dict(self):
    return {
      "total_power": self.total_power,
      "plant_type": self.plant_type,
      "mountingplace": self.mountingplace,
      "beginning_of_operation": self.beginning_of_operation,
      "estimated_annual_production_kWh": self.estimated_annual_production_kWh,
    }





SpaceHeatingDemand = int | float | None
DomesticHotWaterDemand = int | float | None





class HeatingDevice():
  def __init__(self, heat_generator, energy_source, information_source, information_last_updated):
    self.heat_generator = heat_generator
    self.energy_source = energy_source
    self.information_source = information_source
    self.information_last_updated = information_last_updated


  def to_dict(self):
    return {
      "heat_generator": self.heat_generator,
			"energy_source": self.energy_source,
			"information_source": self.information_source,
			"information_last_updated": self.information_last_updated
    }



class SpaceHeatingInfo():
  def __init__(self, main_device: Union[HeatingDevice, None] = None, secondary_device: Union[HeatingDevice, None] = None):
    self.main_device = main_device
    self.secondary_device = secondary_device

  def to_dict(self):
    return {
      "main_device": None if self.main_device == None else self.main_device.to_dict(),
      "secondary_device": None if self.secondary_device == None else self.secondary_device.to_dict(),
    }




class DomesticHotWaterInfo():
  def __init__(self, main_device: Union[HeatingDevice, None] = None, secondary_device: Union[HeatingDevice, None] = None):
    self.main_device = main_device
    self.secondary_device = secondary_device

  def to_dict(self):
    return {
      "main_device": None if self.main_device == None else self.main_device.to_dict(),
      "secondary_device": None if self.secondary_device == None else self.secondary_device.to_dict(),
    }
