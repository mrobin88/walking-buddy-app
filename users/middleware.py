import time
import psutil
import logging
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger('performance')

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