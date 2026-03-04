"""Unified executor for dispatching commands to generation-specific executors."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from ..const import GEN_CLASSIC, GEN_X
from .tadov3.executor import TadoV3Executor
from .tadox.executor import TadoXExecutor

if TYPE_CHECKING:
    from ..coordinator import TadoDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


class TadoUnifiedExecutor:
    """Dispatches command batches to generation-specific executor."""

    def __init__(self, coordinator: TadoDataUpdateCoordinator) -> None:
        """Initialize unified executor."""
        self.coordinator = coordinator
        self._classic_executor = TadoV3Executor(coordinator, coordinator.client)
        self._x_executor = None
        if hasattr(coordinator, "tadox_bridge") and coordinator.tadox_bridge:
            self._x_executor = TadoXExecutor(coordinator, coordinator.tadox_bridge)

    async def execute_batch(self, merged_data: dict[str, Any]) -> None:
        """Execute command batch using appropriate executor."""
        generation = getattr(self.coordinator, "generation", GEN_CLASSIC)

        if generation == GEN_X:
            if not self._x_executor:
                if bridge := getattr(self.coordinator, "tadox_bridge", None):
                    self._x_executor = TadoXExecutor(self.coordinator, bridge)
                else:
                    _LOGGER.error("Tado X executor not available")
                    return
            _LOGGER.debug("Dispatching to Tado X executor")
            await self._x_executor.execute_batch(merged_data)
        else:
            _LOGGER.debug("Dispatching to Classic executor")
            await self._classic_executor.execute_batch(merged_data)
