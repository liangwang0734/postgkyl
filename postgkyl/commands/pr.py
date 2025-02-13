import click
import numpy as np
np.set_printoptions(precision=16)

from postgkyl.commands.util import verb_print

@click.command(help='Print the data')
@click.option('--use', '-u',
              help='Specify a \'tag\' to apply to (default all tags).')
@click.option('--grid', '-g', is_flag=True,
              help='Print grid instead of values')
@click.pass_context
def pr(ctx, **kwargs):
  verb_print(ctx, 'Starting pr')
  data = ctx.obj['data']
    
  for dat in data.iterator(kwargs['use']):
    if kwargs['grid']:
      grid = dat.getGrid()
      for g in grid:
        click.echo(g)
      #end
    else:
      click.echo(dat.getValues().squeeze())
    #end
  #end

  verb_print(ctx, 'Finishing pr')
#end
