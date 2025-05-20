# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Vamsi Duvvuri

# Fifth Grade Explanation:
# This program creates a simple web server to show our knowledge dashboard.
# It's like a digital picture frame that displays our computer brain's information.

# High School Explanation:
# This script implements a simple HTTP server using Python's http.server module
# to serve the dashboard HTML file. It runs on the same origin as the API server
# to avoid CORS issues when making requests from the browser.

import http.server
import socketserver
import os
import sys
from urllib.parse import urlparse, parse_qs

PORT = 8080
DASHBOARD_FILE = "simple-dashboard.html"

class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Parse the URL
        parsed_url = urlparse(self.path)
        
        # Serve the dashboard as the root
        if parsed_url.path == "/":
            self.path = DASHBOARD_FILE
            return http.server.SimpleHTTPRequestHandler.do_GET(self)
        
        # Otherwise serve as normal
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

def serve_dashboard():
    # Check if dashboard file exists
    if not os.path.exists(DASHBOARD_FILE):
        print(f"Error: Dashboard file '{DASHBOARD_FILE}' not found!")
        sys.exit(1)
    
    # Create server
    handler = DashboardHandler
    
    # Disable logging output from http.server
    handler.log_message = lambda *args: None
    
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        print(f"Dashboard server started at http://localhost:{PORT}")
        print(f"Press Ctrl+C to stop the server")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("Server stopped")

if __name__ == "__main__":
    serve_dashboard()