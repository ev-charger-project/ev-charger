# Add the root directory to the Python path
import os
import sys
import logging

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(root_dir)

from app.constant.enum.availability import AvailabilityEnum
from app.constant.enum.power_plug_type import PowerModel

logger = logging.getLogger(__name__)


def create_ev_chargers_from_data(
    locations_and_items,
    ev_charger_service,
    power_plug_type_service,
    power_output_service,
):
    from app.schema.ev_charger_schema import CreateEVCharger, CreatePort
    from app.schema.power_plug_type_schema import CreatePowerPlugType
    from app.schema.power_output_schema import CreatePowerOutput
    import datetime

    for location, item in locations_and_items:
        extended = item.get("extended", {})
        ev_availability = extended.get("evAvailability", {})
        ev_station = extended.get("evStation", {})
        station_list = ev_availability.get("stations", [])
        connectors_info = ev_station.get("connectors", [])
        if not station_list:
            logger.warning(f"No station_list found for location {location.id}")
            continue

        evses = station_list[0].get("evses", [])
        for evse in evses:
            evc_here_id = evse.get("id")
            cpo_id = evse.get("cpoId")
            cpo_evse_emi3_id = evse.get("cpoEvseEMI3Id")
            availability = AvailabilityEnum(evse.get("state", "UNAVAILABLE"))
            last_updated = evse.get("last_updated")
            if last_updated:
                try:
                    last_updated = datetime.datetime.fromisoformat(
                        last_updated.replace("Z", "+00:00")
                    )
                except Exception as e:
                    logger.warning(f"Invalid last_updated format: {last_updated} ({e})")
                    last_updated = None

            ports = []
            for connector in evse.get("connectors", []):
                type_id = connector.get("typeId")
                port_here_id = connector.get("id")
                connector_detail = next(
                    (
                        c
                        for c in connectors_info
                        if c.get("connectorType", {}).get("id") == type_id
                    ),
                    None,
                )
                if not connector_detail:
                    logger.warning(
                        f"Connector type {type_id} not found in evStation.connectors for charger {evc_here_id}."
                    )
                    continue

                supplier_name = connector_detail.get("supplierName")
                connector_type = connector_detail.get("connectorType", {})
                plug_type = connector_type.get("name")
                plug_type_id = connector_type.get("id")
                fixed_plug = connector_detail.get("fixedCable")
                volts_range = connector_detail.get("chargingPoint", {}).get(
                    "voltsRange", ""
                )
                amps_range = connector_detail.get("chargingPoint", {}).get(
                    "ampsRange", ""
                )
                max_power_level = connector_detail.get("maxPowerLevel")

                power_model = PowerModel.DC if "DC" in volts_range else PowerModel.AC

                voltage = None
                amperage = None
                try:
                    voltage = int(
                        volts_range.split("-")[0].replace("V", "").replace(" ", "")
                    )
                except Exception:
                    logger.warning(f"Could not parse voltage from '{volts_range}'")
                    pass
                try:
                    amperage = int(amps_range.replace("A", "").replace(" ", ""))
                except Exception:
                    logger.warning(f"Could not parse amperage from '{amps_range}'")
                    pass

                # Create or get PowerPlugType
                power_plug_type_schema = CreatePowerPlugType(
                    supplier_name=supplier_name,
                    power_model=power_model,
                    plug_type=plug_type,
                    plug_type_id=plug_type_id,
                    fixed_plug=fixed_plug,
                    plug_image_url=None,
                    additional_note=None,
                    power_plug_region=None,
                )
                power_plug_type = power_plug_type_service.add(power_plug_type_schema)

                # Create or get PowerOutput
                power_output_schema = CreatePowerOutput(
                    output_value=max_power_level,
                    voltage=voltage,
                    amperage=amperage,
                    charging_speed=None,
                    description=None,
                )
                power_output = power_output_service.add(power_output_schema)

                port = CreatePort(
                    here_id=port_here_id,
                    power_plug_type_id=power_plug_type.id,
                    power_output_id=power_output.id,
                )
                ports.append(port)

            ev_charger_schema = CreateEVCharger(
                location_id=location.id,
                here_id=evc_here_id,
                cpo_id=cpo_id,
                cpo_evse_emi3_id=cpo_evse_emi3_id,
                availability=availability,
                last_updated=last_updated,
                station_name=None,
                installation_date=None,
                last_maintenance_date=None,
                ev_charger_ports=ports,
            )
            try:
                ev_charger_service.add(ev_charger_schema)
                logger.info(
                    f"Upserted EV charger {evc_here_id} at location {location.id}"
                )
            except Exception as e:
                logger.warning(
                    f"Failed to upsert EV charger {evc_here_id} at location {location.id}: {e}"
                )
