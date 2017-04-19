"""Module for parsing the sitemap of MFNF into a JSON file."""

import re

__all__ = ["parse_sitemap"]

class SitemapTransformer(object):
    """Transforms a JSON by changing its dictionaries."""

    def __call__(self, node):
        """Replacing all nodes in a sitemap tree.

        Not the most generic solution for a JSON transformer! :-)"""
        result = self.replace_node(node)
        result["children"] = [self(x) for x in node["children"]]

        return result

    def replace_node(self, oldnode):
        """Returns a new node."""
        pass

class ParseNodeCodes(SitemapTransformer):
    """Parses the specification of each node in a tree."""

    def replace_node(self, node):
        """Parses the code of the node and returns a new node with the parsed
        link to the article and the node's name.
        """
        if "code" not in node:
            return {}

        code = node["code"].strip()

        match = re.match(r"(.*)\{\{Symbol\|\d+%\}}", code)

        if match:
            code = match.group(1).strip()

        match = re.match(r"\[\[([^|\]]+)\|([^|\]]+)\]\]", code)

        if match:
            link = match.group(1)
            name = match.group(2)

            if not link.startswith("Mathe für Nicht-Freaks"):
                link = None
        else:
            name = code
            link = None

        return {"link": link, "name": name}

def create_empty_node(code, depth):
    """Returns a sitemap node with no children"""
    return {"code": code, "depth": depth, "children": []}

def yield_nodes(sitemap):
    """Generator for all node specifications in a sitemap. It yields tuples
    `(code, depth)` whereas `code` is a string representation of the node
    and `depth` is a number corresponding to the depth the node corresponds
    to.
    """
    max_headline_depth = 6
    headline_re = r"(={1,%s})(.*)\1" % max_headline_depth
    list_re = r"([*]+)(.*)"

    for line in sitemap.splitlines():
        for regex, depth_start in ((headline_re, 0),
                                   (list_re, max_headline_depth)):
            match = re.match(regex, line)

            if match:
                code = match.group(2).strip()
                depth = depth_start + len(match.group(1))

                yield create_empty_node(code, depth)

def insert_node(base, new_node):
    """Inserts a node at the right position."""
    if (len(base["children"]) > 0 and
            new_node["depth"] > base["children"][-1]["depth"]):
        insert_node(base["children"][-1], new_node)
    else:
        base["children"].append(new_node)

def parse_sitemap(sitemap):
    """Parse the sitemap and returns a JSON object of it.

    Arguments:
        sitemap -- content of the sitemap (a string)
    """
    root = {"children":[], "depth":0}

    for node in yield_nodes(sitemap):
        insert_node(root, node)

    root = ParseNodeCodes()(root)

    return root
