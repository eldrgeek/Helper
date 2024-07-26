#!/bin/bash

# ... (previous parts of the script remain unchanged)

# Set up client
cd ./client
npx create-react-app . --template typescript
npm install socket.io-client

# Create a .env file in the client directory to increase memory limit
echo "GENERATE_SOURCEMAP=false" > .env
echo "TSC_COMPILE_ON_ERROR=true" >> .env
echo "DISABLE_NEW_JSX_TRANSFORM=true" >> .env

# Create a custom React app rescripts configuration
cat << EOF > .rescriptsrc.js
module.exports = [
  config => {
    config.optimization.splitChunks = {
      cacheGroups: {
        default: false,
      },
    };
    config.optimization.runtimeChunk = false;
    return config;
  },
  ['use-babel-config', '.babelrc'],
];
EOF

# Create a .babelrc file
cat << EOF > .babelrc
{
  "presets": [
    "react-app"
  ]
}
EOF

# Update package.json to use rescripts
sed -i 's/"react-scripts /"react-app-rewired /g' package.json

# Install necessary dependencies
npm install --save-dev @rescripts/cli react-app-rewired

# ... (rest of the script remains unchanged)