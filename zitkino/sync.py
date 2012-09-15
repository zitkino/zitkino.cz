# -*- coding: utf-8 -*-


from zitkino.models import data


class StaticDataSynchronizer(object):
    """Inserts or updates static data defined in models."""

    def sync(self):
        """Perform synchronization."""
        for document in data:
            found = document.__class__.objects(slug=document.slug).first()
            if found:
                document.id = found.id
                document.save()  # update
            else:
                document.save()  # insert


class ShowtimesSynchronizer(object):
    """Synchronizes showtimes."""

    def sync(self):
        """Perform synchronization."""
        # def scrape_films(self):
        #     films = []
        #     for driver in self.drivers:
        #         films += list(driver().scrape())
        #     sorted_films = sorted(films, key=lambda film: film.date)
        #     filtered_films = [f for f in sorted_films if f.date >= self.today]
        #     return filtered_films
        pass
