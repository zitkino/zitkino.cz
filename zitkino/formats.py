# -*- coding: utf-8 -*-


import lxml.html
from lxml import etree


class HtmlElement(lxml.html.HtmlElement):

    def text_content(self):
        return super(HtmlElement, self).text_content().strip()

    def links(self, base_url):
        self.make_links_absolute(base_url)
        for element, attribute, link, pos in self.iterlinks():
            yield link

    def link(self, base_url):
        for link in self.links(base_url):
            return link
        return None


def html(text):
    lookup = etree.ElementDefaultClassLookup(element=HtmlElement)

    parser = etree.HTMLParser()
    parser.set_element_class_lookup(lookup)

    return lxml.html.fromstring(text, parser=parser)
