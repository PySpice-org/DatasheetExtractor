####################################################################################################
#
# Babel - An Electronic Document Management System
# Copyright (C) 2014 Fabrice Salvaire
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
####################################################################################################

"""
"""

# word: [a-zA-z\-]+[0-9]*
#   - could be cesure or hyphenation
#   . as in "e.g." "fig."
#
# number:
#   integer: [0-9]+
#     thousand separator "123 456"
#   float: [0-9]+.[0-9]+
#     ".1" "0.2"
#     French convention "1,2"
#
# punctuation:
#   terminal: . ? !
#   speparator: , ; :
#
# group: ()

####################################################################################################

import unicodedata

####################################################################################################

from Babel.backend.Tools.EnumFactory import EnumFactory

####################################################################################################

class Token:

    Category = EnumFactory('TokenCategory', ('word',
                                             'number',
                                             'punctuation',
                                             'space',
                                             'symbol',
                                             ))

    ##############################################

    def __init__(self, category, text):

        self._category = category
        self._text = str(text)

    ##############################################

    @property
    def category(self):
        return self._category

    ##############################################

    @property
    def is_word(self) :
        return self._category == Token.Category.word

    ##############################################

    @property
    def is_number(self) :
        return self._category == Token.Category.number

    ##############################################

    @property
    def is_punctuation(self) :
        return self._category == Token.Category.punctuation

    ##############################################

    @property
    def is_space(self) :
        return self._category == Token.Category.space

    ##############################################

    @property
    def is_symbol(self) :
        return self._category == Token.Category.symbol

    ##############################################

    def __str__(self):

        return self._text

    ##############################################

    def __len__(self):

        return len(self._text)

    ##############################################

    def __repr__(self):

        return 'Token %s:"%s"' % (str(self._category), self._text)

####################################################################################################

class TokenisedText(list):

    ##############################################

    def word_iterator(self):

        """ Iterate over words. """

        for token in self:
            if token.category == Token.Category.word:
                yield token

    ##############################################

    def word_number_iterator(self):

        """ Iterate over word and number. """

        for token in self:
            if token.category in (Token.Category.word, Token.Category.number):
                yield token

    ##############################################

    def count_word_number(self):

        """ Count the number of words and numbers. """

        # Fixme: iterator doesn't have len method
        counter = 0
        for token in self.word_number_iterator():
            counter += 1

        return counter

####################################################################################################

class TextTokenizer:

    State = EnumFactory('LexerState', ('letter',
                                       'number',
                                       'special',
                                       ))

    ##############################################

    def lex(self, text):

        state = None
        word = ''
        tokenised_text = TokenisedText()

        def initial_transition(category, char):
            if category in ('Ll', 'Lu'):
                state = TextTokenizer.State.letter
                word = char
            elif category == 'Nd':
                state = TextTokenizer.State.number
                word = char
            else:
                if category == 'Zs':
                    token_category = Token.Category.space
                elif category in ('Po', 'Pd'):
                    token_category = Token.Category.punctuation
                # Ps Pe e.g. ()
                else:
                    token_category = Token.Category.symbol
                tokenised_text.append(Token(token_category, char))
                state = None
                word = ''
            return state, word

        for char in text:
            category = unicodedata.category(char)
            # print '>', char, category, state, word
            if state is None:
                state, word = initial_transition(category, char)
            else:
                if state == TextTokenizer.State.letter:
                    if category in ('Ll', 'Lu', 'Nd'):
                        word += char
                    else:
                        tokenised_text.append(Token(Token.Category.word, word))
                        state, word = initial_transition(category, char)
                elif state == TextTokenizer.State.number:
                    if category == 'Nd':
                        word += char
                    else:
                        tokenised_text.append(Token(Token.Category.number, word))
                        state, word = initial_transition(category, char)
        if word:
            if state == TextTokenizer.State.letter:
                tokenised_text.append(Token(Token.Category.word, word))
            elif state == TextTokenizer.State.number:
                tokenised_text.append(Token(Token.Category.number, word))

        return tokenised_text

####################################################################################################

def strip_word_list(word_list):

    """ Return a word list where the leading and trailing spaces was removed. """

    upper_index_max = len(word_list) -1
    if upper_index_max < 0:
        return ''

    lower_index = 0
    while True:
        if word_list[lower_index].is_space:
            lower_index += 1
        else:
            break
        if lower_index > upper_index_max:
            return []
    upper_index = len(word_list) -1
    while True:
        if word_list[upper_index].is_space:
            upper_index -= 1
        else:
            break

    return word_list[lower_index:upper_index +1]

####################################################################################################

def join_tokens(tokens):
    return ''.join([str(token) for token in tokens])

####################################################################################################

def strip_non_alphabetic(text):

    upper_index = len(text) -1
    while True:
        char = text[upper_index]
        category = unicodedata.category(char)
        if category not in ('Ll', 'Lu'):
            upper_index -= 1
        else:
            break
        if upper_index < 0:
            return ''

    return text[0:upper_index +1]
