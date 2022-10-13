import matplotlib.pyplot as plt

import click

import postgkyl.output.plot as gplot
from postgkyl.commands.util import vlog, pushChain

@click.command()
@click.option('--use', '-u', default=None,
              help="Specify the tag to plot.")
@click.option('--figure', '-f', default=None,
              help="Specify figure to plot in; either number or 'dataset'.")
@click.option('--squeeze', '-s', is_flag=True,
              help="Squeeze the components into one panel.")
@click.option('--subplots', '-b', is_flag=True,
              help="Make subplots from multiple datasets.")
@click.option('--nsubplotrow', 'nSubplotRow', type=click.INT,
              help="Manually set the number of rows for subplots.")
@click.option('--nsubplotcol', 'nSubplotCol', type=click.INT,
              help="Manually set the number of columns for subplots.")
@click.option('--transpose', is_flag=True,
              help="Transpose axes.")
@click.option('-c', '--contour', is_flag=True,
              help="Make contour plot.")
@click.option('--clevels', type=click.STRING,
              help="Specify levels for contours: either integer or start:end:nlevels")
@click.option('-q', '--quiver', is_flag=True,
              help="Make quiver plot.")
@click.option('-l', '--streamline', is_flag=True,
              help="Make streamline plot.")
@click.option('--sdensity', type=click.FLOAT,
              help="Control density of the streamlines.")
@click.option('--arrowstyle', type=click.STRING,
              help="Set the style for streamline arrows.")
@click.option('-g', '--group', type=click.Choice(['0', '1']),
              help="Switch to group mode.")
@click.option('-s', '--scatter', is_flag=True,
              help="Make scatter plot.")
@click.option('--markersize', type=click.FLOAT,
              help="Set marker size for scatter plots.")
@click.option('--linewidth', type=click.FLOAT,
              help="Set the linewidth.")
@click.option('--style',
              help="Specify Matplotlib style file (default: Postgkyl).")
@click.option('-d', '--diverging', is_flag=True,
              help="Switch to diverging color map.")
@click.option('--arg', type=click.STRING,
              help="Additional plotting arguments, e.g., '*--'.")
@click.option('-a', '--fix-aspect', 'fixaspect', is_flag=True,
              help="Enforce the same scaling on both axes.")
@click.option('--aspect', default=None,
              help="Specify the scaling ratio.")
@click.option('--logx', is_flag=True,
              help="Set x-axis to log scale.")
@click.option('--logy', is_flag=True,
              help="Set y-axis to log scale.")
@click.option('--logz', is_flag=True,
              help="Set values of 2D plot to log scale.")
@click.option('--xscale', default=1.0, type=click.FLOAT,
              help="Value to scale the x-axis (default: 1.0).")
@click.option('--yscale', default=1.0, type=click.FLOAT,
              help="Value to scale the y-axis (default: 1.0).")
@click.option('--zscale', default=1.0, type=click.FLOAT,
              help="Value to scale the z-axis (default: 1.0).")
@click.option('--vmax', default=None, type=click.FLOAT,
              help="Set maximal value of data for plots.")
@click.option('--vmin', default=None, type=click.FLOAT,
              help="Set minimal value of data for plots.")
@click.option('--xlim', default=None, type=click.STRING,
              help="Set limits for the x-coordinate (lower,upper)")
@click.option('--ylim', default=None, type=click.STRING,
              help="Set limits for the y-coordinate (lower,upper).")
@click.option('--globalrange', '-r', is_flag=True,
              help="Make uniform extends across datasets.")
@click.option('--legend/--no-legend', default=True,
              help="Show legend.")
@click.option('--force-legend', 'forcelegend', is_flag=True,
              help="Force legend even when plotting a single dataset.")
@click.option('--color', type=click.STRING,
              help="Set color when available.")
@click.option('-x', '--xlabel', type=click.STRING,
              help="Specify a x-axis label.")
@click.option('-y', '--ylabel', type=click.STRING,
              help="Specify a y-axis label.")
@click.option('--clabel', type=click.STRING,
              help="Specify a label for colorbar.")
@click.option('--title', type=click.STRING,
              help="Specify a title.")
@click.option('--save', is_flag=True,
              help="Save figure as PNG file.")
@click.option('--saveas', type=click.STRING, default=None,
              help="Name of figure file.")
@click.option('--dpi', type=click.INT, default=200,
              help="DPI (resolution) for output.")
@click.option('-e', '--edgecolors', type=click.STRING,
              help="Set color for cell edges to show grid outline (default: None)")
@click.option('--showgrid/--no-showgrid', default=True,
              help="Show grid-lines (default: True)")
@click.option('--xkcd', is_flag=True,
              help="Turns on the xkcd style!")
