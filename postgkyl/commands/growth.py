import os
import click
import numpy as np
import matplotlib.pyplot as plt

from postgkyl.commands.util import verb_print
from postgkyl.tools.growth import fitGrowth, exp2
from postgkyl.data import GData

#---------------------------------------------------------------------
#---- Growth ---------------------------------------------------------
@click.command()
@click.option('--use', '-u',
              help='Specify a \'tag\' to apply to (default all tags).')
@click.option('-g', '--guess',
              help='Specify comma-separated initial guess')
@click.option('--minn', type=click.INT,
              help='Set minimal number of points to fit')
@click.option('-d', '--dataset', is_flag=True,
              help='Create a new dataset with fitted exponential')
@click.option('-i', '--instantaneous', is_flag=True,
              help='Plot instantaneous growth rate vs time')
@click.option('--dir', type=click.INT,
              help='Choose direction for multi-D data.')
@click.option('--tag', '-t',
              help='Optional tag for the resulting array')
@click.option('--label', '-l',
              help="Custom label for the result")
@click.pass_context
def growth(ctx, **kwargs):
  """Attempts to compute growth rate (i.e. fit e^(2x)) from DynVector
  data, typically an integrated quantity like electric or magnetic
  field energy.
  """
  verb_print(ctx, 'Starting growth')
  data = ctx.obj['data']

  for dat in data.iterator(kwargs['use']):
    time = dat.getGrid()
    values = dat.getValues()
    num_dims = len(np.array(values.shape).squeeze())

    growth_rates = np.zeros(1)
    ks = np.zeros(1)
    if num_dims == 2:
      if kwargs['dir'] == 0:
        growth_rates = np.zeros(values.shape[1])
        ks = np.zeros(values.shape[1])
      elif kwargs['dir'] == 1:
        growth_rates = np.zeros(values.shape[0])
        ks = np.zeros(values.shape[0])
      #end
    #end

    for idx in range(len(growth_rates)):
      p0 = kwargs['guess']
      if kwargs['guess']:
        guess = kwargs['guess'].split(',')
        p0 = (float(guess[0]), float(guess[1]))
      #end

      x = time[0]
      if kwargs['dir'] == 1:
        x = time[1]

      y = values[..., 0].squeeze()
      if kwargs['dir'] == 0:
        y = values[:, idx, 0].squeeze()
      elif kwargs['dir'] == 1:
        y = values[idx, :, 0].squeeze()
      #end

      bestParams, bestR2, bestN = fitGrowth(x, y,
                                            minN=kwargs['minn'],
                                            p0=p0)

      if kwargs['dataset']:
        out = GData(tag='growth',
                    label='Fit',
                    comp_grid=ctx.obj['compgrid'],
                    meta=dat.meta)
        t = 0.5*(time[0][:-1] + time[0][1:])
        out_val = exp2(t, *bestParams)
        out.push([time[0]], out_val[..., np.newaxis])
        data.add(out)
      #end

      if kwargs['instantaneous']:
        verb_print(ctx, 'growth: Plotting instantaneous growth rate')
        gammas = []
        for i in range(1,len(time[0])-1):
          gamma = (values[i+1,0] - values[i-1,0])/(2*values[i,0]*(time[0][i+1] - time[0][i-1]))
          gammas.append(gamma)

          plt.style.use(os.path.dirname(os.path.realpath(__file__)) \
                        + "/../output/postgkyl.mplstyle")
          fig, ax = plt.subplots()
          ax.plot(time[0][1:-1], gammas)
          #ax.set_autoscale_on(False)
          ax.grid(True)
          plt.show()
        #end
      #end

      growth_rates[idx] = bestParams[1]
      ks[idx] = idx
    #end

    if kwargs['tag']:
      out = GData(tag=kwargs['tag'],
                  label=kwargs['label'],
                  comp_grid=ctx.obj['compgrid'],
                  meta=dat.meta)
      out.push([ks], growth_rates[..., np.newaxis])
      data.add(out)
    #end
  #end
  verb_print(ctx, 'Finishing growth')
#end
