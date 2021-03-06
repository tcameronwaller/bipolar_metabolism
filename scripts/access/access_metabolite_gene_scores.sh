#!/bin/bash

#chmod u+x script.sh

###########################################################################
###########################################################################
###########################################################################
# This script organizes paths and parameters to access local information
# about persons and phenotypes in the UKBiobank.
###########################################################################
###########################################################################
###########################################################################

###########################################################################
# Read private, local file paths.
echo "read private file path variables and organize paths..."
cd ~/paths
path_ukbiobank_metabolites=$(<"./batzler_ukbiobank_metabolites.txt")
path_temporary=$(<"./processing_bipolar_metabolism.txt")
path_dock="$path_temporary/waller/dock"
path_access_metabolites="$path_dock/access/ukbiobank_metabolites"

# Echo each command to console.
#set -x
# Suppress echo each command to console.
set +x

# Determine whether the temporary directory structure already exists.
if [ ! -d $path_access_metabolites ]; then
    # Directory does not already exist.
    # Create directory.
    mkdir -p $path_access_metabolites
fi

# Define glob pattern to recognize relevant files.
pattern="${path_ukbiobank_metabolites}/UKB_M?????.metal.pos_imp0.8_maf0.01.*"
# Iterate on all files and directories in parent directory.
for file in $path_ukbiobank_metabolites/*; do
  if [ -f "$file" ]; then
    # Current content item is a file.
    echo $file
    if [[ "$file" == ${pattern} ]]; then
      # File name matches glob pattern.
      echo "... pattern match! ..."
      base_name="$(basename -- $file)"
      # Copy the file to new directory.
      cp $file "$path_access_metabolites/$base_name"
    fi
  fi
done