@click.option('--hashtag', is_flag=True,
              help="Turns on the pgkyl hashtag!")
@click.option('--show/--no-show', default=True,
              help="Turn showing of the plot ON and OFF (default: ON).")
@click.option('--figsize',
              help="Comma-separated values for x and y size.")
@click.option('--saveframes', type=click.STRING,
              help="Save individual frames as PNGS instead of an opening them")
@click.option('--jet', is_flag=True,
              help="Turn colormap to jet for comparison with literature.")
@click.pass_context
def plot(ctx, **kwargs):
  """Plot active datasets, optionally displaying the plot and/or saving
  it to PNG files. Plot labels can use a sub-set of LaTeX math
  commands placed between dollar ($) signs.
  """
  vlog(ctx, 'Starting plot')
  pushChain(ctx, 'plot', **kwargs)

  if kwargs['group'] is not None:
    kwargs['group'] = int(kwargs['group'])
  #end

  if kwargs['scatter']:
    kwargs['args'] = '.'
  #end

  if kwargs['jet']:
    click.echo(click.style(
      'WARNING: The \'jet\' colormap has been selected. This colormap is not perceptually uniform and seemingly creates features which do not exist in the data!',
      fg='yellow'))
  #end

  if kwargs['aspect']:
    kwargs['fixaspect'] = True
  #end
  
  kwargs['numAxes'] = None
  if kwargs['subplots']:
    kwargs['numAxes'] = 0
    kwargs['startAxes'] = 0
    for dat in ctx.obj['data'].iterator(kwargs['use']):
      kwargs['numAxes'] = kwargs['numAxes'] + dat.getNumComps()
    #end
    if kwargs['figure'] is None:
      kwargs['figure'] = 0
    #end
  #end

  dataset_fignum = False
  if kwargs['figure'] == 'dataset' or kwargs['figure'] == 'set' or kwargs['figure'] == 's':
    dataset_fignum = True
  #end

  if kwargs['globalrange']:
    vmin = float('inf')
    vmax = float('-inf')
    for dat in ctx.obj['data'].iterator(kwargs['use']):
      val = dat.getValues()*kwargs['zscale']
      if kwargs['logz']:
        val = np.log(val)
      #end
      if vmin > np.nanmin(val):
        vmin = np.nanmin(val)
      #end
      if vmax < np.nanmax(val):
        vmax = np.nanmax(val)
      #end
    #end
    if kwargs['vmin'] is None:
      kwargs['vmin'] = vmin
      if kwargs['logz']:
        kwargs['vmin'] = np.exp(vmin)
      #end
    #end
    if kwargs['vmax'] is None:
      kwargs['vmax'] = vmax
      if kwargs['logz']:
        kwargs['vmax'] = np.exp(vmax)
      #end
    #end
  #end
 
  fName = ''
  for i, dat in ctx.obj['data'].iterator(kwargs['use'], enum=True):
    if dataset_fignum:
      kwargs['figure'] = int(i)
    #end
    
    if ctx.obj['data'].getNumDatasets() > 1 or kwargs['forcelegend']:
      label = dat.getLabel()
    else:
      label = ''
    #end
    if kwargs['arg'] is not None:
      gplot(dat, kwargs['arg'], labelPrefix=label, 
            **kwargs)
    else:
      gplot(dat, labelPrefix=label,
            **kwargs)
    #end
    if kwargs['subplots']:
      kwargs['startAxes'] = kwargs['startAxes'] + dat.getNumComps()
    #end

    if (kwargs['save'] or kwargs['saveas']):
      if kwargs['saveas']:
        fName = kwargs['saveas']
      else:
        if fName != "":
          fName = fName + "_"
        #end
        if dat.file_name:
          fName = fName + dat.file_name.split('.')[0]
        else:
          fName = fName + 'ev_'+ctx.obj['labels'][s].replace(' ', '_')
        #end
      #end
    #end
    if (kwargs['save'] or kwargs['saveas']) and kwargs['figure'] is None:
      fName = str(fName)
      plt.savefig(fName, dpi=kwargs['dpi'])
      fName = ""
    #end

    if kwargs['saveframes']:
      fName = '{:s}_{:d}.png'.format(kwargs['saveframes'], i)
      plt.savefig(fName, dpi=kwargs['dpi'])
      kwargs['show'] = False
    #end
  #end
  if (kwargs['save'] or kwargs['saveas']) and kwargs['figure'] is not None:
    fName = str(fName)
    plt.savefig(fName, dpi=kwargs['dpi'])
  #end

  if kwargs['show']:
    plt.show()
  #end
  vlog(ctx, 'Finishing plot')
#end
