from __future__ import division
import sys
import pickle
from collections import defaultdict

# corpus
corpus_en = []
corpus_es = []

# t
tee = dict()

# q
que = dict()

# cached n() values
n_cache = dict()


def q(j,i,l,m):
  return 1/(l+1)


def ibm2():
  global tee,que

  try:
    print "Reading final values from file..."
    # raise IOError    
    tee = pickle.load(open("jiehan_part2_ibm2_t_cache_5iters.txt"))
    que = pickle.load(open("jiehan_part2_ibm2_q_cache_5iters.txt"))
    print "Final parameters were loaded from cache file."
    return
  except IOError:
    print "Params not found."

  print "Reading t values from Part 1 file..."
  tee = pickle.load(open("jiehan_part1_ibm1_t_cache_5iters.txt"))
  print "Part 1 t parameters were loaded."

  # initialization
  print "Initializing q",
  for k in xrange(len(corpus_en)):
    if k % 100 == 0:
      sys.stdout.write(".")
      sys.stdout.flush()

    l = len(corpus_en[k])
    m = len(corpus_es[k])
    for j in xrange(l):
      for i in xrange(m):
        #que[(j,i,l-1,m)] = q(j,i,l-1,m)
        que[(j,i,l-1,m)] = 1/(l+1)
  print
  # print que

  for iteration in xrange(5):
    print "iteration   #" + str(iteration+1),
    # counts
    c = defaultdict(lambda: 0.0)
    for k in xrange(len(corpus_en)):
      if k % 100 == 0:
        sys.stdout.write(".")
        sys.stdout.flush()

      # print

      l = len(corpus_en[k])
      m = len(corpus_es[k])
      for i in xrange(m):
        for j in xrange(l):
          numerator = tee.get((corpus_es[k][i], corpus_en[k][j])) \
                      * que.get((j,i,l-1,m))
          denominator = 0.0
          for denominator_j in xrange(l):
            denominator += tee.get((corpus_es[k][i], corpus_en[k][denominator_j])) \
                           * que.get((denominator_j,i,l-1,m))
          delta = numerator/denominator

          # print k,i,j,delta

          c[(corpus_en[k][j],corpus_es[k][i])] += delta
          c[corpus_en[k][j]] += delta
          c[(j,i,l-1,m)] += delta
          c[(i,l-1,m)] += delta

    # after each iteration, update t parameters
    for f,e in tee.iterkeys():
      tee[(f,e)] = c[(e,f)]/c[e]

    # update q params as well
    for j,i,l,m in que.iterkeys():
      que[(j,i,l,m)] = c[(j,i,l,m)]/c[(i,l,m)]

    print
    # print "TEE", tee
    # print "QUE", que

  print "Writing to file..."
  pickle.dump(tee, open("jiehan_part2_ibm2_t_cache_5iters.txt", "w"))
  pickle.dump(que, open("jiehan_part2_ibm2_q_cache_5iters.txt", "w"))
  print "Done writing final q,t values."


def t(f,e):
  return 1/n(e)


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


def cache_corpus(txt, corpus, prepend_NULL=False):
  for sentence in txt:
    if prepend_NULL:
      corpus.append(tuple(["NULL"] + sentence.split()))
    else:
      corpus.append(tuple(sentence.split()))


def find_alignments(spanish_sentence, english_sentence):
  a = dict()

  l = len(english_sentence)
  m = len(spanish_sentence)
  for i_index,spanish_word in enumerate(spanish_sentence):
    # i index start from 0, but let's make it 1
    i_real = i_index + 1
    max_qt = -1
    max_j = None
    for j,english_word in enumerate(['NULL'] + english_sentence):
      this_qt = tee.get((spanish_word,english_word), 0.0) \
                * que.get((j,i_index,l,m), 0.0)
      if this_qt > max_qt:
        max_qt = this_qt
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

  assert(len(corpus_en) == len(corpus_es))

  ibm2()

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
  open("alignment_test.p2.out", "w").writelines(output_lines)
