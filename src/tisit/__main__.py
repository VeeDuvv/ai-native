# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Vamsi Duvvuri

# Fifth Grade Explanation:
# This file is like the "power button" for our knowledge system. When someone runs
# the TISIT package directly, this file gets called and starts up our system.

# High School Explanation:
# This module serves as the entry point when the TISIT package is executed directly.
# It initializes the command-line interface, enabling users to interact with the
# knowledge graph through the CLI without having to import the CLI class explicitly.

from .cli import main

if __name__ == "__main__":
    main()