import collections
import copy
import json
import os
import re

EXPAND_RE = re.compile(r"\$([a-z]*)")

lookup = {
  "start": {
    "lore": {},
    "influence": {},
    "tool": {},
    "ingredient": {}
  },
  "alllore": {
    "grail": {"subverts": "heart"},
    "moth": {"subverts": "grail"},
    "lantern": {"subverts": "moth"},
    "forge": {"subverts": "lantern"},
    "edge": {"subverts": "forge"},
    "winter": {"subverts": "edge"},
    "heart": {"subverts": "winter"},
    "knock": {},
    "secrethistories": {}
  },
  "lore": {
    "grail": {"subverts": "heart"},
    "moth": {"subverts": "grail"},
    "lantern": {"subverts": "moth"},
    "forge": {"subverts": "lantern"},
    "edge": {"subverts": "forge"},
    "winter": {"subverts": "edge"},
    "heart": {"subverts": "winter"},
    "knock": {},
  },
  "effort": {
    "reason": {},
    "passion": {}
  }
}

writing_recipes = """{
  "$start": {
    "link": {
      "add_pigment": {}
    },
    "requirements": {
      "writingskill": 1,
      "{start}": 1
    },
    "aspects": {
      "fatiguing": 1
    },
    "craftable": true
  },
  "summoned": {
    "link": {
      "add_pigment": {}
    },
    "effects": {
      "insight": 1
    },
    "requirements": {
      "writingskill": 1,
      "summoned": 1
    },
    "aspects": {
      "fatiguing": 1
    },
    "craftable": true
  },
  "add_pigment": {
    "slots": [
      {
        "id": "Ink",
        "required": {
          "pigment": 1
        },
        "description": "XXX Ink"
      }
    ],
    "alt": {
      "added_$lore_match": {},
      "added_pigment": {}
    },
    "link": {
      "add_reason_passion": {}
    }
  },
  "added_$lore_match": {
    "requirements": {
      "{lore}": 5,
      "ingredient{lore}b": 1
    },
    "effects": {
      "insight": 1
    },
    "link": {
      "add_reason_passion": {}
    }
  },
  "added_pigment": {
    "requirements": {
      "pigment": 1
    },
    "link": {
      "add_reason_passion": {}
    }
  },
  "add_reason_passion": {
    "slots": [
      {
        "id": "Effort",
        "required": {
          "$effort": 1
        },
        "description": "XXX Reason or passion"
      }
    ],
    "alt": {
      "added_$effort": {}
    },
    "deckeffect": {
      "writing_results_basic": 1
    },
    "link": {
      "manuscript_$alllore": {},
      "nothing": {}
    }
  },
  "added_$effort": {
    "requirements": {
      "{effort}": 1
    },
    "effects": {
      "insight": 1
    },
    "deckeffect": {
      "writing_results_{effort}": 1
    },
    "link": {
      "secret_$alllore": {"chance": 85},
      "almanac_$lore": {},
      "book_$lore_subvert": {"comments": "subverts {subverts}"},
      "book_$alllore": {},
      "manuscript_$alllore": {},
      "nothing": {}
    }
  },
  "secret_$alllore": {
    "requirements": {
      "{alllore}": 6,
      "pigment": 1,
      "reason": 1,
      "lore": -1
    },
    "alt": {
      "secret_{alllore}_c": {"chance": 60},
      "secret_{alllore}_b": {"chance": 80},
      "secret_{alllore}_a": {}
    }
  },
  "secret_$alllore_c": {
    "requirements": {
      "{alllore}": 16,
      "writingskill": 3
    },
    "effects": {
      "fragment{alllore}c": 1,
      "insight": 2
    },
    "link": {
      "results": {}
    }
  },
  "secret_$alllore_b": {
    "requirements": {
      "{alllore}": 10,
      "writingskill": 2
    },
    "effects": {
      "fragment{alllore}b": 1,
      "insight": 1
    },
    "link": {
      "results": {}
    }
  },
  "secret_$alllore_a": {
    "requirements": {
      "{alllore}": 6
    },
    "effects": {
      "fragment{alllore}": 1
    },
    "link": {
      "results": {}
    }
  },
  "almanac_$lore": {
    "requirements": {
      "{lore}": 14,
      "reason": 1,
      "writingskill": 3
    },
    "effects": {
      "insight": 1,
      "writing_almanac_{lore}": 1
    },
    "link": {
      "results": {}
    }
  },
  "book_$lore_subvert": {
    "requirements": {
      "{subverts}": 8,
      "{lore}": 4,
      "passion": 1,
      "writingskill": 3
    },
    "effects": {
      "writing_book_{lore}_subvert": 1,
      "insight": 1
    },
    "link": {
      "results": {}
    }
  },
  "book_$alllore": {
    "requirements": {
      "{alllore}": 10,
      "passion": 1,
      "writingskill": 2
    },
    "effects": {
      "writing_book_{alllore}": 1
    },
    "link": {
      "results": {}
    }
  },
  "manuscript_$alllore": {
    "requirements": {
      "{alllore}": 2
    },
    "alt": {
      "manuscript_{alllore}_c": {},
      "manuscript_{alllore}_b": {},
      "manuscript_{alllore}_a": {}
    }
  },
  "manuscript_$alllore_c": {
    "requirements": {
      "{alllore}": 10,
      "writingskill": 3
    },
    "effects": {
      "article{alllore}c": 1
    },
    "link": {
      "results": {}
    }
  },
  "manuscript_$alllore_b": {
    "requirements": {
      "{alllore}": 6,
      "writingskill": 2
    },
    "effects": {
      "article{alllore}b": 1
    },
    "link": {
      "results": {}
    }
  },
  "manuscript_$alllore_a": {
    "requirements": {
      "{alllore}": 2
    },
    "effects": {
      "article{alllore}a": 1
    },
    "link": {
      "results": {}
    }
  },
  "nothing": {
    "effects": {
      "restlessness": 1,
      "insight": -99
    }
  },
  "results": {
    "alt": {
      "results_three_insight": {},
      "results_two_insight": {},
      "results_one_insight": {}
    },
    "effects": {
      "insight": -99,
      "pigment": -1
    }
  },
  "results_three_insight": {
    "requirements": {
      "insight": 3
    },
    "effects": {
      "insight": -99,
      "pigment": -1
    },
    "deckeffect": {
      "writing_reputation": 3,
      "writing_results_random": 2
    }
  },
  "results_two_insight": {
    "requirements": {
      "insight": 2
    },
    "effects": {
      "insight": -99,
      "pigment": -1
    },
    "deckeffect": {
      "writing_reputation": 2,
      "writing_results_random": 1
    }
  },
  "results_one_insight": {
    "requirements": {
      "insight": 1
    },
    "effects": {
      "insight": -99,
      "pigment": -1
    },
    "deckeffect": {
      "writing_reputation": 1
    }
  }
}"""


