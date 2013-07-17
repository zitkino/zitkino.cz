# -*- coding: utf-8 -*-


import lxml.html
from lxml import etree
from icalendar import Calendar

from . import parsers


class HtmlElement(lxml.html.HtmlElement):

    def text_content(self, whitespace=False):
        text = super(HtmlElement, self).text_content()
        if whitespace:
            return text
        return parsers.whitespace(text)

    def links(self):
        self.make_links_absolute()
        for element, attribute, link, pos in self.iterlinks():
            yield link

    def link(self):
        for link in self.links():
            return link
        return None

    def split(self, tag):
        elements = []
        for element in self:
            if element.tag.lower() == tag.lower():
                yield elements
                elements = []
            else:
                elements.append(element)


def html(text, base_url=None):
    lookup = etree.ElementDefaultClassLookup(element=HtmlElement)
    parser = etree.HTMLParser()
    parser.set_element_class_lookup(lookup)
    return lxml.html.fromstring(text, parser=parser, base_url=base_url)


def ical(text):
    return Calendar.from_ical(text)
