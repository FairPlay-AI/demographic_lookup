# `demographic_lookup`

## Purpose

This code example estimates the racial
and ethnic probabilities associated with surnames and gender
probabilities associated with first names.

It is typically used as part of the CFPB implementation of
Bayesian Improved Surname Geocoding (BISG) for racial and ethnic
classification or its parallel for gender imputation.

## Installation

```shell
$ pip install -r requirements.txt
```

## Usage

```bash
usage: name-lookup.py [-h] [-f FIRST_NAME] [-l LAST_NAME] [-d DATE_OF_BIRTH]
                      input_file_name output_file_name

Look up gender, race, and ethnicity probabilities

positional arguments:
  input_file_name       Input file name ('-' for standard input)
  output_file_name      Output file name ('-' for standard output)

optional arguments:
  -h, --help            show this help message and exit
  -f FIRST_NAME, --first-name FIRST_NAME
                        Name of column containing applicant first names
  -l LAST_NAME, --last-name LAST_NAME
                        Name of column containing applicant last names
  -d DATE_OF_BIRTH, --date-of-birth DATE_OF_BIRTH
                        Name of column containing applicant dates of birth
```

For example, running 

```bash
./name_lookup tests/valid tests/valid_results
```

should create a file in the `tests` directory which is identical to `tests/valid_results_expected`

And running

```bask
./name_lookup -d applicant_do1b tests/alternate_column_test tests/alternate_column_results
```

should create a file in the `tests` directory which is identical to `tests/alternate_column_results_expected`
