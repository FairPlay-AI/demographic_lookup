#!/usr/bin/env python
# coding: utf-8

import datetime
import os
import pathlib
import re
import sys

import numpy as np
import pandas as pd

class GetDemoPercentagesFromNames():
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
                '.',
                'surnames',
                'Names_2010Census.csv'),
            usecols=(
                ['name'] + self.last_name_probability_columns))
        self.last_name_freqs.name = (
            self.last_name_freqs.name.str.lower())
    
        self.first_name_freqs = self.build_gender_table()
        
    def _build_year_gender_table(self, current_path):
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
        
        yf_return.name = yf_return.name.str.lower()
        
        yf_totals = yf_return.pctfemale + yf_return.pctmale
        yf_return.pctfemale = yf_return.pctfemale / yf_totals
        yf_return.pctmale = yf_return.pctmale / yf_totals
        
        yf_return.loc[:, 'yob'] = (
            np.array([year] * yf_return.shape[0]).reshape(-1, 1))
        
        return yf_return
    
    def build_gender_table(self):
        first_name_directory = (
            pathlib.Path('./first_names'))
        first_name_paths = (
            first_name_directory.glob('*.txt'))
        
        by_year_table_list = [
            (self._build_year_gender_table(current_path)
             .reset_index(drop=True))
            for current_path in first_name_paths]
        
        first_name_freqs = pd.concat(
            by_year_table_list, axis='index')
        
        return first_name_freqs
    
    ## The BISG memo specifies this extra name cleap up step
    ## so that the names in the tables match the inputs as
    ## well as possible.
    def _clean_bisg_names(self, name_series):
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
        retval = retval.replace(
            np.NaN, 1 / len(self.last_name_probability_columns))
        
        return retval
    
    def build_first_name_freqs(self, first_names, dobs):
        dob_datetimes = pd.to_datetime(dobs)
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
        retval = retval.replace(np.NaN, 0.5)
        
        return retval
        
def main():
    probability_converter = GetDemoPercentagesFromNames()
    
    first_name_columns = ['applicant_first_name', 'applicant_dob']
    last_name_columns =  ['applicant_last_name']
    
    if len(sys.argv) < 2 or (sys.argv[1] == '-'):
        input_fd = sys.stdin
    else:
        input_fd = open(sys.argv[1])
        
    input_data_iterator = pd.read_csv(
        input_fd,
        chunksize=10000,
        index_col=False,
        dtype=str)
    
    for input_block in input_data_iterator:
        first_name_chunk = input_block[first_name_columns]
        first_name_probs = (
            probability_converter.build_first_name_freqs(
                first_name_chunk.applicant_first_name,
                first_name_chunk.applicant_dob))
        first_name_probs = first_name_probs
        
        last_name_chunk = input_block[last_name_columns]
        last_name_probs = (
            probability_converter.build_last_name_freqs(
                last_name_chunk))
        
        reduced_input_block = input_block[
            np.setdiff1d(
                input_block.columns,
                first_name_columns + last_name_columns)]
        
        output_block = pd.concat([
            reduced_input_block,
            last_name_probs,
            first_name_probs],
            axis='columns')
        
        output_block.to_csv(sys.stdout)
if __name__ == '__main__':
    main()
