#!/usr/bin/env python3

import json
import re
from collections import defaultdict

import unidecode

RE_BRACKET = re.compile("\(([^)]+)\)")
MEDIA_MARKER = '[[Media:'

ALPHABE = 'abcdefghijklmnopqrstuvwxyz'
SOUNDEX = 'abcdafggadglmmabglsdafbgas'

VOWELS = set('aeiou')

def soundex(ch):
  return SOUNDEX[ord(ch) - ord('a')]

def deletetion_cost(st, idx):
  ch = st[idx]
  if ch == 'h':
    return 0.1
  before = st[idx - 1] if idx > 0 else None
  after = st[idx + 1] if idx < len(st) - 1 else None
  if ch == before or ch == after:
    return 0.1 if ch in VOWELS else 0.3
  if ch in VOWELS and (before in VOWELS or after in VOWELS):
    return 0.2
  if ch in VOWELS:
    return 0.5
  return 1

def substitution_cost(ch1, ch2):
  if ch1 == ch2:
    return 0
  sd1 = soundex(ch1)
  sd2 = soundex(ch2)
  if (ch1 == 'c' or ch2 == 'c') and (sd1 == 's' or sd2 == 's'):
    return 0.4
  if sd1 == sd2:
    return 0.4
  return 1.8


def strip_word(word):
  word = word.replace('gh', 'y')
  return ''.join(ch for ch in unidecode.unidecode(word).lower() if 'a' <= ch <= 'z')


def compare_words(w1, w2):
  w1_size = len(w1) + 1
  w2_size = len(w2) + 1
  dist = [[0] * w1_size for _ in range(w2_size)]
  for i in range(1, w2_size):
    dist[i][0] = dist[i - 1][0] + deletetion_cost(w2, i - 1)
  for i in range(1, w1_size):
    dist[0][i] = dist[0][i - 1] + deletetion_cost(w1, i - 1)
  for col in range(1, w1_size):
    for row in range(1, w2_size):
      dist[row][col] = min(dist[row-1][col] + deletetion_cost(w2, row - 1),
                           dist[row][col-1] + deletetion_cost(w1, col - 1),
                           dist[row-1][col-1] + substitution_cost(w2[row - 1], w1[col - 1]))
  return dist[-1][-1]


def score_distances(distances):
  return sum((10.0 / (10.0 + dist)) ** 1.5 for dist in distances) / len(distances)


def strip_pronunciation(candidate):
  p = candidate.find(MEDIA_MARKER)
  if p > -1:
    p2 = candidate.find('|', p)
    if p2 > -1:
      p3 = candidate.find(']]', p2)
      if p3 > -1:
        candidate = candidate[p2 + 1:p3]
  candidate = candidate.replace('/', ' ').replace('[', ' ').replace('ə', 'uh')
  p = candidate.find(' ')
  if p > -1:
    candidate = candidate[:p]
  return candidate.strip(" '.\"")


def extract_numbers(name, lang):
  numbers = [None] * 10
  for orig_line in lang:
    line = orig_line.strip()
    if not line.startswith(';'):
      continue
    line = line.strip(' ;')
    bits = line.split(':', 1)
    if len(bits) != 2:
      continue

    number, pronunciation = bits
    try:
      number = int(number.replace(',', ''))
    except ValueError:
      continue
    candidates = RE_BRACKET.findall(pronunciation)
    has_quote = False
    best_pronunciation = strip_pronunciation(pronunciation)
    for candidate in candidates:
      candidate_has_quote = candidate[0] == candidate[-1] == "'"
      candidate_stripped = strip_pronunciation(candidate)
      if candidate_stripped and (best_pronunciation is None or (not has_quote and candidate_has_quote)):
        best_pronunciation = candidate_stripped
        has_quote = candidate_has_quote

    if 0 < number <= 10 and not numbers[number - 1] and best_pronunciation:
      numbers[number - 1] = best_pronunciation

  if not all(numbers):
    return None
  return numbers


def main():
  with open('data/numbers.json') as fin:
    languages = json.load(fin)
  languages = {name: extract_numbers(name, lang) for name, lang in languages.items()}
  lang_names = list(sorted(k for k, v in languages.items() if v))# and k in ('French', 'Italian', 'Dutch', 'German')))
  stripped = {name: list(map(strip_word, languages[name])) for name in lang_names}
  by_number = defaultdict(list)
  by_language_pair = defaultdict(list)
  for number in range(10):
    for i, first in enumerate(lang_names):
      for second in lang_names[i + 1:]:
        distance = compare_words(stripped[first][number], stripped[second][number])
        by_number[number].append((first, second, distance))
        by_language_pair[(first, second)].append(distance)

  language_pairs = [(first, second, score_distances(distance)) for (first, second), distance in by_language_pair.items()]

  medians = []
  for number in range(10):
    scores = defaultdict(float)
    for lang1, lang2, distance in by_number[number]:
      distance2 = distance * distance
      scores[lang1] += distance2
      scores[lang2] += distance2
    min_lang, _ = min(scores.items(), key=lambda t:t[1])
    medians.append((min_lang, languages[min_lang][number]))

  with open('data/onetonine.txt', 'w') as fout:
    for lang_name in lang_names:
      fout.write('\n%s\n' % lang_name)
      for number in languages[lang_name]:
        fout.write('  ' + number + '\n')
    fout.write('\nUniversal\n')
    for from_lang, number in medians:
      fout.write('  %s (%s)\n' % (number, from_lang))

  with open('data/pairs.json', 'w') as fout:
    json.dump(sorted(language_pairs, key=lambda triplet:triplet[2], reverse=True), fout, indent=2)

  with open('data/scored_numbers.json', 'w') as fout:
    json.dump(by_number, fout, indent=2)


if __name__ == '__main__':
  main()





