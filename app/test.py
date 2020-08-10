import datetime
def series():
    for i in range(1, 999):
        yield i


def make_get_or_rotate_series():
    today = datetime.date.today()
    current_series = series()

    def get_or_rotate_series(current_day=None):
        nonlocal today, current_series
        current_day = current_day if current_day else datetime.date.today()

        if today != current_day:
            today = current_day
            current_series = series()

        return current_series
    return get_or_rotate_series

get_series = make_get_or_rotate_series()
print(next(get_series()))
