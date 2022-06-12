import os

import numpy as np
import pandas as pd

class RandomNameChooser:
    def __init__(self):
        last_names_base = pd.read_csv(
            os.path.join(
                os.getcwd(),
                'surnames',
                'Names_2010Census.csv'))
        
        self.last_names = (
            last_names_base[last_names_base['name'] != 
                            'ALL OTHER NAMES'])

    def _pick_single_names(self, frequency_table, sample):
        random_item = (
            (frequency_table.probs.cumsum() > sample).idxmax())
        
        return frequency_table.name[random_item]
    
    def _pick_names(self,
                    frequency_table_base, 
                    count,
                    rng):
        frequency_table = pd.DataFrame({
            'name' : frequency_table_base['names'],
            'probs' : (
                frequency_table_base.name_count /
                frequency_table_base.name_count.sum())})
        
        samples = rng.uniform(size=count)
        
        return [
            self._pick_single_names(frequency_table, sample)
            for sample in samples]
    
    def random_first_names(self, gender, yob, count, rng):
        base_names = pd.read_csv(
            os.path.join(
                '.',
                'first_names',
                'yob{0:04d}.txt'.format(yob)),
            header=None)
        
        base_names.columns = [
            'names', 'type', 'name_count']
        
        name_type = (
            'M' if gender == 'pctmale' else 'F')
        
        return self._pick_names(
            base_names[base_names['type'] == name_type],
            count, 
            rng)
    
    def random_last_names(self, race, count, rng):
        chosen_columns = pd.DataFrame({
            'names' : self.last_names['name'],
            'name_count' : (
                self.last_names['count'] * 
                (self.last_names[race]
                 .replace('(S)', 0)
                 .astype(float)))})
        
        return self._pick_names(chosen_columns, count, rng)
