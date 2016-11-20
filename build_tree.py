#!/usr/bin/env python3

import pprint
import json
import itertools
import random

def flatten(l):
  if isinstance(l, str):
    yield l
  else:
    for el in l:
      if not isinstance(el, str):
        for sub in flatten(el):
          yield sub
      else:
        yield el

def score_group(grp1, grp2, numbers):
#  if isinstance(grp1, tuple) and isinstance(grp2, tuple):
#    print('yo')
  res = 0.0
  for number in range(10):
    best_distance = None
    for l1 in flatten(grp1):
      for l2 in flatten(grp2):
        if l1 > l2:
          k = (l2, l1, number)
        else:
          k = (l1, l2, number)
        distance = numbers[k]
        if best_distance is None or distance < best_distance:
          best_distance = distance
    res += best_distance
  return res


def render_tree(tree):
  if isinstance(tree, str):
    return tree
  tree = list(tree)
  random.shuffle(tree)
  return '(%s)' % ','.join(render_tree(subtree) for subtree in tree if not ':' in subtree)

def main():
  numbers = json.load(open('data/scored_numbers.json'))
  distances = {}
  tree = set()
  for number, lst in numbers.items():
    for lang1, lang2, distance in lst:
      tree.add(lang1)
      tree.add(lang2)
      distances[(lang1, lang2, int(number))] = distance
  tree = list(tree)

  while len(tree) > 1:
    min_distance = None
    max_grp1 = None
    max_grp2 = None
    for grp1, grp2 in itertools.combinations(tree, 2):
      distance = score_group(grp1, grp2, distances)
      if isinstance(grp1, str):
        distance *= 0.65
      if isinstance(grp2, str):
        distance *= 0.65
      if min_distance is None or distance < min_distance:
        min_distance = distance
        max_grp1 = grp1
        max_grp2 = grp2
#    print('joining %s with %s (dist=%2.2f)' % (max_grp1, max_grp2, min_distance))
    if type(max_grp1) == tuple and isinstance(max_grp2, str):
      new_elem = max_grp1 + (max_grp2,)
    else:
      new_elem = (max_grp1, max_grp2)
    tree = [new_elem] + [grp for grp in tree if grp != max_grp1 and grp != max_grp2]
  print(render_tree(tree))


if __name__ == '__main__':
  main()





