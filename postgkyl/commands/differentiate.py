import click
import numpy as np

from postgkyl.data import GInterpModal, GInterpNodal
from postgkyl.commands.util import verb_print
from postgkyl.data import GData

@click.command(help='Interpolate a derivative of DG data on a uniform mesh')
@click.option('--basistype', '-b',
              type=click.Choice(['ms', 'ns', 'mo']),
              help='Specify DG basis')
@click.option('--polyorder', '-p', type=click.INT,
              help='Specify polynomial order')
@click.option('--interp', '-i', type=click.INT,
              help='Interpolation onto a general mesh of specified amount')
@click.option('--direction', '-d', type=click.INT,
              help='Direction of the derivative (default: calculate all)')
@click.option('--read', '-r', type=click.BOOL,
              help='Read from general interpolation file')
@click.option('--use', '-u',
              help='Specify a \'tag\' to apply to (default all tags).')
@click.option('--tag', '-t',
              help='Optional tag for the resulting array')
@click.option('--label', '-l',
              help="Custom label for the result")
@click.pass_context
def differentiate(ctx, **kwargs):
  verb_print(ctx, 'Starting differentiate')
  data = ctx.obj['data']

  basisType = None
  isModal = None
  if kwargs['basistype'] is not None:
    if kwargs['basistype'] == 'ms':
      basisType = 'serendipity'
      isModal = True
    elif kwargs['basistype'] == 'ns':
      basisType = 'serendipity'
      isModal = False
    elif kwargs['basistype'] == 'mo':
      basisType = 'maximal-order'
      isModal = True
    elif kwargs['basistype'] == 'mt':
      basisType = 'tensor'
      isModal = True
    #end
  #end
    
  for dat in data.iterator(kwargs['use']):
    if kwargs['basistype'] is None and dat.meta['basisType'] is None:
      ctx.fail(click.style("ERROR in interpolate: no 'basistype' was specified and dataset {:s} does not have required metadata".format(dat.getLabel()), fg='red'))
    #end
        
    if isModal or dat.meta['isModal']:
      dg = GInterpModal(dat,
                        kwargs['polyorder'], kwargs['basistype'], 
                        kwargs['interp'], kwargs['read'])
    else:
      dg = GInterpNodal(dat,
                        kwargs['polyorder'], basisType,
                        kwargs['interp'], kwargs['read'])
    #end
        
    if kwargs['tag']:
      out = GData(tag=kwargs['tag'],
                  label=kwargs['label'],
                  comp_grid=ctx.obj['compgrid'],
                  meta=dat.meta)
      grid, values = dg.differentiate(direction=kwargs['direction'])
      out.push(grid, values)
      data.add(out)
    else:
      dg.differentiate(direction=kwargs['direction'], overwrite=True)
    #end
  verb_print(ctx, 'Finishing differentiate')
#end
