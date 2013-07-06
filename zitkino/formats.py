# -*- coding: utf-8 -*-


import lxml.html
from lxml import etree
from icalendar import Calendar


class HtmlElement(lxml.html.HtmlElement):

    def text_content(self):
        return super(HtmlElement, self).text_content().strip()

    def links(self):
        self.make_links_absolute()
        for element, attribute, link, pos in self.iterlinks():
            yield link

    def link(self):
        for link in self.links():
            return link
        return None


def html(text, base_url=None):
    lookup = etree.ElementDefaultClassLookup(element=HtmlElement)
    parser = etree.HTMLParser()
    parser.set_element_class_lookup(lookup)
    return lxml.html.fromstring(text, parser=parser, base_url=base_url)


class XmlElement(etree.ElementBase):

    def child_text_content(self, tag, namespaces=None):
        return self.xpath('string(.//' + tag + '/text())',
                          namespaces=namespaces)


def xml(text, base_url=None):
    lookup = etree.ElementDefaultClassLookup(element=XmlElement)
    parser = etree.XMLParser(recover=True, remove_comments=True,
                             remove_pis=True)
    parser.set_element_class_lookup(lookup)
    return etree.fromstring(text, parser=parser, base_url=base_url)


def ical(text):
    return Calendar.from_ical(text)
