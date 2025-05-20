# -*- coding: utf-8 -*-
# Copyright (c) 2025 Krishna Kumar
# SPDX-License-Identifier: MIT

from abc import ABC, abstractmethod
from typing import Dict, Any, Generator

from sim.model.signal.signal import Signal

from pcalc.boundary import Boundary
from sim.metamodel import DomainContext

class Node(ABC):
    def __init__(self, name: str, config: Dict[str, Any], sim_context: DomainContext) -> None:
        self._name: str = name
        self._config: Dict[str, Any] = config
        self._sim_context = sim_context
        self.env = sim_context.env


    @property
    def name(self) -> str:
        return self._name

    @property
    def config(self) -> Dict[str, Any]:
        return self._config

    @property
    def sim_context(self) -> DomainContext:
        return self._sim_context


class Service(Boundary):
    def on_enter(self, signal_id: str, **kwargs) -> Generator:
        yield from self.perform_service(signal_id, **kwargs)
        yield from self.exit(signal_id, **kwargs)

    def on_exit(self, signal_id: str, **kwargs) -> Generator:
        yield from ()

    def signal_start_service(self, signal_id:str, **kwargs) -> Signal:
        timestamp = self.env.now
        return self.signal_history.element(
            Signal(
                signal_type="start_service",
                source=self.name,
                timestamp=timestamp,
                signal_id=signal_id,
                **kwargs
            )
        )

    def signal_end_service(self, signal_id:str, **kwargs) -> Signal:
        timestamp = self.env.now
        return self.signal_history.element(
            Signal(
                signal_type="end_service",
                source=self.name,
                timestamp=timestamp,
                signal_id=signal_id,
                **kwargs
            )
        )



    @abstractmethod
    def perform_service(self, signal_id: str, **kwargs) -> Generator:
       pass


class BlockingService(Service, ABC):
    pass


class NonBlockingService(Service, ABC):
    pass




