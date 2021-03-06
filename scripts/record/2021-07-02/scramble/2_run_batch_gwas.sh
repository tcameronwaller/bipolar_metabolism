#!/bin/bash

###########################################################################
# Specify arguments for qsub command.
# Note that bash does not interpret qsub parameters, which are bash comments.
# Bash will not expand variables in qsub parameters.
# Shell.
#$ -S /bin/bash
# Name of job.
#$ -N waller_gwas
# Contact.
# "b": beginning, "e": end, "a": abortion, "s": suspension, "n": never
#$ -M tcameronwaller@gmail.com
#$ -m as
# Standard output and error.
# Specify as arguments when calling qsub.
### -o "./out"
### -e "./error"
# Queue.
# 1 hour is sufficient for process on a single chromosome.
# "1-hour", "1-day", "4-day", "7-day", "30-day", "lg-mem"
#$ -q 1-hour
# Priority 0-15.
### -p -10
# Memory per iteration.
# Segmentation errors commonly indicate a memory error.
#$ -l h_vmem=5G
# Concurrent threads; assigns value to variable NSLOTS.
# Important to specify 32 threads to avoid inconsistency with interactive
# calculations.
#$ -pe threaded 32
# Range of indices.
# Specify as argument when calling qsub.
# Array batch indices cannot start at zero.
### -t 1-100:1
# Limit on concurrent processes.
# Allow simultaneous processes for this count of chromosomes.
# For large cohorts (20,000 - 500,000), limit to 10-20 total simultaneous GWAS
# on NCSA.
# Beyond about 10-15 simultaneous GWAS, PLINK2 begins to use more than 2 TB storage.
#$ -tc 10

# http://gridscheduler.sourceforge.net/htmlman/htmlman1/qsub.html

###########################################################################
###########################################################################
###########################################################################
# This script executes GWAS regression across single nucleotide
# polymorphisms (SNPs).
# PLINK2's intermediate files occupy much more data storage space than do
# the final result files.
# If working within a processing directory with only 3 Terabytes of data
# storage, then only attempt to execute about 10 GWAS concurrently across
# a cohort of 30,000-40,000 persons.
###########################################################################
###########################################################################
###########################################################################

################################################################################
# Organize argument variables.

path_table_phenotypes_covariates=${1} # full path to file for table with phenotypes and covariates
path_report=${2} # full path to parent directory for GWAS summary statistics
phenotypes=${3} # names of table's column or columns for single or multiple phenotypes, dependent variables
covariates=${4} # name of table's columns for covariates, independent variables
threads=${5} # count of processing threads to use
maf=${6} # minor allele frequency threshold filter

###########################################################################
# Organize variables.

# Read private, local file paths.
#echo "read private file path variables and organize paths..."
cd ~/paths
path_plink2=$(<"./tools_plink2.txt")
path_ukb_genotype=$(<"./ukbiobank_genotype.txt")

# Organize variables.
# Task identifier starts at one.
index=$SGE_TASK_ID

# Set directory.
path_chromosome="$path_report/chromosome_${index}"
# Determine whether the temporary directory structure already exists.
if [ ! -d $path_chromosome ]; then
    # Directory does not already exist.
    # Create directory.
    mkdir -p $path_chromosome
fi
cd $path_chromosome

# Call PLINK2.
# 90,000 Mebibytes (MiB) is 94.372 Gigabytes (GB)
# --pfilter 1 \
# --pfilter drops SNPs with null p-values and any beyond threshold (such as 1)
# But, maybe pfilter is actually a problem.
$path_plink2 \
--memory 90000 \
--threads $threads \
--bgen $path_ukb_genotype/Chromosome/ukb_imp_chr${index}_v3.bgen \
--sample $path_ukb_genotype/Chromosome/ukb46237_imp_chr${index}_v3_s487320.sample \
--keep $path_table_phenotypes_covariates \
--maf $maf \
--freq --glm hide-covar \
--pheno $path_table_phenotypes_covariates \
--pheno-name $phenotypes \
--covar $path_table_phenotypes_covariates \
--covar-name $covariates \
--out report
