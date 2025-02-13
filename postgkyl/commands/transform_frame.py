import click

# ---- Postgkyl imports ------------------------------------------------
from postgkyl.commands.util import verb_print
from postgkyl.data import GData
from postgkyl.tools import transform_frame
# ----------------------------------------------------------------------

@click.command(help='Compose PKPM Laguerre coefficients together.')
@click.option('--distribution', '-f', type=click.STRING, prompt=True,
              help='Specify the PKPM distribution function.')
@click.option('--bulk', '-u', type=click.STRING, prompt=True,
              help='Specify the PKPM moments.')
@click.option('--cdim', '-c', type=click.INT, prompt=True,
              help='Specify the number of configuration space dimensions.')
@click.option('--tag', '-t',
              help='Optional tag for the resulting array')
@click.option('--label', '-l',
              help="Custom label for the result")
@click.pass_context
def transformframe(ctx, **kwargs):
  verb_print(ctx, 'Starting transformframe')
  data = ctx.obj['data']

  for f, bulk in zip(data.iterator(kwargs['distribution']),
                    data.iterator(kwargs['bulk'])):
    if kwargs['tag']:
      out = GData(tag=kwargs['tag'],
                  label=kwargs['label'],
                  comp_grid=ctx.obj['compgrid'],
                  meta=f.meta)
      transform_frame(f, bulk, kwargs['cdim'], out)
    else:
      transform_frame(f, bulk, kwargs['cdim'], f)
    #end
  #end
  verb_print(ctx, 'Finishing transformframe')
#end