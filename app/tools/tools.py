import time
import logging

logger = logging.getLogger(__name__)


def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        tz = te-ts
        if tz >= 0.05:
            logger.debug(f'{tz:.2f} sec, {method.__name__}')
        return result
    return timed
