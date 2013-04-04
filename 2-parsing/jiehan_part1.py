import json
from collections import defaultdict


word_count = defaultdict(lambda: 0)


def count_node(node):
  for this_node in node[1:]:
    if type(this_node) == unicode:  # is a terminal
      word_count[this_node] = word_count[this_node] + 1
    else:                           # node, look deeper
      count_node(this_node)


def replace_rare(node, rare_words):
  for i, this_node in enumerate(node[1:]):
    if type(this_node) == unicode:  # is a terminal
      if this_node in rare_words:
        this_node = "_RARE_"
    else:                           # node, look deeper
      replace_rare(this_node, rare_words)

    # since I sliced node already
    # we need to reflect this change in original node object
    node[i+1] = this_node

  return node

  # FIXME: save result recursively


def filter_rare(word_count):
  return {word for word, count in word_count.iteritems() if count < 5}


if __name__ == "__main__":
  lines = open("parse_train.dat").readlines()
  for line in lines:
    sentence = json.loads(line)
    count_node(sentence)

  rare_words = filter_rare(word_count)

  for i, line in enumerate(lines):
    sentence = json.loads(line)
    lines[i] = json.dumps(replace_rare(sentence, rare_words)) + '\n'

  open("parse_train.dat", 'w').writelines(lines)
