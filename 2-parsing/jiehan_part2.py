from __future__ import division
import json
from collections import defaultdict


# counts read from training set
fp_counts = dict()

# non-terminal symbols
N = set()

# "non-rare" words
non_rare = set()

# rules in CNF
R_binary = defaultdict(lambda: list())


def cky_parse(sentence):
  """ Implementation of the algorithm described on p. 14 """

  # initialization
  pi = defaultdict(lambda: 0.0)
  bp = dict()

  # split sentence into words
  x = sentence.split()
  n = len(x)

  # prepend one empty element to x so that real word starts at index 1
  x.insert(0, None)

  # terminals
  for i in range(1,n+1):
    for X in N:
      pi[(i,i,X)] = distribution(X, x[i])

  # non-terminals
  for l in range(1,n):
    for i in range(1,n-l+1):
      j = i + l
      for X in N:
        max_pi = -1
        max_pi_bp = None
        for rule in R_binary[X]:
          for s in range(i,j):
            Y = rule[0]
            Z = rule[1]
            this_pi = distribution(X,Y,Z) * pi[(i,s,Y)] * pi[(s+1,j,Z)]
            # if this_pi > 0.0:
            # # if True:
              # print "q(%s->%s %s)*pi(%s,%s,%s)*pi(%s,%s,%s)" % (X,Y,Z,i,s,Y,s+1,j,Z),
              # print '=', this_pi
              # print distribution(X,Y,Z),pi[(i,s,Y)],pi[(s+1,j,Z)]
            if this_pi > max_pi:
              max_pi = this_pi
              max_pi_bp = (rule,s)
        # print "pi("+str(i)+','+str(j)+','+X+') =',
        pi[(i,j,X)] = max_pi if max_pi > 0 else 0.0
        bp[(i,j,X)] = max_pi_bp
        # print pi[(i,j,X)]

  # recover tree from bp
  return bp_recover(bp,1,n,'SBARQ',x)


def bp_recover(bp,i,j,X,x,depth=0):
  tree = []

  # if we are at the terminal level
  # return tree[0] being the pos tag, tree[1] being the word in x
  if i == j:
    tree.append(X)
    tree.append(x[i])
    return tree

  # print "  "*depth,"recovering", i,j,X, '=', bp[(i,j,X)]

  # tree[0] is the tag
  tree.append(X)

  # tree[1] is the Y
  # print "  "*depth,"--> recover Y", bp[(i,j,X)][0][0], "from", i, "to", bp[(i,j,X)][1]
  tree.append(bp_recover(bp, i, bp[(i,j,X)][1], bp[(i,j,X)][0][0], 
              x, depth=depth+1))

  # tree[2] is the Z
  # print "  "*depth,"--> recover Z", bp[(i,j,X)][0][1], "from", bp[(i,j,X)][1]+1, "to", j
  tree.append(bp_recover(bp, bp[(i,j,X)][1]+1, j, bp[(i,j,X)][0][1], 
              x, depth=depth+1))

  return tree


def distribution(x,y1,y2=None):
  numerator = count(x,y1,y2)
  denominator = count(x)

  # print numerator, '/', denominator

  try:
    return numerator / denominator
  except ZeroDivisionError:
    return 0.0


def count(x,y1=None,y2=None):
  # print '(', x, y1, y2, '):',

  # x,y1,y2 all present: BINARYRULE
  if y1 is not None and y2 is not None:
    try:
      return fp_counts[('BINARYRULE',x,y1,y2)]
    except KeyError:
      return 0

  # only x,y1: UNARYRULE
  elif y1 is not None:
    try:
      return fp_counts[('UNARYRULE',x,y1)]
    except KeyError:
      if y1 in non_rare:
        return 0
      try:
        return fp_counts[('UNARYRULE',x,'_RARE_')]
      except KeyError:
        return 0

  # x only: NONTERMINAL
  else:
    try:
      return fp_counts[('NONTERMINAL',x)]
    except KeyError:
      return 0


def cache_counts(lines):
  for line in lines:
    line = line.split()
    if line:
      # cache with fp being the key
      fp = line[1:]
      fp_counts[tuple(fp)] = int(line[0])

      # populate N
      if line[1] == 'NONTERMINAL':
        N.add(line[2])

      # populate R
      if line[1] == 'BINARYRULE':
        R_binary[line[2]].append((line[3], line[4]))

      # populate non-rare words
      if line[1] == 'UNARYRULE':
        non_rare.add(line[3])


if __name__ == '__main__':
  training_lines = open("parse_train.counts.out").readlines()
  cache_counts(training_lines)

  # input_lines = open("parse_dev.dat").readlines()
  input_lines = open("parse_test.dat").readlines()

  output_lines = []
  for input_line in input_lines:
    tree = cky_parse(input_line)
    print tree
    output_lines.append(json.dumps(tree) + '\n')

  # open("parse_dev.p2.out",'w').writelines(output_lines)
  open("parse_test.p2.out",'w').writelines(output_lines)
