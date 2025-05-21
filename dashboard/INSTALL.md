# SPDX-License-Identifier: MIT
# Copyright (c) 2025 Vamsi Duvvuri

# Koya Workflow Subway Map Dashboard - Installation Guide

This guide provides detailed instructions for setting up the Koya Workflow Subway Map Dashboard.

## System Requirements

- **Node.js**: Version 16.0 or higher
- **npm**: Version 7.0 or higher (comes with Node.js)
- **Browser**: Modern browser with ES6 support (Chrome, Firefox, Safari, Edge)
- **Operating System**: Any system that supports Node.js (Windows, macOS, Linux)

## Installation Steps

### 1. Clone or Download the Repository

If using Git:
```bash
git clone https://github.com/yourusername/koya-workflow-dashboard.git
cd koya-workflow-dashboard
```

Or download and extract the ZIP file, then navigate to the extracted directory.

### 2. Install Dependencies

Using npm:
```bash
cd dashboard
npm install
```

Using Yarn (if you prefer):
```bash
cd dashboard
yarn install
```

This will install all necessary dependencies defined in the `package.json` file.

### 3. Configure the Application (if needed)

The dashboard comes pre-configured to use static data from our agent workflow documentation. If you want to connect it to live data sources, you'll need to modify the data fetching logic in the future.

### 4. Start the Development Server

```bash
npm run dev
```

This will start the development server and automatically open the dashboard in your default web browser. If it doesn't open automatically, you can access it at http://localhost:5173 (or the port shown in your terminal).

### 5. Building for Production

When you're ready to deploy the dashboard:

```bash
npm run build
```

This creates an optimized production build in the `dist` directory, which you can deploy to any static file hosting service.

## Troubleshooting

If you encounter any issues during installation:

1. **Node.js Version Issues**: Ensure you're using Node.js 16+. You can check with `node -v`.
2. **Dependency Conflicts**: Try removing `node_modules` and the lock file, then reinstall.
   ```bash
   rm -rf node_modules package-lock.json
   npm install
   ```
3. **Port Conflicts**: If port 5173 is already in use, Vite will automatically suggest an alternative port.

## Next Steps

After installation, you can explore the following files to understand and customize the dashboard:

- `src/data/workflows.js` - Static data structure for agents and workflows
- `src/components/SubwayMap.jsx` - Main visualization component
- `src/App.jsx` - Main application structure and layout

## Support

For any issues or questions, please create an issue in the repository or contact the development team.