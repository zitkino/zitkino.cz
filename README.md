
# Status: ARCHIV

Tento repozitář je archivní.

zitkino.cz teď jede z kódu na https://github.com/zitkino/zitkino (bez `.cz`), který má s tímto repozitářem společnou myšlenku a jméno, ale to je tak všechno.

# Žít kino (in Czech)

Nejpřehlednější program brněnských kin.

- [web](http://zitkino.cz)
- [Facebook](https://www.facebook.com/zitkino)
- [Twitter](https://twitter.com/zitkino)

## Instalace

Je potřeba MongoDB, které nainstalujete podle návodů na jejich webu
([Ubuntu](http://docs.mongodb.org/manual/tutorial/install-mongodb-on-debian-or-ubuntu-linux/),
[Fedora](http://docs.mongodb.org/manual/tutorial/install-mongodb-on-red-hat-centos-or-fedora-linux/)).

Dále je nutné mít LESS kompilátor - použijte originál napsaný v JavaScriptu:

```bash
$ sudo apt-get install -y node-less
```

No a potom už stačí jen nainstalovat Žít kino ze složky projektu:

```bash
$ git clone git@github.com:zitkino/zitkino.cz.git "zitkino.cz"
$ cd "zitkino.cz"
$ pip install -r requirements.txt
```

Aktualizace dat o filmových představeních se spouští jako:

```bash
$ python manage.py sync all
```

Vývojový server se spouští jako:

```bash
$ export ZITKINO_DEBUG=1
$ python manage.py runserver
```

## Konfigurace

Výchozí konfigurace se nachází v souboru `config.py`. Je parametrizovatelná přes
systémové proměnné, např. nastavením `export MONGOLAB_URI='mongodb://localhost/zitkino'`
změníme připojení k databázi. Je možné si udělat i celý vlastní konfigurační
soubor, který může přepsat výchozí hodnoty, a to nastavením `ZITKINO_CONFIG` na
cestu k vašemu konfiguračnímu souboru (viz
[dokumentace Flasku](http://flask.pocoo.org/docs/config/#configuring-from-files)).

## Pravidla pro přispívání

Žít kino je open source, což znamená, že se na něm může volně podílet kdokoli
má chuť. Pravidla pro přispívání k projektu jsou [zde](https://github.com/zitkino/zitkino.cz/blob/master/CONTRIBUTING.md).

## License: MIT

© 2012 Jan Javorek &lt;<a
href="mailto:mail&#64;honzajavorek.cz">mail&#64;honzajavorek.cz</a>&gt;

Žít kino je licencováno pod [MIT license](https://en.wikipedia.org/wiki/MIT_License).
