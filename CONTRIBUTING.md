# Contribution submission guidelines

## Language

- Commit messages, comments, identifiers, etc. should be in English.
- Discussions should be in Czech, as there is almost zero chance of strangers
  to be interested in contribution and the zitkino.cz site is in Czech and
  for Czechs.

*...takže znova:*

# Pravidla pro přispívání k projektu

## Jazyk

- Zprávy ke commitům, komentáře v kódu, identifikátory, apod. by měly být
  anglicky.
- Diskuse, popisy pull requestů apod. by měly být česky, protože je prakticky
  nulová šance, že by tento projekt zajímal i někoho jiného než česky mluvící,
  zvláště pokud je i celá stránka zitkino.cz pouze česky a pro Čechy.

## Kód

- Dodržuje se přísně PEP8, zapnout všechny
  [linty](https://pypi.python.org/pypi/pyflakes)...! Ve zvláštních případech
  lze lint potlačit komentářem `# NOQA`.
- Dodržuje se přísně limit na 80 znaků na řádek.
- Pokud zalamujeme kód, použijeme raději `()` než `\`.
- Hlavička souboru začíná vždy pro jistotu `# -*- coding: utf-8 -*-`.
- Importy jsou seřazeny od nejkratšího po nejdelší a seskupeny do těchto bloků:
  stdlib, externí knihovny, importy ze `zitkino`, importy z `.`

## Ostatní

Až mě něco napadne, dopíšu to sem :-)
