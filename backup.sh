#!/bin/bash

# Show to script where conda is installed
source /c/ProgramData/Miniconda3/etc/profile.d/conda.sh

# Activate environment
conda activate auto-sync-local

# Redirect to repository folder
cd "/c/Users/test/Desktop/auto-sync-local"

# Run synchronization script
python synchronize.py