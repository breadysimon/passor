import datetime

from jinja2 import contextfunction

from passor.data_gen import DataGen

d = DataGen()


@contextfunction
def cf_today(context):
    return datetime.datetime.now().strftime('%Y-%m-%d')


@contextfunction
def cf_delta_today(context, days):
    ddd = datetime.timedelta(days=days)
    return (datetime.datetime.now() + ddd).strftime('%Y-%m-%d')


@contextfunction
def cf_fake(context, *args, **kwargs):
    return d.gen(*args, **kwargs)
