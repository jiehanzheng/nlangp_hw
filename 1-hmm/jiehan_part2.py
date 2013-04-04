from __future__ import division
from collections import defaultdict
import sys


counts = dict()
tag_counts = dict()


def viterbi(x_list):
  """ Given list x, return a list containing corresponding tags. """
  # n is the number of words
  n = len(x_list)

  # list -> dictionary
  x = dict()
  x['-1'] = '*'
  x['0'] = '*'
  for i, x_list_item in enumerate(x_list):
    x[str(i+1)] = x_list_item

  # print x

  # allowed tags for each position
  K = defaultdict(lambda: {'I-GENE', 'O'})
  K['-1'] = {'*'}
  K['0'] = {'*'}

  # store results
  pi = {(0,'*','*'): 1}
  bp = dict()

  for k in range(1,n+1):
    for u in K[str(k-1)]:
      for v in K[str(k)]:
        max_pi = -1
        max_pi_w = None
        for w in K[str(k-2)]:
          # print k,x[str(k)]+'->'+w,u,v,
          this_pi = pi[(k-1,w,u)] * transition(v,w,u) * emission(x[str(k)],v)
          # print "=", this_pi, '(p:', pi[(k-1,w,u)],'t:', transition(v,w,u), 'e:', emission(x[str(k)],v), ')',
          # print "curmax =", max_pi,

          if this_pi >= max_pi or max_pi_w is None:
            max_pi = this_pi
            max_pi_w = w
            # print "[max]",
          # print
        # print 'bp ('+str(k)+', '+str(u)+', '+str(v)+') =', max_pi_w
        pi[(k,u,v)] = max_pi
        bp[(k,u,v)] = max_pi_w

  # prepare y to return
  y = dict()

  # set last two tags
  max_pi = -1
  for u in K[str(n-1)]:
    for v in K[str(n)]:
      this_pi = pi[(n,u,v)] * transition('STOP',u,v)
      if this_pi >= max_pi:
        y[str(n-1)] = u
        y[str(n)] = v

  for k in range(n-2, 1-1, -1):
    y[str(k)] = bp[(k+2,y[str(k+1)],y[str(k+2)])]

  # print bp
  # print y

  # dict --> list
  # print sorted([int(i) for i in y.iterkeys()])
  return [y[str(i)] for i in sorted([int(i) for i in y.iterkeys()]) if int(i) >= 1]


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
  counts_lines = open("gene.part2.counts","r").readlines()
  cache_counts(counts_lines)
  print len(counts_lines), "lines read and cached."

  print "Reading dev file..."
  dev_lines = open("gene.dev","r").readlines()
  # dev_lines = open("gene.test","r").readlines()
  dev_lines = dev_lines[:]
  print len(dev_lines), "lines read."

  # print viterbi(["Therefore", ",", "we", "suggested", "that", "both", "proteins", "might", "belong", "to", "the", "PLTP", "family", "."])
  # print viterbi(["Finally",",","a","chromogenic","method","was","used",",","based","on","thrombin","inhibition","and","the","substrate","S","-","2238","."])
  # print viterbi(["Molecular","cloning",",","genomic","mapping",",","and","expression","of","two","secretor","blood","group","alpha","(","1",",","2",")","fucosyltransferase","genes","differentially","regulated","in","mouse","uterine","epithelium","and","gastrointestinal","tract","."])
  # print viterbi(["STAT5A","mutations","in","the","Src","homology","2","(","SH2",")","and","SH3","domains","did","not","alter","the","BTK","-","mediated","tyrosine","phosphorylation","."])

  out_lines = []

  sentence_buffer = []
  for dev_line in dev_lines:
    if len(dev_line.strip()):
      sentence_buffer.append(dev_line.strip())
    else:  # end of sentence
      # print sentence_buffer
      tags = viterbi(sentence_buffer)
      # print tags
      # print

      for i, word in enumerate(sentence_buffer):
        out_lines.append(word + ' ' +tags[i]+'\n')
      out_lines.append('\n')

      sentence_buffer = []

  # TESTS FOR count_ngram()
  # print "OOO"
  # print "uvw"
  # print count_ngram("O", "O", "O")
  # print "uv"
  # print count_ngram("O", "O")
  # print "uvw/uv"
  # print transition("O", "O", "O")

  print "Writing dev file..."
  out_file = open("gene_dev.p2.out","w")
  # out_file = open("gene_test.p2.out","w")
  out_file.writelines(out_lines)
