import os

import numpy as np
import pandas as pd

class NameChooser:
    def _pick_single_names(self, frequency_table, sample):
        random_item = (
            (frequency_table.probs > sample).idxmax())
        
        return frequency_table.name
    
    def _pick_names(self,
                    name_type,
                    frequency_table_base, 
                    count,
                    rng):
        frequency_table = frequency_table_base[
            frequency_table_base.name_type == name_type]
        
        frequency_table.probs = (
            frequency_table.name_count /
            frequency_table.name_count.sum())
        
        samples = rng.uniform(size=count)
        
        return [
            self._pick_single_name(frequency_table, sample)
            for sample in samples]
    
    def random_first_names(self, gender, yob, count, rng):
        base_names = pd.read_csv(
            os.path.join(
                'first_names',
                'yob{0:04d}.txt'.format(yob)),
            head=False)
        
        base_names.columns = [
            'name', 'type', 'name_count']
        
        name_type = (
            'M' if gender == 'pctmale' else 'F')
        
        return self._pick_names(
            name_type, base_names, count, rng)
    
    def crandom_last_names(self, race, count, rng):
        base_names = pd.read_csv(