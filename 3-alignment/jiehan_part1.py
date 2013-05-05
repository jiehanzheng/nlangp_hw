from __future__ import division
import sys
import pickle
from collections import defaultdict

# corpus
corpus_en = []
corpus_es = []

# t
tee = dict()

# cached n() values
n_cache = dict()


def n(e):
  """
  Number of different words that occur in any translation of a sentence
  containing e.

  """

  if e not in n_cache:
    possible_foreign_words = set()
    for k,english_sentence in enumerate(corpus_en):
      if e in english_sentence:
        possible_foreign_words |= set(corpus_es[k])

    n_cache[e] = len(possible_foreign_words)

  return n_cache[e]


def ibm1():
  global tee

  try:
    print "Reading final t values from file..."
    tee = pickle.load(open("jiehan_part1_ibm1_t_cache_5iters.txt"))
    print "final t parameters were loaded from cache file."
    return
  except IOError:
    print "Final t params not found."

  # initialization
  print "Initializing",
  for k,english_sentence in enumerate(corpus_en):
    if k % 100 == 0:
      sys.stdout.write(".")
      sys.stdout.flush()

    for english_word in english_sentence:
      for spanish_word in corpus_es[k]:
        tee[(spanish_word, english_word)] = t(spanish_word,english_word)
  print
  # print tee

  for iteration in xrange(5):
    print "iteration #" + str(iteration+1),
    # counts
    c = None
    c = defaultdict(lambda: 0.0)
    for k in xrange(len(corpus_en)):
      if k % 100 == 0:
        sys.stdout.write(".")
        sys.stdout.flush()
      for i in xrange(len(corpus_es[k])):
        for j in xrange(len(corpus_en[k])):
          numerator = tee.get((corpus_es[k][i], corpus_en[k][j]))
          denominator = 0.0
          for denominator_j in xrange(len(corpus_en[k])):
            denominator += tee.get((corpus_es[k][i], corpus_en[k][denominator_j]))
          delta = numerator/denominator
          # print k,i,j,delta
          c[(corpus_en[k][j],corpus_es[k][i])] += delta
          c[corpus_en[k][j]] += delta

    # after each iteration, update t parameters
    for f,e in tee.iterkeys():
      tee[(f,e)] = c[(e,f)]/c[e]

    print
    # print tee

  print "Writing to file..."
  pickle.dump(tee, open("jiehan_part1_ibm1_t_cache_5iters.txt", "w"))
  print "Done writing final t values."


def t(f,e):
  return 1/n(e)


def cache_corpus(txt, corpus, prepend_NULL=False):
  for sentence in txt:
    if prepend_NULL:
      corpus.append(tuple(["NULL"] + sentence.split()))
    else:
      corpus.append(tuple(sentence.split()))


def find_alignments(spanish_sentence, english_sentence):
  a = dict()
  for i_index,spanish_word in enumerate(spanish_sentence):
    # i index start from 0, but let's make it 1
    i_real = i_index + 1
    max_t = -1
    max_j = None
    for j,english_word in enumerate(['NULL'] + english_sentence):
      this_t = tee.get((spanish_word,english_word), 0.0)
      if this_t > max_t:
        max_t = this_t
        max_j = j
    a[i_real] = max_j

  return a


if __name__ == '__main__':
  corpus_en_txt = open("corpus.en").readlines()
  # corpus_en_txt = ["the car","the house","the woman"]
  cache_corpus(corpus_en_txt, corpus_en, prepend_NULL=True)

  corpus_es_txt = open("corpus.es").readlines()
  # corpus_es_txt = ["la coche","el casa","el mujer"]
  cache_corpus(corpus_es_txt, corpus_es)

  # print corpus_en
  # print corpus_es

  assert(len(corpus_en) == len(corpus_es))

  ibm1()

  # for key,value in tee.items():
  #   if key[1] == "requested":
  #     print key, value

  # dev_en_txt = open("dev.en").readlines()
  dev_en_txt = open("test.en").readlines()

  # dev_es_txt = open("dev.es").readlines()
  dev_es_txt = open("test.es").readlines()

  output_lines = []
  for k,spanish_sentence_txt in enumerate(dev_es_txt):
    spanish_sentence = spanish_sentence_txt.split()
    english_sentence = dev_en_txt[k].split()
    
    for spanish_index, english_index in find_alignments(spanish_sentence, english_sentence).items():
      output_lines.append(str(k+1) + ' ' + str(english_index) + ' ' + str(spanish_index) + '\n')

  # open("dev.out", "w").writelines(output_lines)
  open("alignment_test.p1.out", "w").writelines(output_lines)
