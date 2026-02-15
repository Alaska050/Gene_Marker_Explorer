"""
Connector factory module.
Provides a centralised way to create API connector instances.
"""

from typing import Dict, Type
from .base import BaseConnector
from .ensembl import EnsemblConnector
from .hpa import HPAConnector


class ConnectorFactory:
    """
    Factory class responsible for creating connector instances.
    Maintains a register of available connectors and
    provides a consistent interface for instantiation.
    """

    #  Registry mapping connector names to their corresponding classes.
    _connectors: Dict[str, Type[BaseConnector]] = {
        "ensembl": EnsemblConnector,
        "hpa": HPAConnector,
    }

    @classmethod
    def create(cls, connector_type: str, **kwargs) -> BaseConnector:
        """
        Create a connector instance by its registered name.
        """
        connector_type = connector_type.lower()

        # Validate connector type before instantiation.
        if connector_type not in cls._connectors:
            available = ", ".join(cls._connectors.keys())
            raise ValueError(
                f"Unknown connector type: '{connector_type}'. "
                f"Available types: {available}"
            )

        connector_class = cls._connectors[connector_type]
        return connector_class(**kwargs)

    @classmethod
    def register(cls, name: str, connector_class: Type[BaseConnector]) -> None:
        """
        Register a new connector class at runtime.
        """
        if not issubclass(connector_class, BaseConnector):
            raise TypeError(
                f"Connector class must inherit from BaseConnector, "
                f"got {connector_class.__name__}"
            )

        cls._connectors[name.lower()] = connector_class

    @classmethod
    def available_connectors(cls) -> list:
        """
        Return a list of registered connector names.
        """
        return list(cls._connectors.keys())

    @classmethod
    def get_ensembl(cls, **kwargs) -> EnsemblConnector:
        """
        Convenience method for creating an Ensembl connector.
        """
        return cls.create("ensembl", **kwargs)

    @classmethod
    def get_hpa(cls, **kwargs) -> HPAConnector:
        """
        Convenience method for creating an HPA connector.
        """
        return cls.create("hpa", **kwargs)
