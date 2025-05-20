# -*- coding: utf-8 -*-
# Copyright (c) 2025 Krishna Kumar
# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import Protocol, Any, Optional, Dict, TYPE_CHECKING
from abc import ABC, abstractmethod
from sim.model.registry import Registry

if TYPE_CHECKING:
    from prototypes.queueing_network.base_node import Node


# ---- Protocol: Routing Function Type ----
class RouterProtocol(Protocol):
    def __init__(self, node: Node, **params: Any): ...
    def __call__(self, signal_id: str, node: Node, **kwargs: Any) -> Optional[str]: ...

# ---- Mixin: Routing Initialization and Dispatch ----
class RoutingMixin(ABC):
    routing_fn: RouterProtocol  # will be initialized by _init_routing

    # must be called from the subclass mixing this in.
    def setup_routing(self, config: Dict[str, Any], node: Node) -> None:
        self.routing_fn = resolve_routing(config, node)

    @abstractmethod
    def route(self, signal_id: str, **kwargs) -> Node:
        pass


# ---- Factory: Router Registry with Parameterization ----
router_registry: Registry[RouterProtocol] = Registry()



# ---- Pure utility function to resolve routing function/class from config ----
def resolve_routing(config: Dict[str, Any], node: "Node") -> RouterProtocol:
    if "router" in config:
        router_name = config["router"]
        router_params = config.get("router_params", {})
        return router_registry.create(router_name, node=node, router_params=router_params)

    if "route" in config:
        route_fn = config["route"]
        if not callable(route_fn):
            raise TypeError(f"'route' must be callable in node {node.name}")
        return route_fn

    raise ValueError(f"Node {node.name} must specify either 'router' or 'route' in config.")