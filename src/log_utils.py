from datetime import datetime
import os
from dataclasses import is_dataclass
import string
import random

oj = os.path.join

strip_characters = ['a', 'e', 'i', 'o', 'u', 'A', 'E', 'I', 'O', 'U']
characters = [str(i) for i in range(10)]
characters.extend(list(string.ascii_lowercase))

def format_value_or_key(value):
    if isinstance(value, float):
        # takes 2 significant figures automatically
        return f'{value:.2g}'  
    elif isinstance(value, str):
        # removes '_', vowels (unless first), repeat letters, and capitalises first character
        value = value.replace('_', '')
        value = ''.join([x for i, x in enumerate(value) if (x not in strip_characters) or (i == 0)])
        value = ''.join(sorted(set(value), key=value.index))
        return value.capitalize()
    elif isinstance(value, int):
        # limit length of ints to 4
        return str(value)[:4]
    else:
        return str(value)

def generate_alphnum(length=4):
    # generate an n character string composed of alphanumeric characters
    alphnum = ''.join([random.choice(characters) for _ in range(length)])
    return alphnum

def create_filename(cfg, hyperparams=None):
    """
    helper for creating filenames in a consistent way from a config
    """

    date_time_alphnum = datetime.now().strftime("%d%b%H%M") + generate_alphnum()

    if is_dataclass(cfg):
        cfg = cfg.asdict()

    if hyperparams is None:
        hyperparams = cfg.keys()
        
    sorted_keys = sorted(hyperparams)
    '''
    formats the values 
    formats the keys
    adds _ between hyperparams
    '''
    hyperparams_name = '_'.join([f'{format_value_or_key(k)}{format_value_or_key(cfg[k])}' for k in sorted_keys])

    name = date_time_alphnum + '_' + hyperparams_name

    return name


if __name__ == '__main__':
    cfg = {
        'lr': 0.001,
        'ex_int': 3,
        'ex_str': 'leaky_relu'
    }

    hyperparams = None
    filename = create_filename(cfg, hyperparams=hyperparams)

    print(filename)
    

