from typing import Dict, Type
from .base import BaseConnector
from .ensembl import EnsemblConnector
from .hpa import HPAConnector


class ConnectorFactory:
    """
    Factory for creating API connectors.

    Implements the Factory pattern to decouple connector creation from usage.
    Allows easy registration of new connector types without modifying client code.
    """

    # Registry of available connectors
    _connectors: Dict[str, Type[BaseConnector]] = {
        "ensembl": EnsemblConnector,
        "hpa": HPAConnector,
    }

    @classmethod
    def create(cls, connector_type: str, **kwargs) -> BaseConnector:
        """
        Create a connector instance by type name.

        Args:
            connector_type: Name of the connector ('ensembl', 'hpa').
            **kwargs: Additional arguments passed to connector constructor.

        Returns:
            Instance of the requested connector.

        Raises:
            ValueError: If connector type is not registered.
        """
        connector_type = connector_type.lower()

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
        Register a new connector type.

        Args:
            name: Name to register the connector under.
            connector_class: Connector class (must inherit from BaseConnector).

        Raises:
            TypeError: If connector_class doesn't inherit from BaseConnector.
        """
        if not issubclass(connector_class, BaseConnector):
            raise TypeError(
                f"Connector class must inherit from BaseConnector, "
                f"got {connector_class.__name__}"
            )

        cls._connectors[name.lower()] = connector_class

    @classmethod
    def available_connectors(cls) -> list:
        """Return list of available connector type names."""
        return list(cls._connectors.keys())

    @classmethod
    def get_ensembl(cls, **kwargs) -> EnsemblConnector:
        """Convenience method to create an Ensembl connector."""
        return cls.create("ensembl", **kwargs)

    @classmethod
    def get_hpa(cls, **kwargs) -> HPAConnector:
        """Convenience method to create an HPA connector."""
        return cls.create("hpa", **kwargs)
