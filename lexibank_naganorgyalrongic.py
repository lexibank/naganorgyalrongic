import csv

import lingpy
from clldutils.path import Path
from clldutils.text import split_text
from pylexibank.dataset import Concept, Language
from pylexibank.dataset import NonSplittingDataset
from tqdm import tqdm
import attr

# Define minimum coverage in order to include a doculect
MIN_COVERAGE = 500

# Define glossing languages not be included
SKIP_LANGS = ["Tibetan (Script)", "Chinese (Hanzi)", "Japanese"]

@attr.s
class HLanguage(Language):
    Latitude = attr.ib(default=None)
    Longitude = attr.ib(default=None)
    ChineseName = attr.ib(default=None)
    SubGroup = attr.ib(default='Rgyalrong')
    Family = attr.ib(default='Sino-Tibetan')


class Dataset(NonSplittingDataset):
    id = "naganorgyalrongic"
    dir = Path(__file__).parent
    language_class = HLanguage
    separators = ';,/'
    brackets = {"(": ")", "[": "]"}
    missing_data = ['?']
    strip_inside_brackets = True

    def cmd_download(self, **kw):
        # nothing to do, as the raw data is in the repository
        pass

    def cmd_install(self, **kw):
        # Read raw data
        raw_data = self.dir.joinpath("raw", "YN-RGLD.csv").as_posix()
        wl = lingpy.Wordlist(raw_data)

        # Get the list of doculects with the minimum coverage
        doculects = [
            key
            for key, value in wl.coverage().items()
            if value >= MIN_COVERAGE and key not in SKIP_LANGS
        ]

        # Collect rows for languoids with the minimum requested coverage
        raw_entries = []
        with open(raw_data) as handler:
            reader = csv.DictReader(handler, delimiter="\t")
            for row in reader:
                # Extract the fields we are interested in
                value = row["reflex"]
                gloss = row["gloss"]
                if row["gfn"]:
                    gloss = "%s (%s)" % (gloss, row["gfn"])
                language = row["language"]
                srcid = row["srcid"]

                # Skip if no minimum coverage
                if language not in doculects:
                    continue

                # Fix error in STEDT (bad parsing)
                if row["rn"] == "621453":
                    srcid = "1680"

                # add to raw entries
                raw_entries.append(
                    {"value": value, "gloss": gloss, "language": language, "srcid": srcid}
                )

        # add information to the dataset
        with self.cldf as ds:
            ds.add_sources(*self.raw.read_bib())

            # add languages to the dataset
            lang_map = {}
            for language in self.languages:
                ds.add_language(
                    ID=language["ID"],
                    Name=language["NAME"],
                    Latitude=language['LATITUDE'],
                    Longitude=language['LONGITUDE'],
                    Glottocode=language["GLOTTOCODE"],
                )
                lang_map[language["NAME"]] = language["ID"]

            # add concepts to the dataset
            for concept in self.concepts:
                ds.add_concept(
                    ID=concept["SRCID"],
                    Name=concept["GLOSS"],
                    Concepticon_ID=concept["CONCEPTICON_ID"],
                    Concepticon_Gloss=concept["CONCEPTICON_GLOSS"],
                )

            # add lexemes
            for idx, entry in tqdm(enumerate(raw_entries), desc="make-cldf"):
                forms = ds.add_forms_from_value(
                        Language_ID=lang_map[entry["language"]],
                        Parameter_ID=entry["srcid"],
                        Value=entry["value"],
                        Source=["Nagano2013"]
                        )
