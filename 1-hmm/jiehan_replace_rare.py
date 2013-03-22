import sys


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

  rare_words = []
  for word, count in counts.iteritems():
    if count < 5:
      rare_words.append(word)

  return rare_words


def replace_with_rare(input, word):
  for i, line in enumerate(input):
    tokens = line.split()

    try:
      if tokens[0] == word:
        tokens[0] = "_RARE_"
        print "  > Line replaced with", tokens
        input[i] = ' '.join(tokens) + "\n"
    except IndexError:
      continue


if __name__ == "__main__":
  try:
    input = open(sys.argv[1],"r").readlines()
  except IOError:
    sys.stderr.write("ERROR: Cannot read inputfile %s.\n" % arg)
    sys.exit(1)

  print len(input), "lines read."

  rare_words = find_rare_words(input)

  print "Going to replace", len(rare_words), "words."

  for i, rare_word in enumerate(rare_words):
    print "[", i,"]", "Replacing", rare_word, "..."
    replace_with_rare(input, rare_word)

  output = open(sys.argv[1],"w")
  output.writelines(input)
