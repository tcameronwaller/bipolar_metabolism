
"""
...

"""

###############################################################################
# Notes

###############################################################################
# Installation and importation

# Standard

import sys
#print(sys.path)
import os
import math
import statistics
import pickle
import copy
import random
import itertools
import time

# Relevant

import numpy
import scipy.stats
import pandas
pandas.options.mode.chained_assignment = None # default = "warn"

# Custom
import promiscuity.utility as utility
import promiscuity.plot as plot
import uk_biobank.assembly
import uk_biobank.organization as ukb_organization

###############################################################################
# Functionality


##########
# Initialization

# TODO: temporarily routed to "organization_test" to avoid disruption to genetic analyses in progress
def initialize_directories(
    restore=None,
    path_dock=None,
):
    """
    Initialize directories for procedure's product files.

    arguments:
        restore (bool): whether to remove previous versions of data
        path_dock (str): path to dock directory for source and product
            directories and files

    raises:

    returns:
        (dict<str>): collection of paths to directories for procedure's files

    """

    # Collect paths.
    paths = dict()
    # Define paths to directories.
    paths["dock"] = path_dock
    paths["organization"] = os.path.join(paths["dock"], "organization_test")
    paths["export"] = os.path.join(
        paths["organization"], "export"
    )
    paths["cohorts_models"] = os.path.join(
        paths["organization"], "cohorts_models"
    )
    # Remove previous files to avoid version or batch confusion.
    if restore:
        utility.remove_directory(path=paths["organization"])
    # Initialize directories.
    utility.create_directories(
        path=paths["organization"]
    )
    utility.create_directories(
        path=paths["export"]
    )
    utility.create_directories(
        path=paths["cohorts_models"]
    )
    # Return information.
    return paths


##########
# Read


def read_source(
    path_dock=None,
    report=None,
):
    """
    Reads and organizes source information from file.

    Notice that Pandas does not accommodate missing values within series of
    integer variable types.

    arguments:
        path_dock (str): path to dock directory for source and product
            directories and files
        report (bool): whether to print reports

    raises:

    returns:
        (object): source information

    """

    # Specify directories and files.
    path_table_phenotypes = os.path.join(
        path_dock, "assembly", "table_phenotypes.pickle"
    )
    # Read information from file.
    table_phenotypes = pandas.read_pickle(
        path_table_phenotypes
    )

    # Metabolites.
    if False:
        path_table_metabolites_names = os.path.join(
            path_dock, "access", "24816252_shin_2014", "metaboliteMap.txt"
        )
        path_table_metabolites_scores = os.path.join(
            path_dock, "aggregation", "selection",
            "table_metabolites_scores_prs_0_0001.pickle"
        )
        table_metabolites_names = pandas.read_csv(
            path_table_metabolites_names,
            sep="\t",
            header=0,
            dtype="string",
        )
        table_metabolites_scores = pandas.read_pickle(
            path_table_metabolites_scores
        )
    # Compile and return information.
    return {
        "table_phenotypes": table_phenotypes,
        #"table_metabolites_names": table_metabolites_names,
        #"table_metabolites_scores": table_metabolites_scores,
    }


##########
# Metabolites


def determine_metabolite_valid_identity(
    name=None,
):
    """
    Determine whether a single metabolite has a valid identity from Metabolon.

    arguments:
        name (str): name of metabolite from Metabolon reference

    raises:

    returns:
        (float): ordinal representation of person's frequency of alcohol
            consumption

    """

    # Determine whether the variable has a valid (non-missing) value.
    if (len(str(name)) > 2):
        # The variable has a valid value.
        if (str(name).strip().lower().startswith("x-")):
            # Metabolite has an indefinite identity.
            identity = 0
        else:
            # Metabolite has a definite identity.
            identity = 1
    else:
        # Name is empty.
        #identity = float("nan")
        identity = 0
    # Return information.
    return identity


