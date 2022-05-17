# `demographic_lookup`

## Purpose

This is a very simple code example which estimates the racial
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
usage: name-lookup.py [-h] [-f FIRST_NAME] [-l LAST_NAME] [-d DATE_OF_BIRTH] input_file_name

Look up gender, race, and ethnicity probabilities

positional arguments:
  input_file_name       Input file name ('-' for standard input)

optional arguments:
  -h, --help            show this help message and exit
  -f FIRST_NAME, --first-name FIRST_NAME
                        Name of column containing applicant first names
  -l LAST_NAME, --last-name LAST_NAME
                        Name of column containing applicant last names
  -d DATE_OF_BIRTH, --date-of-birth DATE_OF_BIRTH
                        Name of column containing applicant dates of birth
```