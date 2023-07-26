#!/bin/bash

# Exit script if any command fails
set -e

# Clone the Llama repo
git clone https://github.com/ggerganov/llama.cpp

# Enter the repo directory
cd llama.cpp

# Build the project
make

# Exit the repo directory
cd ..

# Set CMAKE_ARGS environmental variable
export CMAKE_ARGS="-DLLAMA_CUBLAS=on"

# Set FORCE_CMAKE environmental variable
export FORCE_CMAKE=1

# Install llama-cpp-python
pip install llama-cpp-python --no-cache-dir

echo "Installation complete"
