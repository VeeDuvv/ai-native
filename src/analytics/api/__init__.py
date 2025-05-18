# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Vamsi Duvvuri

# Fifth Grade Explanation:
# This file helps connect all the parts of the analytics system with the rest of the app.
# It's like a doorway that lets other programs ask for information about how well ads are doing.

# High School Explanation:
# This module initializes the analytics API package and provides interfaces for other
# parts of the application to interact with the analytics system. It exposes endpoints
# for querying analytics data, generating reports, and accessing insights through a
# consistent API interface.

from .reporting import AnalyticsReportingAPI, ReportFormatter