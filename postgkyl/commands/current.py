import click
import numpy as np

from postgkyl.commands.util import verb_print
from postgkyl.data import GData
import postgkyl.tools as diag

@click.command(help='Accumulate current, sum over species of charge multiplied by flow')
@click.option('--qbym', '-q',
              default=False, show_default=True,
              help="Flag for multiplying by charge/mass ratio instead of just charge")
@click.option('--use', '-u',
              help='Specify a \'tag\' to apply to (default all tags).')
@click.option('--tag', '-t',
              default='current', show_default=True,
              help='Tag for the resulting current array')
@click.option('--label', '-l',
              default='J', show_default=True,
              help="Custom label for the result")
@click.pass_context
def current(ctx, **kwargs):
  verb_print(ctx, 'Starting current accumulation')
  data = ctx.obj['data']

  for dat in data.iterator(kwargs['use']):
    grid = dat.getGrid()
    outcurrent = np.zeros(dat.getValues().shape)
    grid, outcurrent = diag.accumulate_current(dat, kwargs['qbym'])
    dat.deactivate()
    out = GData(tag=kwargs['tag'],
                comp_grid=ctx.obj['compgrid'],
                label=kwargs['label'],
                meta=dat.meta)
    out.push(grid, outcurrent)
    data.add(out)
  #end
  verb_print(ctx, 'Finishing current accumulation')
#end
