#!/usr/bin/env python3
"""
Authentication middleware and decorators for MCP Voice Generation Server.
"""

import functools
import logging
from typing import Any, Dict, Optional, Callable
from fastmcp import Context

logger = logging.getLogger(__name__)


class AuthenticationError(Exception):
    """Raised when authentication fails."""
    pass


class AuthMiddleware:
    """Authentication middleware for MCP server."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize authentication middleware.
        
        Args:
            config: Configuration dictionary containing auth settings
        """
        self.config = config
        self.auth_config = config.get('auth', {})
        self.enabled = self.auth_config.get('enabled', False)
        self.api_key = self.auth_config.get('api_key')
        self.header_name = self.auth_config.get('header_name', 'X-API-Key')
        self.require_auth_for_tools = self.auth_config.get('require_auth_for_tools', True)
        
        if self.enabled and not self.api_key:
            raise ValueError("Authentication is enabled but no API key is configured")
    
    def is_authenticated(self, context: Optional[Context] = None) -> bool:
        """
        Check if the current request is authenticated.
        
        Args:
            context: FastMCP context containing request information
            
        Returns:
            bool: True if authenticated, False otherwise
        """
        if not self.enabled:
            return True
        
        if not context:
            logger.warning("No context provided for authentication check")
            return False
        
        # Extract API key from headers
        api_key = self._extract_api_key(context)
        
        if not api_key:
            logger.warning("No API key provided in request")
            return False
        
        # Validate API key
        if api_key != self.api_key:
            logger.warning("Invalid API key provided")
            return False
        
        return True
    
    def _extract_api_key(self, context: Optional[Context]) -> Optional[str]:
        """
        Extract API key from request context.
        
        Args:
            context: FastMCP context
            
        Returns:
            Optional[str]: API key if found, None otherwise
        """
        if not context:
            return None
        
        try:
            # Get the HTTP request from the context
            request = context.request_context.request
            if request and hasattr(request, 'headers'):
                headers = request.headers
                # Try different header name variations
                for header_name in [self.header_name, 'Authorization', 'X-API-Key']:
                    if header_name in headers:
                        api_key = headers[header_name]
                        # Handle "Bearer <token>" format
                        if api_key.startswith('Bearer '):
                            api_key = api_key[7:]
                        return api_key
        except (ValueError, AttributeError) as e:
            # Context is not available outside of a request or request doesn't have headers
            logger.debug(f"Could not extract headers from context: {e}")
        
        # Try to get from request metadata if available
        try:
            metadata = getattr(context, 'metadata', {})
            if isinstance(metadata, dict) and 'api_key' in metadata:
                return metadata['api_key']
        except AttributeError:
            pass
        
        return None
    
    def require_auth(self, func: Callable) -> Callable:
        """
        Decorator to require authentication for a function.
        
        Args:
            func: Function to protect
            
        Returns:
            Callable: Wrapped function with authentication check
        """
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract context from arguments (both args and kwargs)
            context = None
            
            # Check args - look for Context or objects with request_context
            for arg in args:
                if isinstance(arg, Context) or (hasattr(arg, 'request_context') and hasattr(arg, 'metadata')):
                    context = arg
                    break
            
            # Check kwargs if not found in args
            if context is None:
                for value in kwargs.values():
                    if isinstance(value, Context) or (hasattr(value, 'request_context') and hasattr(value, 'metadata')):
                        context = value
                        break
            
            # Check authentication
            if not self.is_authenticated(context):
                error_msg = "Authentication required. Please provide a valid API key."
                logger.error(f"Authentication failed for {func.__name__}")
                
                if context:
                    await context.error(error_msg)
                
                raise AuthenticationError(error_msg)
            
            # Call the original function
            return await func(*args, **kwargs)
        
        return wrapper


def create_auth_middleware(config: Dict[str, Any]) -> Optional[AuthMiddleware]:
    """
    Create authentication middleware from configuration.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Optional[AuthMiddleware]: Auth middleware if enabled, None otherwise
    """
    auth_config = config.get('auth', {})
    if not auth_config.get('enabled', False):
        logger.info("Authentication is disabled")
        return None
    
    try:
        middleware = AuthMiddleware(config)
        logger.info("Authentication middleware created successfully")
        return middleware
    except Exception as e:
        logger.error(f"Failed to create authentication middleware: {e}")
        raise


def auth_required(middleware: Optional[AuthMiddleware]):
    """
    Decorator factory for authentication requirement.
    
    Args:
        middleware: Authentication middleware instance
        
    Returns:
        Callable: Decorator function
    """
    def decorator(func: Callable) -> Callable:
        if not middleware or not middleware.enabled:
            # If auth is disabled, return the original function
            return func
        
        return middleware.require_auth(func)
    
    return decorator
