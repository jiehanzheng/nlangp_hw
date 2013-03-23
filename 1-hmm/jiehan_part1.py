from __future__ import division
import sys

counts = dict()
tag_counts = dict()


def count_corpus(y, x=None):
  """
  Look in the counts that count_freqs.py generated, and return number of 
  occurrences of word x, or occurrences of word x and tag y, if y is given.

  """

  # print "x =", x, ", y =", y

  if x:
    try:
      # print 'from counts', counts[('WORDTAG', y, x)]
      return counts[('WORDTAG', y, x)]
    except KeyError:
      pass
  else:
    # print 'from tag counts', tag_counts[y]
    return tag_counts[y]

  # before we use _RARE_, check and see if it is really rare
  if (('WORDTAG', 'O', x) not in counts) and (('WORDTAG', 'I-GENE', x) not in counts):
    # print 'from rare', counts[('WORDTAG', y, '_RARE_')]
    return counts[('WORDTAG', y, '_RARE_')]

  # print 'from nothing', 0
  return 0



def emission(x, y):
  return count_corpus(x=x, y=y) / count_corpus(y=y)


def cache_counts(lines):
  """
  Build a dictionary for O(1) lookup.

  The dict key is a tuple, in the form of tuple(the_type, ...), where

    the_type -- WORDTAG or 1-/2-/3-GRAM
    ...      -- 2-3 tags/words

  """
  for line in lines:
    line = line.split()
    if line:
      # cache with fp being the key
      fp = line[1:]
      counts[tuple(fp)] = int(line[0])

      # count tag for the denominator
      if line[1] == 'WORDTAG':
        try:
          tag_counts[line[2]] = tag_counts[line[2]] + int(line[0])
        except KeyError:
          tag_counts[line[2]] = 0


if __name__ == "__main__":
  print "Reading counts..."
  counts_lines = open("gene.counts","r").readlines()
  cache_counts(counts_lines)
  print len(counts_lines), "lines read and cached."

  print "Reading dev file..."
  # dev_lines = open("gene.dev","r").readlines()
  dev_lines = open("gene.test","r").readlines()
  dev_lines = dev_lines[:]
  print len(dev_lines), "lines read."

  for i, dev_line in enumerate(dev_lines):
    dev_word = dev_line.strip()
    if dev_word:
      dev_line = dev_word + ' '
      dev_line = dev_line + ('O' if emission(x=dev_word, y='O') > emission(x=dev_word, y='I-GENE') else 'I-GENE')
      dev_line = dev_line + "\n"
      dev_lines[i] = dev_line

  print "Writing dev file..."
  # out_file = open("gene_dev.p1.out","w")
  out_file = open("gene_test.p1.out","w")
  out_file.writelines(dev_lines)

  # print "-"
  # print "O:",
  # print emission(x="-", y='O')
  # print "GENE:",
  # print emission(x="-", y='I-GENE')