def select_organize_metabolites_valid_identities_scores(
    table_names=None,
    table_scores=None,
    report=None,
):
    """
    Selects identifiers of metabolites from Metabolon with valid identities.

    arguments:
        table_names (object): Pandas data frame of metabolites' identifiers and
            names from Metabolon
        table_scores (object): Pandas data frame of metabolites' genetic scores
            across UK Biobank cohort
        report (bool): whether to print reports

    raises:

    returns:
        (dict): collection of information about metabolites, their identifiers,
            and their names

    """

    # Copy information.
    table_names = table_names.copy(deep=True)
    table_scores = table_scores.copy(deep=True)
    # Translate column names.
    translations = dict()
    translations["metabolonID"] = "identifier"
    translations["metabolonDescription"] = "name"
    table_names.rename(
        columns=translations,
        inplace=True,
    )
    # Determine whether metabolite has a valid identity.
    table_names["identity"] = table_names.apply(
        lambda row:
            determine_metabolite_valid_identity(
                name=row["name"],
            ),
        axis="columns", # apply across rows
    )
    # Select metabolites with valid identities.
    table_identity = table_names.loc[
        (table_names["identity"] > 0.5), :
    ]
    metabolites_identity = table_identity["identifier"].to_list()
    names_identity = table_identity["name"].to_list()
    # Organize table.
    table_names["identifier"].astype("string")
    table_names.set_index(
        "identifier",
        drop=True,
        inplace=True,
    )
    # Remove table columns for metabolites with null genetic scores.
    table_scores.dropna(
        axis="columns",
        how="all",
        subset=None,
        inplace=True,
    )
    # Select metabolites with valid identities and valid genetic scores.
    metabolites_scores = table_scores.columns.to_list()
    metabolites_valid = utility.filter_common_elements(
        list_minor=metabolites_identity,
        list_major=metabolites_scores,
    )
    # Compile information.
    pail = dict()
    pail["table"] = table_names
    pail["metabolites_valid"] = metabolites_valid
    # Report.
    if report:
        # Column name translations.
        utility.print_terminal_partition(level=2)
        print("Report from select_metabolites_with_valid_identities()")
        utility.print_terminal_partition(level=3)
        print(
            "Count of identifiable metabolites: " +
            str(len(metabolites_identity))
        )
        print(
            "Count of identifiable metabolites with scores: " +
            str(len(metabolites_valid))
        )
        utility.print_terminal_partition(level=3)
        print(table_names)
    # Return information.
    return pail


##########
# Write


def write_product_export_table(
    name=None,
    information=None,
    path_parent=None,
):
    """
    Writes product information to file.

    arguments:
        name (str): base name for file
        information (object): information to write to file
        path_parent (str): path to parent directory

    raises:

    returns:

    """

    # Specify directories and files.
    path_table = os.path.join(
        path_parent, str(name + ".tsv")
    )
    # Write information to file.
    information.to_csv(
        path_or_buf=path_table,
        sep="\t",
        header=True,
        index=True,
    )
    pass


def write_product_export(
    information=None,
    path_parent=None,
):
    """
    Writes product information to file.

    arguments:
        information (object): information to write to file
        path_parent (str): path to parent directory

    raises:

    returns:

    """

    for name in information.keys():
        write_product_export_table(
            name=name,
            information=information[name],
            path_parent=path_parent,
        )
    pass


def write_product_cohort_model_table(
    name=None,
    information=None,
    path_parent=None,
):
    """
    Writes product information to file.

    arguments:
        name (str): base name for file
        information (object): information to write to file
        path_parent (str): path to parent directory

    raises:

    returns:

    """

    # Specify directories and files.
    path_table = os.path.join(
        path_parent, str(name + ".tsv")
    )
    # Write information to file.
    information.to_csv(
        path_or_buf=path_table,
        sep="\t",
        header=True,
        index=False,
    )
    pass


def write_product_cohorts_models(
    information=None,
    path_parent=None,
):
    """
    Writes product information to file.

    arguments:
        information (object): information to write to file
        path_parent (str): path to parent directory

    raises:

    returns:

    """

    for name in information.keys():
        write_product_cohort_model_table(
            name=name,
            information=information[name],
            path_parent=path_parent,
        )
    pass


def write_product(
    information=None,
    paths=None,
):
    """
    Writes product information to file.

    arguments:
        information (object): information to write to file
        paths (dict<str>): collection of paths to directories for procedure's
            files

    raises:

    returns:

    """

    # Export information.
    write_product_export(
        information=information["export"],
        path_parent=paths["export"],
    )
    # Cohort tables in PLINK format.
    if True:
        write_product_cohorts_models(
            information=information["cohorts_models"],
            path_parent=paths["cohorts_models"],
        )
    pass


