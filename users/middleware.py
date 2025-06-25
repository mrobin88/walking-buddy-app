import time
import psutil
import logging
import re
from django.utils.deprecation import MiddlewareMixin
from django.middleware.csrf import CsrfViewMiddleware, get_token

logger = logging.getLogger('performance')

class CSRFExemptionMiddleware(MiddlewareMixin):
    """Middleware to handle CSRF tokens for authentication endpoints."""
    
    EXEMPT_URLS = [
        r'^/api/auth/login/$',
        r'^/api/auth/register/$',
        r'^/api/auth/token/refresh/$',
        r'^/api/auth/token/verify/$',
    ]
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        # For login and register endpoints, we want to allow CSRF tokens
        if any(re.match(url, request.path) for url in self.EXEMPT_URLS):
            request.csrf_processing_done = True
            return None
        return None

    def process_response(self, request, response):
        # For login and register endpoints, return CSRF token in headers
        if any(re.match(url, request.path) for url in self.EXEMPT_URLS):
            if 'csrftoken' not in request.COOKIES:
                # Create a new CSRF token if it doesn't exist
                csrf_token = get_token(request)
                response.set_cookie('csrftoken', csrf_token)
                response['X-CSRFToken'] = csrf_token
        return response

    def process_request(self, request):
        # For all API endpoints, we want to allow CSRF tokens
        if request.path.startswith('/api/'):
            # Allow CSRF tokens for these endpoints
            request.csrf_processing_done = True
            # Also set the CSRF token in the request
            if not request.COOKIES.get('csrftoken'):
                request.COOKIES['csrftoken'] = request.META.get('CSRF_COOKIE', '')
        return None

class PerformanceMonitoringMiddleware(MiddlewareMixin):
    """Middleware to monitor request performance and system resources."""
    
    def process_request(self, request):
        # Record start time
        request.start_time = time.time()
        
        # Log system resources
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        
        logger.debug(f"Request started: {request.path} | CPU: {cpu_percent}% | Memory: {memory.percent}%")
        
    def process_response(self, request, response):
        # Calculate processing time
        if hasattr(request, 'start_time'):
            processing_time = time.time() - request.start_time
            
            # Log performance metrics
            logger.info(f"Request completed: {request.path} | Time: {processing_time:.3f}s | Status: {response.status_code}")
            
            # Add processing time to response headers
            response['X-Processing-Time'] = f"{processing_time:.3f}"
            
        return response

class DatabaseQueryMonitorMiddleware(MiddlewareMixin):
    """Middleware to monitor database query performance."""
    
    def process_request(self, request):
        from django.db import connection
        request.db_queries_start = len(connection.queries)
        
    def process_response(self, request, response):
        from django.db import connection
        
        if hasattr(request, 'db_queries_start'):
            queries_count = len(connection.queries) - request.db_queries_start
            total_time = sum(float(q['time']) for q in connection.queries[request.db_queries_start:])
            
            if queries_count > 0:
                logger.debug(f"DB Queries: {queries_count} | Total time: {total_time:.3f}s | Path: {request.path}")
                
        return response
    
    def process_request(self, request):
        # Patterns for URLs that should be exempt from CSRF
        exempt_patterns = [
            r'^/api/.*$',  # All API endpoints
            r'^/admin/.*$',  # Admin endpoints
        ]
        
        # Check if the request path matches any exempt pattern
        path = request.path_info.lstrip('/')
        
        for pattern in exempt_patterns:
            if re.match(pattern, path):
                # Set a flag to skip CSRF validation
                request._skip_csrf_validation = True
                break
        
        return None 