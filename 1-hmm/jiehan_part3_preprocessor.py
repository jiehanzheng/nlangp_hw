import re


numeric = re.compile('\d')
all_caps = re.compile('^[A-Z]+$')
last_capital = re.compile('[A-Z]$')

def word_class(word):
  if re.search(numeric, word):
    return '_NUMERIC_'
  elif re.search(all_caps, word):
    return '_ALLCAPS_'
  elif re.search(last_capital, word):
    return '_LASTCAPITAL_'

  return '_RARE_'


def find_rare_words(input):
  counts = dict()
  for line in input:
    try:
      word, _ = line.split()[:2]
      try:
        counts[word] = counts[word] + 1
      except KeyError:
        counts[word] = 1
    except ValueError:
      continue

  rare_words = set()
  for word, count in counts.iteritems():
    if count < 5:
      rare_words.add(word)

  return rare_words


def replace_with_rare(input, rare_words):
  for i, line in enumerate(input):
    tokens = line.split()

    try:
      if tokens[0] in rare_words:
        print "  >", tokens[0],
        tokens[0] = word_class(tokens[0])
        print "replaced with", tokens[0]
        input[i] = ' '.join(tokens) + "\n"
    except IndexError:
      continue


if __name__ == "__main__":
  try:
    input = open("gene_with_better_classes.train","r").readlines()
  except IOError:
    sys.stderr.write("ERROR: Cannot read inputfile %s.\n" % arg)
    sys.exit(1)

  print len(input), "lines read."

  rare_words = find_rare_words(input)

  print "Going to replace", len(rare_words), "words."
  replace_with_rare(input, rare_words)

  output = open("gene_with_better_classes.train","w")
  output.writelines(input)