def write_product_metabolites_former(
    information=None,
    paths=None,
):
    """
    Writes product information to file.

    arguments:
        information (object): information to write to file
        paths (dict<str>): collection of paths to directories for procedure's
            files

    returns:

    """

    # Specify directories and files.

    path_table_metabolites_names = os.path.join(
        paths["organization"], "table_metabolites_names.pickle"
    )
    path_table_metabolites_names_text = os.path.join(
        paths["organization"], "table_metabolites_names.tsv"
    )
    path_metabolites_valid = os.path.join(
        paths["organization"], "metabolites_valid.pickle"
    )
    path_table_phenotypes = os.path.join(
        paths["organization"], "table_phenotypes.pickle"
    )
    path_table_phenotypes_text = os.path.join(
        paths["organization"], "table_phenotypes.tsv"
    )

    # Write information to file.
    information["table_metabolites_names"].to_pickle(
        path_table_metabolites_names
    )
    information["table_metabolites_names"].to_csv(
        path_or_buf=path_table_metabolites_names_text,
        sep="\t",
        header=True,
        index=True,
    )
    with open(path_metabolites_valid, "wb") as file_product:
        pickle.dump(information["metabolites_valid"], file_product)
    information["table_phenotypes"].to_pickle(
        path_table_phenotypes
    )
    information["table_phenotypes"].to_csv(
        path_or_buf=path_table_phenotypes_text,
        sep="\t",
        header=True,
        index=True,
    )
    pass



###############################################################################
# Procedure


def execute_procedure(
    path_dock=None,
):
    """
    Function to execute module's main behavior.

    arguments:
        path_dock (str): path to dock directory for source and product
            directories and files

    raises:

    returns:

    """

    utility.print_terminal_partition(level=1)
    print(path_dock)
    print("version check: 5")
    # Pause procedure.
    time.sleep(5.0)

    # Initialize directories.
    paths = initialize_directories(
        restore=True,
        path_dock=path_dock,
    )
    # Read source information from file.
    # Exclusion identifiers are "eid".
    source = read_source(
        path_dock=path_dock,
        report=True,
    )

    # Organize variables for persons' genotypes, sex, age, and body mass index
    # across the UK Biobank.
    pail_basis = ukb_organization.execute_genotype_sex_age_body(
        table=source["table_phenotypes"],
        report=True,
    )
    # Organize variables for persons' sex hormones across the UK Biobank.
    pail_hormone = ukb_organization.execute_sex_hormones(
        table=pail_basis["table"], # pail_basis["table_clean"]
        report=False,
    )
    # Organize variables for female menstruation across the UK Biobank.
    pail_female = ukb_organization.execute_female_menstruation(
        table=pail_hormone["table"], # pail_hormone["table_clean"]
        report=False,
    )
    # Organize variables for persons' mental health across the UK Biobank.
    pail_psychology = ukb_organization.execute_psychology_psychiatry(
        table=pail_female["table"],
        report=True,
    )
    #print(pail_psychology["table_clean"].columns.to_list())

    # Describe variables within cohorts and models.
    if True:
        pail_summary = (
            ukb_organization.execute_describe_cohorts_models_phenotypes(
                table=pail_psychology["table"],
                set="bipolar_disorder_body",
                path_dock=path_dock,
                report=True,
        ))


    # Select and organize variables across cohorts.
    # Organize phenotypes and covariates in format for analysis in PLINK.
    if True:
        pail_cohorts_models = (
            ukb_organization.execute_cohorts_models_genetic_analysis(
                table=pail_psychology["table_clean"],
                set="bipolar_disorder_body",
                path_dock=path_dock,
                report=True,
        ))
    else:
        pail_cohorts_models = dict()


    # Collect information.
    information = dict()
    information["export"] = dict()
    information["export"]["table_summary_cohorts_models_phenotypes"] = (
        pail_summary["table_summary_cohorts_models_phenotypes"]
    )
    information["export"]["table_summary_cohorts_models_genotypes"] = (
        pail_summary["table_summary_cohorts_models_genotypes"]
    )
    information["cohorts_models"] = pail_cohorts_models
    # Write product information to file.
    write_product(
        paths=paths,
        information=information
    )
    pass


if (__name__ == "__main__"):
    execute_procedure()
