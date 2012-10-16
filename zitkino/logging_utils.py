# -*- coding: utf-8 -*-


import times
import logging

from zitkino.models import Action, LogRecord


class _ContextInjector(object):

    def __init__(self, context_items, logger):
        self.context_items = context_items
        self.logger = logger

    def _inject(self, kwargs):
        extra = kwargs.get('extra', {})
        extra.update(self.context_items)
        kwargs['extra'] = extra
        return kwargs

    def debug(self, *args, **kwargs):
        self.logger.debug(*args, **self._inject(kwargs))

    def info(self, *args, **kwargs):
        self.logger.info(*args, **self._inject(kwargs))

    def warning(self, *args, **kwargs):
        self.logger.warning(*args, **self._inject(kwargs))

    def error(self, *args, **kwargs):
        self.logger.error(*args, **self._inject(kwargs))

    def critical(self, *args, **kwargs):
        self.logger.critical(*args, **self._inject(kwargs))

    def log(self, *args, **kwargs):
        self.logger.log(*args, **self._inject(kwargs))

    def exception(self, *args, **kwargs):
        self.logger.exception(*args, **self._inject(kwargs))


class Context(dict):

    def open(self):
        return self

    def __enter__(self):
        return self.open()

    def logger(self, name):
        logger = logging.getLogger(name)
        return _ContextInjector(self.viewitems(), logger)

    def close(self):
        self.clear()

    def __exit__(self, type, value, traceback):
        self.close()


class ActionContext(Context):

    def __init__(self, name, *args, **kwargs):
        self.name = name
        super(ActionContext, self).__init__(*args, **kwargs)

    def _start_action(self, name):
        action = Action(name=name)
        action.start()
        action.save()
        return action

    def open(self):
        self['action'] = self._start_action(self.name)
        return super(ActionContext, self).open()

    def _finish_action(self, action):
        if action:
            action.finish()
            action.save()

    def close(self):
        self._finish_action(self['action'])
        del self['action']
        super(ActionContext, self).close()


class Handler(logging.Handler):

    _attrs_mapper = {
        # filtering out
        'threadName': None, 'thread': None, 'created': None,
        'relativeCreated': None, 'levelno': None, 'filename': None,
        'funcName': None, 'module': None, 'msg': None, 'args': None,
        'levelname': None, 'msecs': None, 'action': None,
        'lineno': None, 'pathname': None,

        # renaming
        'name': 'logger_name',
    }

    def _filter_value(self, value):
        return value

    def _extract_context(self, record):
        context = {}
        mapper = self._attrs_mapper

        for attr, value in vars(record).items():
            value = self._filter_value(value)
            if attr in mapper:
                # in mapper, search for it's new name
                new_name = mapper[attr]
                if new_name:
                    # save under it's new name
                    context[new_name] = value
                # else it's None, which means it should
                # be filtered out
            else:
                # no definition in mapper for this one,
                # keep it under it's original name
                context[attr] = value
        return context

    def emit(self, record):
        if record.name.startswith('zitkino'):
            print vars(record)
            print getattr(record, 'action', None)

            r = LogRecord()
            r.action = getattr(record, 'action', None)
            r.level = getattr(record, 'levelname', None)
            r.message = self.format(record)
            r.context = self._extract_context(record)
            r.happened_at = times.now()
            r.save()


def init_app(app):
    level = logging.DEBUG if app.debug else logging.INFO

    logger = logging.getLogger()
    logger.setLevel(level)

    format = '%(message)s'
    handler = Handler()
    handler.setFormatter(logging.Formatter(format))
    logger.addHandler(handler)

    format = '%(levelname)s\t%(name)s\t%(message)s'
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(format))
    logger.addHandler(handler)
