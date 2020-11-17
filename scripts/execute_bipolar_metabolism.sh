#!/bin/bash

#chmod u+x script.sh

# Read private, local file paths.
echo "read private file path variables and organize paths..."
cd ~/paths
path_python_library=$(<"./project_tools_python_library.txt")
path_temporary=$(<"./temporary_bipolar_metabolism.txt")
path_waller="$path_temporary/waller"
path_dock="$path_waller/dock"
path_bipolar_metabolism="$path_waller/bipolar_metabolism"
path_package="$path_bipolar_metabolism/bipolar_metabolism"

# Organize paths to custom package installations.
PYTHONPATH=$path_python_library:$PYTHONPATH
export PYTHONPATH

# Echo each command to console.
set -x

# Determine whether the temporary directory structure already exists.
if [ ! -d $path_dock ]
then
    # Directory does not already exist.
    # Create directory.
    mkdir -p $path_dock
fi

# Execute procedure(s).

python3 $path_package/interface.py main --path_dock $path_dock --heritability