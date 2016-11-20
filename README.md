# universal numbers
Measure the distances between numbers from different languages by using a slightly modified edit distance algorithm. This gives us a language map showing the distances and also a universal 1-10 numbers list, by taking the median number for each.

To get there, run extract_numbers.py over a wiki dump of wikivoyage. Then run compare_languages to get the language matrix. build_tree.py then spits out a language tree if you are interested in that too.
