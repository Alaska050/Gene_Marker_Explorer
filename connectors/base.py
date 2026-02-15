from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import requests

class BaseConnector(ABC):


    def __init__(self, timeout: int = 30):

        self.timeout = timeout
        self._session = requests.Session()

    @property
    @abstractmethod
    def base_url(self) -> str:
        """Return the base URL for this API."""
        pass

    @abstractmethod
    def _build_url(self, identifier: str, **kwargs) -> str:
        """Build the full URL for the request."""

        pass

    @abstractmethod
    def _parse_response(self, response: requests.Response, **kwargs) -> Any:
        """Parse the API response into the desired format."""
        pass

    def _get_headers(self) -> Dict[str, str]:
        """Return headers for the request."""
        return {
            "Accept": "application/json",
            "User-Agent": "GeneMarker-Explorer/0.1.0"
        }

    def fetch(self, identifier: str, **kwargs) -> Any:
        """
        Template method that orchestrates the fetch operation.

        Args:
            identifier: The primary identifier to look up.
            **kwargs: Additional parameters passed to build/parse methods.

        Returns:
            Parsed response data.

        Raises:
            APIError: If the HTTP request fails.
            ParseError: If response parsing fails.
        """
        url = self._build_url(identifier, **kwargs)
        headers = self._get_headers()

        try:
            response = self._session.get(
                url,
                headers=headers,
                timeout=self.timeout
            )
            response.raise_for_status()
        except:
            raise ValueError("Something went wrong")

        return self._parse_response(response, **kwargs)

    def close(self):
        """Close the underlying session."""
        self._session.close()