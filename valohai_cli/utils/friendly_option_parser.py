from click import OptionParser, NoSuchOption

from .levenshtein import levenshtein


class FriendlyOptionParser(OptionParser):
    """
    A friendlier version of OptionParser that uses Levenshtein distances to figure out
    if the user has just misspelled an option name.
    """
    def _match_long_opt(self, opt, explicit_value, state):
        try:
            return super(FriendlyOptionParser, self)._match_long_opt(opt, explicit_value, state)
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