book_elements = """{
  "book_$alllore": {
    "aspects": {
      "{alllore}": 6,
      "tool": 1,
      "text": 1
    }
  },
  "book_$lore_subvert": {
    "aspects": {
      "{lore}": 8,
      "{subverts}": 4,
      "tool": 1,
      "text": 1
    }
  },
  "almanac": {
    "isaspect": true
  },
  "almanac_$lore": {
    "aspects": {
      "{lore}": 10,
      "text": 1,
      "writing_almanac": 1,
      "secrethistories": 1
    },
    "lifetime": 180
  }
}"""


almanac_recipes = """{
  "$lore": {
    "requirements": {
      "writing_almanac": 1,
      "{lore}": 1
    },
    "linked": {
      "{lore}_c": { "chance": 10 },
      "{lore}_b": { "chance": 35 },
      "{lore}_a": {}
    },
    "craftable": true
  },
  "$lore_c": {
    "effects": {
      "influence{lore}e": 1
    },
    "linked": {
      "notoriety": { "chance": 10 },
      "fascination": { "chance": 35 },
      "dread": {}
    }
  },
  "$lore_b": {
    "effects": {
      "influence{lore}c": 1
    },
    "linked": {
      "fascination": { "chance": 10 },
      "dread": { "chance": 35 },
      "mystique": {}
    }
  },
  "$lore_a": {
    "effects": {
      "influence{lore}": 1
    },
    "linked": {
      "dread": { "chance": 10 },
      "mystique": { "chance": 35 },
      "safe": {}
    }
  },
  "safe": {
  },
  "mystique": {
    "effects": {
      "mystique": 1
    }
  },
  "dread": {
    "effects": {
      "dread": 1
    }
  },
  "fascination": {
    "effects": {
      "fascination": 1
    }
  },
  "notoriety": {
    "effects": {
      "notoriety": 1
    }
  }
}"""


