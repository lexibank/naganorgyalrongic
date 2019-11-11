from pathlib import Path

from pylexibank.dataset import Dataset as BaseDataset
from pylexibank import Concept, Language
from pylexibank import FormSpec
from pylexibank.util import progressbar

from clldutils.misc import slug

import lingpy
import attr

# Define minimum coverage in order to include a doculect
MIN_COVERAGE = 500

# Define glossing languages not be included
SKIP_LANGS = ["Tibetan (Script)", "Chinese (Hanzi)", "Japanese"]


@attr.s
class CustomConcept(Concept):
    SrcId = attr.ib(default=None)
    Number = attr.ib(default=None)


@attr.s
class CustomLanguage(Language):
    Latitude = attr.ib(default=None)
    Longitude = attr.ib(default=None)
    SubGroup = attr.ib(default="Rgyalrong")
    Family = attr.ib(default="Sino-Tibetan")
    Source_ID = attr.ib(default=None)
    Short_Name = attr.ib(default=None)


class Dataset(BaseDataset):
    id = "naganorgyalrongic"
    dir = Path(__file__).parent
    language_class = CustomLanguage
    concept_class = CustomConcept
    form_spec = FormSpec(
        separators=";,/",
        brackets={"(": ")", "[": "]"},
        missing_data=("?",),
        strip_inside_brackets=True,
        first_form_only=True
    )

    def cmd_makecldf(self, args):
        # Read raw data
        wl = lingpy.Wordlist(self.raw_dir.joinpath("YN-RGLD.csv").as_posix())

        args.writer.add_sources()
        concept_lookup = args.writer.add_concepts(
            id_factory=lambda x: x.id.split("-")[-1] + "_" + slug(x.english), lookup_factory="SrcId"
        )
        language_lookup = args.writer.add_languages(lookup_factory="Name")
        # add lexemes
        for idx, language, concept, value in progressbar(
            wl.iter_rows("doculect", "srcid", "reflex"), desc="make-cldf"
        ):
            if language in language_lookup and concept in concept_lookup:
                args.writer.add_forms_from_value(
                    Language_ID=language_lookup[language],
                    Parameter_ID=concept_lookup[concept],
                    Value=value,
                    Source=["Nagano2013"],
                )
