class Filter:
    def __init__(self, tag: str, extra: dict = {}):
        self.tag = tag
        self.extra = extra

def apply_filters(filters: list[Filter], sp: any):
    filters.reverse()
    return _apply_filters(filters, sp, len(filters))

def _apply_filters(filters: list[Filter], sp: any, idx: int):
    filter = filters[idx - 1]
    res = sp.find_all(filter.tag, filter.extra)

    extracted = [x for x in res]
    
    if idx - 1 == 0 or len(extracted) == 0:
        return extracted
    
    to_return = []
    for x in extracted:
        next_filter_res = _apply_filters(filters, x, idx - 1)
        for y in next_filter_res:
            to_return.append(y)

    return to_return