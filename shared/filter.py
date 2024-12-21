import logging

logger = logging.getLogger()

class Filter:
    def __init__(self, tag: str, extra: dict = {}):
        self.tag = tag
        self.extra = extra

    def __str__(self):
        return f"{self.tag},{self.extra}"
    
    def __repr__(self):
        return str(self)

def apply_filters(filters: list[Filter], sp: any):
    # TODO: Remove the .reverse() and walk the list forwards
    # The reason why the list is reversed, is because this used to be implemented with a stack.
    # That turned out not to work too well, so now we just keep track of an index that says how far along we are, 
    # and elemetns are not popped from the array (list). Obviously, this is no longer needed.
    filters.reverse()

    logger.debug(f"Working on: {filters}")
    return _apply_filters(filters, sp, len(filters))

def _apply_filters(filters: list[Filter], sp: any, idx: int):
    filter = filters[idx - 1]
    logger.debug(f"Applying filter: {filter}")

    res = sp.find_all(filter.tag, filter.extra)

    extracted = [x for x in res]
    
    if idx - 1 == 0 or len(extracted) == 0:
        logger.debug(f"Filter bottom for: {filters}")
        return extracted
    
    to_return = []
    for x in extracted:
        next_filter_res = _apply_filters(filters, x, idx - 1)
        for y in next_filter_res:
            to_return.append(y)

    return to_return