#!/usr/bin/env python3
# coding: utf-8

import argparse
import datetime
import os
import pathlib
import re
import sys

import numpy as np
import pandas as pd


class GetDemoPercentagesFromNames():
    """Gets imputed probabilities from applicant names"""

    last_name_probability_columns = [
        'pctwhite',
        'pctblack',
        'pctapi',
        'pctaian',
        'pct2prace',
        'pcthispanic']

    def __init__(self):
        self.last_name_freqs = pd.read_csv(
            os.path.join(
                os.getcwd(),
                'surnames',
                'Names_2010Census.csv'),
            usecols=(
                ['name'] + self.last_name_probability_columns))
        self.last_name_freqs.name = (
            self.last_name_freqs.name.str.lower())
    
        self.first_name_freqs = self.build_gender_table()
        
    def _build_year_gender_table(self, current_path):
        """Build the gender ratio table for a single year.

        The SSA name database is broken up by year. This is
        essential, since names have different gender breakdowns
        at different times (e.g. Taylor is overwhelmingly male 
        for children born in 1960, but predominantly female
        for children born 1990.
        
        Params:
            current_path (str): the path to the current first name year
                                file (e.g. yob1880.txt)
        """

        year = (
            int(re.sub('yob([0-9]*).txt',
                       '\g<1>',
                       current_path.name)))
        
        year_frame = pd.read_csv(current_path, header=None)
        yf_f = year_frame[year_frame[1] == 'F']
        yf_m = year_frame[year_frame[1] == 'M']
        
        yf_f = yf_f.reset_index(drop=True)
        yf_m = yf_m.reset_index(drop=True)
        
        yf_merged = yf_f.merge(yf_m, on=0, how='outer')
        yf_merged.replace(np.NaN, 0.0, inplace=True)
        
        yf_return = yf_merged[[0, '2_x', '2_y']]
        yf_return.columns = ['name', 'pctfemale', 'pctmale']
        
        yf_totals = yf_return.pctfemale + yf_return.pctmale
        
        retval = pd.DataFrame({
            'name' : yf_return.name.str.lower(),
            'pctfemale' : yf_return.pctfemale / yf_totals,
            'pctmale' : yf_return.pctmale / yf_totals,
            'yob' : [year] * yf_return.shape[0]})
        
        return retval
    
    def build_gender_table(self):
        """Collect and join the fist name tables across all years"""
        first_name_directory = (
            pathlib.Path(os.path.join(os.getcwd(), 'first_names')))
        first_name_paths = (
            first_name_directory.glob('*.txt'))
        
        by_year_table_list = [
            (self._build_year_gender_table(current_path)
             .reset_index(drop=True))
            for current_path in first_name_paths]
        
        first_name_freqs = pd.concat(
            by_year_table_list, axis='index')
        
        return first_name_freqs
    
    def _clean_bisg_names(self, name_series):
        """Apply the CFPB name-cleaning algorithm to input names.

        'Real' names are complicated and inconsistent,
        which means that many of them should match a name
        in the database won't unless they're cleaned up.
        The CFPB 2014 BISG report specifies a particular
        cleaning procedure, which, while far from perfect
        if significantly better than nothing. This function
        implements that process.
        
        Params:
             name_series [str]: the union set of last or first names considered in the 
                                BISG imputation method
        """

        special_character_re = re.compile('[\`\{}\\,.0-9]')
        apostrophe_replace_re = re.compile("[']")
        double_quote_replace_re = re.compile('\"')
        suffix_replace_re = (
            re.compile(' +(jr|sr|ii|iii|iv|dds|md|phd)'))
        isolated_initials_re = (
            re.compile(" +[a-ce-np-z] +"))
        lone_o_d_re = re.compile(' +[od] +')

        ns_temp = (
            name_series.str.lower().
            str.replace(apostrophe_replace_re, '').
            str.replace(double_quote_replace_re, ' ').
            str.replace(suffix_replace_re, ' ').
            str.replace(isolated_initials_re, '').
            str.replace(lone_o_d_re, '').
            str.replace(' ', ''))

        return ns_temp

    def build_last_name_freqs(self, last_names):
        """Compute the race and ethnicity probabilities

        Given the list of last names in last_names, clean the
        names and then look up the probabilities for those last names.
        In the cases where a last name can't be found, substitute
        eqaul probabilities so that the resulting imputed probabilities
        will simply reflect the underlying census tract.
        
        Params:
            last_names [str]: all the last names to consider as part 
                              of imputation method.  case-insensitive.
        """

        transformed_last_names = pd.DataFrame(
            { 'surname' : self._clean_bisg_names(last_names.iloc[:, 0])})
        
        retval = transformed_last_names.merge(
            self.last_name_freqs,
            left_on='surname', 
            right_on='name',
            how='left')
        retval.drop(['surname', 'name'],
                    axis='columns',
                    inplace=True)
        retval = retval.replace(np.NaN, 1)
        
        return retval
    
    def build_first_name_freqs(self, first_names, dobs):
        """Compute the gender probability estimates

        Unlike the last name case, the first name case has
        two input terms: the name and the date of birth of
        the applicant, because the SSA database is structured by
        year.
        
        Params:
        
            first_names [str]: all the first names to consider as part 
                               of imputation method.  case-insensitive.
        """

        dob_datetimes = pd.to_datetime(dobs, errors='coerce')
        dob_datetimes[dob_datetimes.isnull()] = (
            datetime.datetime.fromisoformat('1990-01-01'))
        yobs = [
            int(dob_datetime.year)
            for dob_datetime in dob_datetimes]
        
        transformed_first_names = pd.DataFrame(
            {
                'first_name' : self._clean_bisg_names(first_names),
                'yob' : yobs})
        
        retval = (
            transformed_first_names.merge(
                self.first_name_freqs,
                left_on=['first_name', 'yob'],
                right_on=['name', 'yob'],
                how='left'))
        retval.drop(['first_name', 'name', 'yob'],
                    axis='columns',
                    inplace=True)
        retval = retval.replace(np.NaN, 1)
        
        return retval
        
