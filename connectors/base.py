"""
Base connector module.
Defines a reusable abstract connector for interacting with REST APIs.
Concrete connectors (Ensembl and HPA) inherit from this class
and implement API specific behaviour.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import requests

class BaseConnector(ABC):
    """
    Abstract base class for API connectors.
    """

    def __init__(self, timeout: int = 30):
        # Default timeout for HTTP requests.
        self.timeout = timeout

        # Reusable session improves performance for multiple requests.
        self._session = requests.Session()

    @property
    @abstractmethod
    def base_url(self) -> str:
        """
        Return the base URL for the API.
        Must be implemented by subclasses.
        """
        pass

    @abstractmethod
    def _build_url(self, identifier: str, **kwargs) -> str:
        """
        Construct the full request URL.
        """
        pass

    @abstractmethod
    def _parse_response(self, response: requests.Response, **kwargs) -> Any:
        """
        Parse the HTTP response into structured data.
        """
        pass

    def _get_headers(self) -> Dict[str, str]:
        """
        Return headers for the API request.
        """
        return {
            "Accept": "application/json",
            "User-Agent": "GeneMarker-Explorer/0.1.0"
        }

    def fetch(self, identifier: str, **kwargs) -> Any:
        """
        Template method that performs the full request workflow.
        1. Build request URL
        2. Send HTTP request
        3. Validate response status
        4. Parse response into structured data
        """

        # Construct full endpoint URL.
        url = self._build_url(identifier, **kwargs)

        # Retrieve headers (can be overridden by subclasses)/
        headers = self._get_headers()

        try:
            response = self._session.get(
                url,
                headers=headers,
                timeout=self.timeout
            )
            response.raise_for_status()

        # Catch request related issues.
        except:
            raise ValueError("Something went wrong")

        # Delegate response parsing to subclass implementation.
        return self._parse_response(response, **kwargs)

    def close(self):
        """
        Close the underlying session.
        """
        self._session.close()