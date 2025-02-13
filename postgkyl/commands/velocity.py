import click

from postgkyl.commands.util import verb_print
from postgkyl.data import GData

@click.command()
@click.option('--density', '-d',
              default='density', show_default=True,
              help="Tag for density")
@click.option('--momentum', '-m',
              default='momentum', show_default=True,
              help="Tag for momentum")
@click.option('--tag', '-t',
              default='velocity', show_default=True,
              help='Tag for the result')
@click.option('--label', '-l',
              default='velocity', show_default=True,
              help="Custom label for the result")
@click.pass_context
def velocity(ctx, **kwargs):
  verb_print(ctx, 'Starting velocity')
    
  data = ctx.obj['data'] # shortcut
    
  for m0, m1 in zip(data.iterator(kwargs['density']),
                    data.iterator(kwargs['momentum'])):
    grid = m0.getGrid()        
    valsM0 = m0.getValues()
    valsM1 = m1.getValues()
            
    out = GData(tag=kwargs['tag'],
                comp_grid=ctx.obj['compgrid'],
                label=kwargs['label'],
                meta=m0.meta)
    out.push(grid, valsM1/valsM0)
    data.add(out)
  #end

  data.deactivateAll(tag=kwargs['density'])
  data.deactivateAll(tag=kwargs['momentum'])

  verb_print(ctx, 'Finishing velocity')
#end
