from mecha.contrib.statistics import Analyzer
from beet import Context


def beet_default(ctx: Context):
    ctx.meta["stats"] = ctx.inject(Analyzer).stats
