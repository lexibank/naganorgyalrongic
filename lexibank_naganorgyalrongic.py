# encoding: utf-8
from __future__ import unicode_literals, print_function
from collections import OrderedDict, defaultdict

import attr
from clldutils.misc import slug
from clldutils.path import Path
from clldutils.text import split_text, strip_brackets
from pylexibank.dataset import NonSplittingDataset
from pylexibank.dataset import Concept, Language

from tqdm import tqdm

import csv
import lingpy

# Define minimum coverage in order to include a doculect
MIN_COVERAGE = 500

# Define glossing languages not be included
SKIP_LANGS = [
    'Tibetan (Script)',
    'Chinese (Hanzi)',
    'Japanese',
]

class Dataset(NonSplittingDataset):
    id = 'naganorgyalrongic'
    dir = Path(__file__).parent
    concept_class = Concept
    language_class = Language

    def cmd_download(self, **kw):
        # nothing to do, as the raw data is in the repository
        pass

    def cmd_install(self, **kw):
        # Read raw data
        raw_data = self.dir.joinpath('raw', 'YN-RGLD.csv').as_posix()
        wl = lingpy.Wordlist(raw_data)

        # Get the list of doculects with the minimum coverage
        doculects = [
            key for key, value in wl.coverage().items()
            if value >= MIN_COVERAGE and key not in SKIP_LANGS]

        # Collect rows for languoids with the minimum requested coverage
        raw_entries = []
        with open(raw_data) as handler:
            reader = csv.DictReader(handler, delimiter='\t')
            for row in reader:
                # Extract the fields we are interested in
                value = row['reflex']
                gloss = row['gloss']
                if row['gfn']:
                    gloss = "%s (%s)" % (gloss, row['gfn'])
                language = row['language']
                srcid = row['srcid']

                # Skip if no minimum coverage
                if language not in doculects:
                    continue

                # Fix error in STEDT (bad parsing)
                if row['rn'] == '621453':
                    srcid = '1680'

                # add to raw entries
                raw_entries.append({
                    'value' : value,
                    'gloss' : gloss,
                    'language' : language,
                    'srcid' : srcid,
                })

        # add information to the dataset
        with self.cldf as ds:
            # add languages to the dataset
            lang_map = {}
            for language in self.languages:
                ds.add_language(
                    ID=language['SHORT_NAME'],
                    Name=language['NAME'],
                )
                lang_map[language['NAME']] = language['SHORT_NAME']

            # add concepts to the dataset
            for concept in self.concepts:
                ds.add_concept(
                    ID=concept['SRCID'],
                    Name=concept['GLOSS'],
                )

            # add lexemes
            for idx, entry in tqdm(enumerate(raw_entries), desc='make-cldf'):
                # !!! only for developing
                segments = [c for c in entry['value']]
                for row in ds.add_lexemes(
                    Language_ID=lang_map[entry['language']],
                    Parameter_ID=entry['srcid'],
                    Form=entry['value'],
                    Value=entry['value'],
                    Segments=segments,
                    Source=['Nagano2013']):
                    pass
