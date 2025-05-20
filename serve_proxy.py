# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Vamsi Duvvuri

# Fifth Grade Explanation:
# This program is like a telephone operator that helps the dashboard talk to the API.
# It passes messages back and forth between them, even if they're in different places.

# High School Explanation:
# This script implements a CORS-aware proxy server using Python's http.server module
# to relay requests from the dashboard to the API server. It adds appropriate CORS
# headers to responses, allowing the dashboard to communicate with the API server
# even when they are running on different origins.

import http.server
import socketserver
import urllib.request
import urllib.error
import json
import sys
from urllib.parse import urlparse

# Configuration
PROXY_PORT = 8081
API_SERVER_URL = "http://localhost:8000"

class CORSProxyHandler(http.server.BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_cors_headers()
        self.end_headers()
    
    def do_GET(self):
        self.proxy_request("GET")
    
    def do_POST(self):
        self.proxy_request("POST")
    
    def do_PUT(self):
        self.proxy_request("PUT")
    
    def do_DELETE(self):
        self.proxy_request("DELETE")
    
    def send_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Accept")
    
    def proxy_request(self, method):
        try:
            # Get the full API URL
            api_url = f"{API_SERVER_URL}{self.path}"
            print(f"Proxying {method} request to {api_url}")
            
            # Read request body for POST/PUT
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length) if content_length > 0 else None
            
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
            
            # Send the request
            with urllib.request.urlopen(req) as response:
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
                self.wfile.write(response.read())
            
        except urllib.error.HTTPError as error:
            self.send_response(error.code)
            self.send_cors_headers()
            self.end_headers()
            error_message = {"error": f"HTTP Error: {error.code} {error.reason}"}
            self.wfile.write(json.dumps(error_message).encode('utf-8'))
        
        except Exception as error:
            self.send_response(500)
            self.send_cors_headers()
            self.end_headers()
            error_message = {"error": f"Proxy Error: {str(error)}"}
            self.wfile.write(json.dumps(error_message).encode('utf-8'))
    
    # Disable logging
    def log_message(self, format, *args):
        return

def start_proxy_server():
    handler = CORSProxyHandler
    with socketserver.TCPServer(("", PROXY_PORT), handler) as httpd:
        print(f"Proxy server running at http://localhost:{PROXY_PORT}")
        print(f"Proxying requests to {API_SERVER_URL}")
        print("Press Ctrl+C to stop the server")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("Proxy server stopped")

if __name__ == "__main__":
    start_proxy_server()