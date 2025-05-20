# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Vamsi Duvvuri

# Fifth Grade Explanation:
# This program creates a simple web server to show our knowledge dashboard.
# It's like a digital picture frame that displays our computer brain's information.

# High School Explanation:
# This script implements a simple HTTP server using Python's http.server module
# to serve the dashboard HTML file and also handle API requests by proxying them
# to the actual API server.

import http.server
import socketserver
import os
import sys
import json
import urllib.request
from urllib.parse import urlparse, parse_qs
from http import HTTPStatus

PORT = 8080
DASHBOARD_FILE = "simple-dashboard.html"
API_SERVER_URL = "http://localhost:8000"

class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests."""
        parsed_url = urlparse(self.path)
        
        # Handle API proxying
        if parsed_url.path.startswith('/api/'):
            self.proxy_api_request('GET', parsed_url.path[4:], None)
            return
            
        # Serve the dashboard as the root
        if parsed_url.path == "/":
            self.path = DASHBOARD_FILE
            return http.server.SimpleHTTPRequestHandler.do_GET(self)
            
        # Otherwise serve as normal
        return http.server.SimpleHTTPRequestHandler.do_GET(self)
    
    def do_POST(self):
        """Handle POST requests."""
        parsed_url = urlparse(self.path)
        
        # Handle API proxying
        if parsed_url.path.startswith('/api/'):
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length) if content_length > 0 else None
            self.proxy_api_request('POST', parsed_url.path[4:], body)
            return
            
        # Default handler for other POST requests
        self.send_response(HTTPStatus.METHOD_NOT_ALLOWED)
        self.end_headers()
        
    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS."""
        self.send_response(HTTPStatus.OK)
        self.send_cors_headers()
        self.end_headers()
    
    def send_cors_headers(self):
        """Add CORS headers to the response."""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Accept')
    
    def proxy_api_request(self, method, path, body):
        """Proxy a request to the API server."""
        try:
            # Construct the full API URL
            api_url = f"{API_SERVER_URL}{path}"
            print(f"Proxying {method} request to {api_url}")
            
            # Create the request
            req = urllib.request.Request(
                url=api_url,
                data=body,
                method=method
            )
            
            # Copy headers
            for header, value in self.headers.items():
                if header.lower() not in ('host', 'content-length'):
                    req.add_header(header, value)
            
            # Send the request to the API server
            with urllib.request.urlopen(req) as response:
                # Get response data
                response_body = response.read()
                
                # Send response status
                self.send_response(response.status)
                
                # Send headers
                for header, value in response.getheaders():
                    if header.lower() not in ('transfer-encoding', 'connection'):
                        self.send_header(header, value)
                
                # Add CORS headers
                self.send_cors_headers()
                
                # End headers
                self.end_headers()
                
                # Send response body
                self.wfile.write(response_body)
                
        except Exception as e:
            print(f"Error proxying request: {str(e)}")
            self.send_response(HTTPStatus.INTERNAL_SERVER_ERROR)
            self.send_header('Content-Type', 'application/json')
            self.send_cors_headers()
            self.end_headers()
            
            error_message = json.dumps({
                "error": f"Error proxying request: {str(e)}"
            }).encode('utf-8')
            
            self.wfile.write(error_message)

def serve_dashboard():
    """Start the dashboard server."""
    # Check if dashboard file exists
    if not os.path.exists(DASHBOARD_FILE):
        print(f"Error: Dashboard file '{DASHBOARD_FILE}' not found!")
        sys.exit(1)
    
    # Create server
    handler = DashboardHandler
    
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        print(f"Dashboard server started at http://localhost:{PORT}")
        print(f"API requests will be proxied to {API_SERVER_URL}")
        print(f"Press Ctrl+C to stop the server")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("Server stopped")

if __name__ == "__main__":
    serve_dashboard()