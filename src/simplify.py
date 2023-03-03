from readability import Document
import lxml

def simplify(html, document_title=""):
  document = Document(html)
  title = document.title()
  if title == "[no-title]":
      title = document_title
  tree = lxml.html.fromstring(document.summary())
  this_level: list[lxml.html] = [tree]
  while this_level:
      next_level = []
      for elem in this_level:
          if elem.tag not in ("figure", "a"):
              elem.attrib.clear()
          next_level.extend(elem)
      this_level = next_level
  while len(tree) == 1 and tree[0].tag != "p":
      tree = tree[0]
  text = f"<h1>{title}</h1></br>" + "".join([lxml.html.tostring(child).decode('utf-8') for child in tree]).replace("\n", "").replace("\r", "")
  return text