def expand(node, replacements):
  try:
    if isinstance(node, (str,)):
      results = node
      for label, replace in replacements.items():
        results = re.sub("{{{}}}".format(label), replace, results)
      if re.search(r"{\w+}", results):
        return None
    elif isinstance(node, (list,)):
      results = []
      for item in node:
        results.append(expand(item, replacements))
    else:
      results = collections.OrderedDict()
      for key, value in node.items():
        for label, replace in replacements.items():
          key = re.sub("{{{}}}".format(label), replace, key)
        if re.search(r"{\w+}", key):
          return None

        match = EXPAND_RE.search(key)
        if match:
          label = match.group(1)
          for replace, additional in lookup[label].items():
            new_key = EXPAND_RE.sub(replace, key)
            new_replacements = copy.deepcopy(replacements)
            new_replacements[label] = replace
            new_replacements.update(additional)
            result = expand(value, new_replacements)
            if result is None:
              continue
            results[new_key] = result
        else:
          result = expand(value, replacements)
          if result is None:
            return None
          results[key] = result

    return results
  except AttributeError:
    return node


def rewrite_link(name, node, series):
  result = collections.OrderedDict()
  result["id"] = "_".join([series, name])
  result.update(node)
  if "chance" not in result:
    result["chance"] = 100
  return result


def rewrite(name, node, type, action, series):
  result = collections.OrderedDict()
  result["id"] = "_".join([series, name])
  if type == "recipes":
    result["actionId"] = action

  for key, value in node.items():
    if key.startswith("link"):
      result["linked"] = [rewrite_link(k, v, series)
                          for k, v in value.items()]
    elif key.startswith("alt"):
      result["alternativerecipes"] = [rewrite_link(k, v, series)
                                      for k, v in value.items()]
    else:
      result[key] = value

  if "label" not in result:
    result["label"] = "XXX " + name
  if "description" not in result:
    result["description"] = "XXX " + name

  if type == "recipes":
    if "startdescription" not in result:
      result["startdescription"] = "XXX " + name
    if "warmup" not in result:
      result["warmup"] = 1

  return result


def generate(data, type, action, series, filename):
  data = json.loads(data, object_pairs_hook=collections.OrderedDict)
  data = expand(data, {})
  output = []
  for key, value in data.items():
    output.append(rewrite(key, value, type, action, series))
  output = {type: output}
  with open(os.path.join(type, filename), "w") as f:
    json.dump(output, f, indent=2)
  print(json.dumps(output, indent=2))


if __name__ == "__main__":
  generate(writing_recipes, "recipes", "work", "writing",
           "quill_work_writing.json")
  generate(book_elements, "elements", "", "writing", "quill_books.json")
  generate(almanac_recipes, "recipes", "explore", "almanac",
           "quill_explore_almanac.json")
