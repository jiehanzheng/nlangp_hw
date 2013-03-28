from __future__ import division
from collections import defaultdict
import sys

# hehehe let's be lazy and steal some functions from this professor's script
import count_freqs


counts = dict()
tag_counts = dict()


def viterbi(k, u, v, x, pi={(0,'*','*'): 1}, bp=dict(), K=None, outermost=True):
  """ We take care of STOP symbol already, so STOP shouldn't be passed in """

  # see if we have something already cached
  if (k, u, v) in pi:
    return pi[(k, u, v)]

  if k == 0:
    raise Exception("wtf?!  if k == 0 we should have returned!")

  # K[] stores possible tags for its corresponding index locations
  if K is None:
    # for most of the terms, K can be the two tags
    K = defaultdict(lambda: {'I-GENE', 'O'})

    # first two terms (beginning of sentence) should always be *
    K['-1'] = {'*'}
    K['0'] = {'*'}

  for v in K[str(k)]:
    for u in K[str(k-1)]:
      best_pi = 0
      best_w = '?'
      for w in K[str(k-2)]:
        this_pi = viterbi(k-1,w,u,x,pi=pi,bp=bp,K=K,outermost=False) * transition(v,w,u) * emission(x[k],v)
        if this_pi > best_pi:
          best_pi = this_pi
          best_w = w
      pi[(k,u,v)] = best_pi
      bp[(k,u,v)] = best_w

  print "pi at", k, u, v, "is", pi

  # let's see who is the best friend with STOP symbol
  # if we are the first function call (end of sentence)
  if not outermost:
    return best_pi
  else:
    best_pi = 0
    best_uv = ('?', '?')
    for u in K[str(k-1)]:
      for v in K[str(k)]:
        this_pi = viterbi(k,u,v,x,pi=pi,bp=bp,K=K,outermost=False) * transition('STOP',u,v)
      if this_pi > best_pi:
        best_pi = this_pi
        best_uv = (u,v)

    return best_uv


def emission(x, y):
  """ e(x|y) = Count(x,y)/Count(y) """
  return count_wordtag(x=x, y=y) / count_wordtag(y=y)


def transition(w, u, v):
  """ q(w|u,v) = Count(u,v,w)/Count(u,v) """
  return count_ngram(u=u, v=v, w=w) / count_ngram(u=u, v=v)


def count_ngram(u, v, w=None):
  """
  Look in the counts that count_freqs.py generated, and return number of 
  occurrences of tag u,v, in addition to w if w is specified.

  """
  if w:  # bigram
    try:
      return counts[('3-GRAM', u, v, w)]
    except KeyError:
      pass
  else:  # trigram
    try:
      return counts[('2-GRAM', u, v)]
    except KeyError:
      pass

  return 0


def count_wordtag(y, x=None):
  """
  Look in the counts that count_freqs.py generated, and return number of 
  occurrences of tag y, or number of occurrences of tag y and word x, 
  if x is given.

  """
  if x:
    try:
      return counts[('WORDTAG', y, x)]
    except KeyError:
      pass
  else:
    return tag_counts[y]

  # before we use _RARE_, check and see if it is really rare
  if (('WORDTAG', 'O', x) not in counts) and (('WORDTAG', 'I-GENE', x) not in counts):
    return counts[('WORDTAG', y, '_RARE_')]

  return 0


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

  print viterbi(14, 'I-GENE', 'O', [None, "Therefore", ",", "we", "suggested", "that", "both", "proteins", "might", "belong", "to", "the", "PLTP", "family", "."])
  # print viterbi(1, '*', 'O', [None, "Therefore"])


  # TESTS FOR count_ngram()
  # print "OOO"
  # print "uvw"
  # print count_ngram("O", "O", "O")
  # print "uv"
  # print count_ngram("O", "O")
  # print "uvw/uv"
  # print transition("O", "O", "O")



  # for i, dev_line in enumerate(dev_lines):
  #   dev_word = dev_line.strip()
  #   if dev_word:
  #     dev_line = dev_word + ' '
  #     dev_line = dev_line + ('O' if emission(x=dev_word, y='O') > emission(x=dev_word, y='I-GENE') else 'I-GENE')
  #     dev_line = dev_line + "\n"
  #     dev_lines[i] = dev_line

  # print "Writing dev file..."
  # # out_file = open("gene_dev.p1.out","w")
  # out_file = open("gene_test.p1.out","w")
  # out_file.writelines(dev_lines)
