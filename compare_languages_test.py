#!/usr/bin/env python

import json
import unittest
import compare_languages
from compare_languages import compare_words


class TestCompareLanguagesEditDistance(unittest.TestCase):
  def setUp(self):
    self.old_funcs = compare_languages.deletetion_cost, compare_languages.substitution_cost
    compare_languages.deletetion_cost = lambda st, idx: 1
    compare_languages.substitution_cost = lambda ch: 1.5

  def test_compare_words(self):
    self.assertEqual(compare_words('hello', 'hello'), 0)
    self.assertEqual(compare_words('hello', 'hell'), 1)
    self.assertEqual(compare_words('hello', 'helo'), 1)
    self.assertEqual(compare_words('helo', 'hello'), 1)
    self.assertEqual(compare_words('hell', 'hello'), 1)
    self.assertEqual(compare_words('he123', 'helllo143'), 5.5)
    self.assertEqual(compare_words('helloXX', 'heXX'), 3)
    self.assertEqual(compare_words('hell123', 'hello123'), 1)
    self.assertEqual(compare_words('hello123', 'hell123'), 1)
    self.assertEqual(compare_words('hello123', 'helmo123'), 1.5)
    self.assertEqual(compare_words('helmo123', 'hello123'), 1.5)
    self.assertEqual(compare_words('abcdefgh', 'xaxcdefxh'), 4.0)
    self.assertEqual(compare_words('zayvuhn', 'zeeben'), 7.0)

  def tearDown(self):
    compare_languages.deletetion_cost, compare_languages.substitution_cost = self.old_funcs


class TestCompareLanguagesWeights(unittest.TestCase):

  def test_compare_weights(self):
    d = compare_words('i', 'ee')
    print(d)

    self.assertLess(
      compare_words('veer', 'fear'),
      compare_words('veer', 'lear'),
    )
    self.assertLess(
      compare_words('hello', 'ello'),
      compare_words('hello', 'hell'),
    )
    self.assertLess(
      compare_words('hello', 'helo'),
      compare_words('hello', 'henlo'),
    )
    self.assertLess(
      compare_words('hello', 'hallo'),
      compare_words('hello', 'henlo'),
    )
    self.assertLess(
      compare_words('sihnk', 'cheenkweh'),
      compare_words('weet', 'ohtoh')
    )


if __name__ == '__main__':
  unittest.main()
