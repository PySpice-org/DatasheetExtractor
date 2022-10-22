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

####################################################################################################

from ..Math.Statistics import Gaussian
from ..Tools.DictionaryTools import DictInitialised
from .PdfDocument import PdfDocument
from .TextTokenizer import Token, strip_word_list, strip_non_alphabetic

####################################################################################################

class PdfMetaDataExtractor:

    """ This class implements a PDF document Metadata Extractor. """

    address_words = set((
            'avenue',
            'box',
            'division',
            'france',
            'institute',
            'laboratory',
            'rue',
            'university',
            'usa',
            ))

    ##############################################

    def __init__(self, path):

        self._pdf_document = PdfDocument(path)

        self._document_metadata = DocumentMetaData()

        self._document_metadata['number_of_pages'] = self._pdf_document.number_of_pages

        # metadata = pdf_document.metadata
        # for key in sorted(metadata.iterkeys()):
        #     unicode(metadata[key])

        self._first_text_page = self._pdf_document.first_page.text
        self._first_text_blocks = self._first_text_page.blocks

        if bool(self._first_text_blocks):
            self._guess_title()
            self._guess_authors()
        else:
            # First page has not text, could be a scan
            self._title_block = None
            self._authors = []

    ##############################################

    @property
    def title(self):
        if self._title_block is not None:
            return str(self._title_block)
        else:
            return None

    ##############################################

    @property
    def authors(self):
        return self._authors

    ##############################################

    @property
    def number_of_pages(self):
        return self._document_metadata['number_of_pages']

    ##############################################

    @property
    def metadata(self):
        return self._pdf_document.metadata

    ##############################################

    def _first_text_blocks_iterator(self):

        return self._first_text_blocks.sorted_iter()

    ##############################################

    def dump(self):

        print('Number of pages:', self._pdf_document.number_of_pages)
        metadata = self._pdf_document.metadata
        for key in sorted(metadata.keys()):
            print(key + ': ' + str(metadata[key]))

        for text_block in self._first_text_blocks_iterator():

            template = """
        Block %u
          y rank %u
          Interval %s
          Horizontal Margin %s
          Is centred %s
          Is left justifier %g
          Is right justifier %g
          Number of characters %u
          Number of words %u
          main style %s
        """
            print(template[:-1] % (text_block.block_id,
                                   text_block.y_rank,
                                   text_block.interval,
                                   str(text_block.horizontal_margin),
                                   text_block.is_centred,
                                   text_block.is_left_justified,
                                   text_block.is_right_justified,
                                   len(text_block),
                                   text_block.tokenised_text.count_word_number(),
                                   str(text_block.main_style)
                                   ))
            line = '='*100
            print(line)
            print(str(text_block))
            print(line)

    ##############################################

    @staticmethod
    def word_ratio(block):

        token_counter = 0
        word_counter = 0
        for token in block.tokenised_text:
            token_counter += 1
            if token.is_word:
                word_counter += 1

        return word_counter / float(token_counter)

    ##############################################

    def _guess_title(self):

        # Fixme: inference ?

        title_gaussian_style_rank = Gaussian(0, 1)
        title_gaussian_y_rank = Gaussian(0, 3)
        probabilities = TextBlockProbabilities()
        for text_block in self._first_text_blocks_iterator():
            if self.word_ratio(text_block) > .5:
                p0 = title_gaussian_style_rank(text_block.main_style.rank)
                p1 = title_gaussian_y_rank(text_block.y_rank)
                probability = p0*p1
                # print 'Title probability', probability
                probabilities.add_candidate(text_block=text_block, probability=probability)
        probabilities.sort()

        text_block_probability = probabilities.most_probable()
        if text_block_probability is not None:
            self._title_block = text_block_probability.text_block
        else:
            self._title_block = None

    ##############################################

    def _guess_authors(self):

        if self._title_block is None:
            self._authors = []
            return

        probabilities = TextBlockProbabilities()
        for text_block in self._first_text_blocks.sorted_iter():
            author_gaussian_y_rank = Gaussian(self._title_block.y_rank +1, 1)
            author_gaussian_number_of_words = Gaussian(10, 5)
            number_of_words = text_block.tokenised_text.count_word_number()
            p0 = author_gaussian_y_rank(text_block.y_rank)
            p1 = author_gaussian_number_of_words(number_of_words)
            probability = p0*p1
            # print 'Author probability', probability
            probabilities.add_candidate(text_block=text_block, probability=probability)
        probabilities.sort()

        author_block = None
        for text_block_probability in probabilities:
            text_block = text_block_probability.text_block
            if text_block is not self._title_block:
                author_block = text_block
                break
        else:
            author_block = None
        self._author_block = author_block

        if author_block is None:
            self._authors = []
            return

        author_list_words = []
        space_token = Token(Token.Category.space, ' ')
        for i, line in enumerate(author_block.line_iterator()):
            line_words = []
            for word in line.tokenised_text:
                if word.is_word and str(word).lower() in self.address_words:
                    break
                else:
                    # remove super script like: John Doe^1 Doe\dag
                    if word.is_word:
                        word = Token(word.category, strip_non_alphabetic(str(word)))
                    line_words.append(word)
            else:
                if author_list_words:
                    author_list_words.append(space_token)
                author_list_words += line_words

        author_separators = []
        for i, word in enumerate(author_list_words):
            word_string = str(word).lower()
            if (word.is_punctuation and word_string == ',' or
                (word.is_word and word_string == 'and')):
                author_separators.append(i)
        lower_index = 0
        number_of_words = len(author_list_words)
        if (not author_separators or
            (author_separators and author_separators[-1] != number_of_words -1)):
           author_separators.append(number_of_words)
        self._authors = []
        for upper_index in author_separators:
            author_words = author_list_words[lower_index:upper_index]
            author_words = strip_word_list(author_words)
            self._authors.append(author_words)
            lower_index = upper_index +1

####################################################################################################

class TextBlockProbability(DictInitialised):

    """

    Public Attributes:

      :attr:`text_block`

      :attr:`probability`

    """

    __REQUIRED_ATTRIBUTES__ = (
        'text_block',
        'probability',
        )

    ##############################################

    def __lt__(self, other):

        return self.probability < other.probability

####################################################################################################

class TextBlockProbabilities(list):

    ##############################################

    def add_candidate(self, **kwargs):

        text_block_probability = TextBlockProbability(**kwargs)
        self.append(text_block_probability)

    ##############################################

    def sort(self):

        super(TextBlockProbabilities, self).sort(reverse=True)

    ##############################################

    def most_probable(self):

        if self:
            return self[0]
        else:
            return None

####################################################################################################

class DocumentMetaData(dict):
    pass
