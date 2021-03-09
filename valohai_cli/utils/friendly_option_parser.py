from click import NoSuchOption, OptionParser

from .levenshtein import levenshtein
from click.parser import ParsingState
from typing import Optional


class FriendlyOptionParser(OptionParser):
    """
    A friendlier version of OptionParser that uses Levenshtein distances to figure out
    if the user has just misspelled an option name.
    """

    def _match_long_opt(self, opt: str, explicit_value: Optional[str], state: ParsingState) -> None:
        try:
            super()._match_long_opt(opt, explicit_value, state)  # type: ignore[misc]
        except NoSuchOption as nse:
            if not nse.possibilities:
                # No possibilities were guessed, so attempt some deeper magic
                nse.possibilities = [
                    word
                    for word
                    in self._long_opt
                    if levenshtein(
                        word.lower().lstrip('-'),
                        nse.option_name.lower().lstrip('-'),
                    ) <= 4
                ]
            raise
