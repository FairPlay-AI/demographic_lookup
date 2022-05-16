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

To compute probabilities corresponding to names from the specified input file:

```bash
$ python3 name-lookup.py < tests/invalid_column_test
$ ./name-lookup [input filename]
```

Alternatively, to compute probabilites corresponding to names from standard input:

```
$ ./name-lookup.py < <input file>
```
