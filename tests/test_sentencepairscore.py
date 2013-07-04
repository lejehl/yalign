#!/usr/bin/env python
# coding: utf-8

import os
import unittest

from yalign.datatypes import Sentence
from yalign.wordpairscore import WordPairScore
from yalign.sentencepairscore import SentencePairScore
from yalign.input_conversion import parse_training_file


class TestSentencePairScore(unittest.TestCase):
    def setUp(self):
        base_path = os.path.dirname(os.path.abspath(__file__))
        word_scores = os.path.join(base_path, "data", "test_word_scores_big.csv")
        word_pair_score = WordPairScore(word_scores)
        self.alignments_file = os.path.join(base_path, "data", "test_training.csv")
        alignments = parse_training_file(self.alignments_file)
        self.score = SentencePairScore()
        self.score.train(alignments, word_pair_score)

    def test_does_not_raises_errors(self):
        # Since I can't test if its a good or a bad alignment at this level
        # I'll just run the code to check that no exceptions are raised
        a = Sentence(u"house you".split(), position=0.5)
        b = Sentence(u"casa usted".split(), position=0.5)
        self.score(a, b)
        a = Sentence(u"Valar Morghulis".split(), position=0.0)
        b = Sentence(u"Dracarys".split(), position=1.0)
        self.score(a, b)

    def test_score_order(self):
        a = Sentence(u"Call History .".split(), position=0.0)
        b = Sentence(u"Historial de llamadas .".split(), position=0.0)
        score1 = self.score(a, b)
        a = Sentence(u"Replace the cover .".split(), position=0.0)
        b = Sentence(u"Vuelva a ingresar un nuevo código de bloqueo .".split(),
                     position=0.26)
        score2 = self.score(a, b)
        self.assertGreater(score1, score2)

    def test_score_in_bounds(self):
        for alignment in parse_training_file(self.alignments_file):
            score = self.score(*alignment)
            self.assertGreaterEqual(score, self.score.min_bound)
            self.assertLessEqual(score, self.score.max_bound)

    def test_alignment_is_better_than_all_gaps(self):
        a = Sentence(u"house µa µb µc µd".split(), position=0.0)
        b = Sentence(u"casa  µ1 µ2 µ3 µ4".split(), position=0.0)
        align1 = self.score.problem.aligner(a, b)

        c = Sentence(u"µx µa µb µc µd".split(), position=0.0)
        d = Sentence(u"µ5 µ1 µ2 µ3 µ4".split(), position=0.0)
        align2 = self.score.problem.aligner(c, d)

        s1 = sum(x[2] for x in align1)
        s2 = sum(x[2] for x in align2)

        self.assertLess(s1, s2)

        # FIXME: check this case, the alignment appears to be wrong
        # e = Sentence(u"house µa µb µc µd µe".split(), position=0.0)
        # f = Sentence(u"casa  µ1 µ2 µ3 µ4".split(), position=0.0)
        # align3 = self.score.problem.aligner(e, f)
        # print align3


if __name__ == "__main__":
    unittest.main()
