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

class Dataset(NonSplittingDataset):
    id = 'naganorgyalrongic'
    dir = Path(__file__).parent
    concept_class = Concept
    language_class = Language

    def cmd_download(self, **kw):
        # nothing to do, as the raw data is in the repository
        pass

    def cmd_install(self, **kw):
        print("should install")
        pass

