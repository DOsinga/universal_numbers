#!/usr/bin/env python

import mwparserfromhell
import subprocess
from xml import sax
import json

class WikiXmlHandler(sax.handler.ContentHandler):
  def __init__(self):
    sax.handler.ContentHandler.__init__(self)
    self._languages = {}
    self._count = 0
    self.reset()

  def reset(self):
    self._buffer = []
    self._state = None
    self._values = {}

  def startElement(self, name, attrs):
    if name in ('title', 'text'):
      self._state = name

  def endElement(self, name):
    if name == self._state:
      self._values[name] = ''.join(self._buffer)
      self._state = None
      self._buffer = []

    if name == 'page':
      if self._values.get('title', '').endswith('phrasebook'):
        numbers = []
        numbers_level = 0
        for line in self._values['text'].split('\n'):
          title = line.strip('=')
          level = (len(line) - len(title)) - 1
          if level > 1 and title.lower() == 'numbers':
            numbers_level = level
          elif numbers_level:
            if 0 < level <= numbers_level:
              break
            numbers.append(line)
        if len(numbers) > 10:
          self._languages[self._values['title'].rsplit(' ', 1)[0]] = numbers
      self.reset()
      self._count += 1
      if self._count % 100000 == 0:
        print(self._count)

  def characters(self, content):
    if self._state:
      self._buffer.append(content)


def main():
  parser = sax.make_parser()
  handler = WikiXmlHandler()
  parser.setContentHandler(handler)
  for line in subprocess.Popen(['bzcat'], stdin=open('data/enwikivoyage-latest-pages-articles.xml.bz2'), stdout=subprocess.PIPE).stdout:
    try:
      parser.feed(line)
    except StopIteration:
      break
  with open('data/numbers.json', 'w') as fout:
    json.dump(handler._languages, fout, indent=2)

if __name__ == '__main__':
  main()