def main():
    """main method"""

    ##
    command_line_parser = (
        argparse.ArgumentParser(
            description=(
                'Look up gender, race, and ethnicity probabilities')))
    
    command_line_parser.add_argument(
        '-f', '--first-name',
        dest='first_name',
        type=str,
        default='applicant_first_name',
        help='Name of column containing applicant first names')
    command_line_parser.add_argument(
        '-l', '--last-name',
        dest='last_name',
        type=str,
        default='applicant_last_name',
        help='Name of column containing applicant last names')
    command_line_parser.add_argument(
        '-d', '--date-of-birth',
        dest='date_of_birth',
        type=str,
        default='applicant_dob',
        help='Name of column containing applicant dates of birth')
    command_line_parser.add_argument(
        '-b', '--bad-input-filename',
        dest='bad_input_filename',
        type=str,
        default=None,
        help='Output filename for bad input samples')
    command_line_parser.add_argument(
        'input_file_name',
        type=str,
        help='Input file name (\'-\' for standard input)')
    command_line_parser.add_argument(
        'output_file_name',
        type=str,
        help='Output file name (\'-\' for standard output)')
    
    args = command_line_parser.parse_args()
    
    ##
    probability_converter = GetDemoPercentagesFromNames()
    first_name_column =  args.first_name
    last_name_column =  args.last_name
    first_name_columns = [first_name_column, args.date_of_birth]
    last_name_columns =  [last_name_column]
    
    if args.input_file_name == '-':
        input_fd = sys.stdin
    else:
        input_fd = open(args.input_file_name)
        
    input_data_iterator = pd.read_csv(
        input_fd,
        chunksize=10000,
        index_col=False,
        dtype=str)
    
    if args.output_file_name == '-':
        output_fd = sys.stdout
    else:
        output_fd = open(args.output_file_name, 'w', newline='')

    if args.bad_input_filename is not None:
         bad_input_fd = open(args.bad_input_filename, 'w')
    else:
         bad_input_fd = None

    header_block = True
    
    for input_block in input_data_iterator:
        # collect bad inputs with missing first or last name
        bad_input_block = input_block[
             input_block[first_name_column].isna()
           | input_block[last_name_column].isna()
        ]

        # trim inputs missing first or last name from input block
        input_block = input_block[
             input_block[first_name_column].notna()
           & input_block[last_name_column].notna()
        ]

        first_name_chunk = input_block[first_name_columns]
        first_name_probs = (
            probability_converter.build_first_name_freqs(
                first_name_chunk[args.first_name],
                first_name_chunk[args.date_of_birth]))
        first_name_probs = first_name_probs
        
        last_name_chunk = input_block[last_name_columns]
        last_name_probs = (
            probability_converter.build_last_name_freqs(
                last_name_chunk))
        
        reduced_input_block = input_block[
            np.setdiff1d(
                input_block.columns,
                [args.first_name, args.last_name])]
        
        output_block = pd.concat([
            reduced_input_block.reset_index(drop=True),
            last_name_probs.reset_index(drop=True),
            first_name_probs.reset_index(drop=True)],
            axis='columns')
        
        output_block.to_csv(
            output_fd,
            header=header_block,
            mode='w',
            index=False)

        # if bad output file is enabled, write bad inputs to bad output file
        if args.bad_input_filename:
            bad_input_block.to_csv(
                bad_input_fd,
                header=header_block,
                mode='w',
                index=False)
        header_block = False

if __name__ == '__main__':
    main()
