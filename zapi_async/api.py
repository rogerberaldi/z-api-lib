"""Internal API for Z-API HTTP operations."""

from __future__ import annotations
import logging
from typing import Any, Literal
import httpx

from .errors import (
    ZAPIError,
    AuthenticationError,
    InstanceError,
    RateLimitError,
    NetworkError,
    ValidationError,
)

_logger = logging.getLogger(__name__)


class GraphAPI:
    """Internal API class for making HTTP requests to Z-API."""
    
    BASE_URL = "https://api.z-api.io"
    
    def __init__(
        self,
        instance_id: str,
        token: str,
        client_token: str | None = None,
        session: httpx.AsyncClient | None = None,
    ):
        """
        Initialize GraphAPI.
        
        Args:
            instance_id: Z-API instance ID
            token: Z-API token
            client_token: Optional security client token
            session: Optional httpx AsyncClient session
        """
        self.instance_id = instance_id
        self.token = token
        self.client_token = client_token
        self._session = session or httpx.AsyncClient(timeout=30.0)
        self._base_url = f"{self.BASE_URL}/instances/{instance_id}/token/{token}"
    
    def __str__(self) -> str:
        return f"GraphAPI(instance={self.instance_id})"
    
    def _build_url(self, endpoint: str) -> str:
        """
        Build full URL for endpoint.
        
        Args:
            endpoint: API endpoint (without leading slash)
            
        Returns:
            Full URL
        """
        # Remove leading slash if present
        endpoint = endpoint.lstrip('/')
        return f"{self._base_url}/{endpoint}"
    
    def _build_headers(self, extra_headers: dict[str, str] | None = None) -> dict[str, str]:
        """
        Build request headers.
        
        Args:
            extra_headers: Additional headers to include
            
        Returns:
            Complete headers dict
        """
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        
        if self.client_token:
            headers["Client-Token"] = self.client_token
        
        if extra_headers:
            headers.update(extra_headers)
        
        return headers
    
    async def _make_request(
        self,
        method: Literal["GET", "POST", "PUT", "DELETE"],
        endpoint: str,
        json: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        log_request: bool = True,
    ) -> dict[str, Any]:
        """
        Make HTTP request to Z-API.
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            json: JSON request body
            params: URL parameters
            headers: Additional headers
            log_request: Whether to log request details
            
        Returns:
            Response JSON data
            
        Raises:
            AuthenticationError: Invalid credentials
            InstanceError: Instance not connected
            RateLimitError: Rate limit exceeded
            ValidationError: Invalid request
            NetworkError: Network/connection error
            ZAPIError: Other API errors
        """
        url = self._build_url(endpoint)
        request_headers = self._build_headers(headers)
        
        if log_request:
            _logger.debug(f"{method} {url}")
            if json and _logger.isEnabledFor(logging.DEBUG):
                _logger.debug(f"Request body: {json}")
        
        try:
            response = await self._session.request(
                method=method,
                url=url,
                json=json,
                params=params,
                headers=request_headers,
            )
            
            # Log response status
            _logger.debug(f"Response status: {response.status_code}")
            
            # Check for HTTP errors
            if response.status_code >= 400:
                await self._handle_error(response)
            
            # Parse JSON response
            try:
                data = response.json()
                return data
            except Exception:
                # Some endpoints might return empty response
                return {}
        
        except httpx.TimeoutException as e:
            raise NetworkError(f"Request timeout: {e}")
        except httpx.NetworkError as e:
            raise NetworkError(f"Network error: {e}")
        except httpx.HTTPStatusError as e:
            raise ZAPIError(f"HTTP error: {e}", status_code=e.response.status_code)
    
    async def _handle_error(self, response: httpx.Response) -> None:
        """
        Handle error responses.
        
        Args:
            response: HTTP response
            
        Raises:
            Appropriate ZAPIError subclass
        """
        status_code = response.status_code
        
        # Try to parse error message from response
        try:
            error_data = response.json()
            error_message = error_data.get('message') or error_data.get('error') or response.text
        except Exception:
            error_message = response.text or f"HTTP {status_code}"
        
        # Map status codes to exception types
        if status_code == 401 or status_code == 403:
            raise AuthenticationError(
                f"Authentication failed: {error_message}",
                status_code=status_code,
                response_data=error_data if 'error_data' in locals() else {}
            )
        elif status_code == 404:
            raise InstanceError(
                f"Instance not found or not connected: {error_message}",
                status_code=status_code
            )
        elif status_code == 405:
            raise ValidationError(
                f"Method not allowed: Check HTTP method (GET/POST/PUT/DELETE)",
                status_code=status_code
            )
        elif status_code == 415:
            raise ValidationError(
                f"Unsupported media type: Check Content-Type header",
                status_code=status_code
            )
        elif status_code == 429:
            raise RateLimitError(
                f"Rate limit exceeded: {error_message}",
                status_code=status_code
            )
        elif status_code >= 500:
            raise ZAPIError(
                f"Server error: {error_message}",
                status_code=status_code
            )
        else:
            raise ZAPIError(
                f"Request failed: {error_message}",
                status_code=status_code
            )
    
    async def get(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
        **kwargs
    ) -> dict[str, Any]:
        """
        Make GET request.
        
        Args:
            endpoint: API endpoint
            params: URL parameters
            **kwargs: Additional request arguments
            
        Returns:
            Response data
        """
        return await self._make_request("GET", endpoint, params=params, **kwargs)
    
    async def post(
        self,
        endpoint: str,
        json: dict[str, Any] | None = None,
        **kwargs
    ) -> dict[str, Any]:
        """
        Make POST request.
        
        Args:
            endpoint: API endpoint
            json: Request body
            **kwargs: Additional request arguments
            
        Returns:
            Response data
        """
        return await self._make_request("POST", endpoint, json=json, **kwargs)
    
    async def put(
        self,
        endpoint: str,
        json: dict[str, Any] | None = None,
        **kwargs
    ) -> dict[str, Any]:
        """
        Make PUT request.
        
        Args:
            endpoint: API endpoint
            json: Request body
            **kwargs: Additional request arguments
            
        Returns:
            Response data
        """
        return await self._make_request("PUT", endpoint, json=json, **kwargs)
    
    async def delete(
        self,
        endpoint: str,
        **kwargs
    ) -> dict[str, Any]:
        """
        Make DELETE request.
        
        Args:
            endpoint: API endpoint
            **kwargs: Additional request arguments
            
        Returns:
            Response data
        """
        return await self._make_request("DELETE", endpoint, **kwargs)
    
    async def close(self) -> None:
        """Close the HTTP session."""
        await self._session.aclose()
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
