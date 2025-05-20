# -*- coding: utf-8 -*-
# Copyright (c) 2025 Krishna Kumar
# SPDX-License-Identifier: MIT

from typing import Dict, Any, Optional, List, Callable

from abc import ABC, abstractmethod

import numpy as np

from sim.metamodel import DomainEvent, Signal, Entity
from sim.metamodel import  Timeline, DomainEventListener
from pcalc import Presence, Boundary

from sim.runtime.simulation import Simulation
from sim.model.timeline import DefaultTimeline

class BoundaryBase(Boundary, DomainEventListener, ABC):
    def __init__(self, kind, name, enter_event: str, exit_event: str, config: Dict[str,Any], sim_context: Simulation, id:Optional[str]=None ):
        super().__init__(kind, name, config, sim_context, id)

        self._timeline: Timeline = DefaultTimeline()
        self._sim_context = sim_context
        self._enter_event = enter_event
        self._exit_event = exit_event

        self._sim_context.register_listener(self)

    @property
    def timeline(self) -> Timeline:
        return self._timeline

    def get_signal_presences(self, start_time:float, end_time:float, match: Callable[[DomainEvent], bool] = None, **kwargs) -> List[Presence]:
        domain_events = self.timeline.domain_events
        enter_event = self._enter_event
        exit_event = self._exit_event

        if match is not None:
             domain_events = filter(match, domain_events)

        domain_events = sorted(domain_events, key=lambda s: s.timestamp)

        presences: List[Presence[Signal]] = []
        open_presences: Dict[str, Presence[Signal]] = {}

        for e in domain_events:
            # Once we hit t1, we don't care about later events
            if not open_presences and e.timestamp > end_time:
                break

            if e.event_type == enter_event:
                presence = Presence(boundary=self, element=e.signal, start=e.timestamp, end=np.inf)
                open_presences[e.signal_id] = presence

            elif e.event_type == exit_event:
                presence = open_presences.pop(e.signal_id, None)
                if presence:
                    presence.end = e.timestamp
                    # If it ends within window, include it
                    if presence.overlaps(start_time, end_time):
                        presences.append(presence)
                else:
                    # Exit without entry: assume it was open from time t0
                    presence = Presence(boundary=self, element=e.signal, start=0.0, end=e.timestamp)
                    if presence.overlaps(start_time, end_time):
                        presences.append(presence)

            # Flush any still-open presences: event stream ended without an exit signal seen.
        for presence in open_presences.values():
            if presence.overlaps(start_time, end_time):
                presences.append(presence)
        return presences

    def get_entity_presences(self, start_time: float, end_time: float, match: Optional[Callable[[DomainEvent], bool]]=None, **kwargs) -> List[Presence]:
        raise NotImplemented("Entity Presences not implemented for BoundaryBase")


    @abstractmethod
    def on_domain_event(self, event: DomainEvent) -> None:...