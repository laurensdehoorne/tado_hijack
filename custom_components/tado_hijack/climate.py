"""Platform for Tado climate entities."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .climate_entity import TadoAirConditioning, TadoHeating
from .const import ZONE_TYPE_AIR_CONDITIONING, ZONE_TYPE_HEATING
from .helpers.discovery import yield_zones

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import TadoDataUpdateCoordinator


def _setup_climate_entities_full_cloud(
    coordinator: TadoDataUpdateCoordinator,
) -> list[TadoHeating | TadoAirConditioning]:
    """Set up climate entities for full cloud mode."""
    from .const import GEN_X

    entities: list[TadoHeating | TadoAirConditioning] = []

    if coordinator.generation == GEN_X:
        # Tado X: One entity per room
        entities.extend(
            TadoAirConditioning(coordinator, zone.id, zone.name)
            for zone in yield_zones(coordinator)
        )
    else:
        # V2/V3: Separate heating/AC entities
        entities.extend(
            TadoHeating(coordinator, zone.id, zone.name)
            for zone in yield_zones(coordinator, {ZONE_TYPE_HEATING})
        )
        entities.extend(
            TadoAirConditioning(coordinator, zone.id, zone.name)
            for zone in yield_zones(coordinator, {ZONE_TYPE_AIR_CONDITIONING})
        )

    return entities


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Tado climate entities."""
    coordinator: TadoDataUpdateCoordinator = entry.runtime_data

    # Only create climate entities if full_cloud_mode is enabled
    if coordinator.full_cloud_mode:
        entities = _setup_climate_entities_full_cloud(coordinator)
    else:
        entities = []

    async_add_entities(entities)
