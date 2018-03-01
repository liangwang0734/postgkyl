import numpy as np
import matplotlib.pyplot as plt
import matplotlib.figure
import os.path

def _colorbar(obj, fig, ax, label=""):
    from mpl_toolkits.axes_grid1 import make_axes_locatable

    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="3%", pad=0.05)
    return fig.colorbar(obj, cax=cax, label=label)

def plot(gdata, *args, figure=None, squeeze=False,
         streamline=False, quiver=False, contour=False,
         style=None, legend=True, labelPrefix='',
         xlabel=None, ylabel=None, title=None,
         logx=False, logy=False, color=None, fixedaxis=False,
         **kwargs):
    """Plots Gkyl data

    Unifies the plotting across a wide range of Gkyl applications. Can
    be used for both 1D an 2D data. Uses a proper colormap by default.

    Args:
    """
    # Load Postgkyl style
    if style is None:
        plt.style.use(os.path.dirname(os.path.realpath(__file__)) \
                      + "/postgkyl.mplstyle")
    else:
        plt.style.use(style)

    # Get the handles on the grid and values
    grid  = gdata.peakGrid()
    lower, upper = gdata.getBounds()
    values = gdata.peakValues()

    # Squeeze the data (get rid of "collapsed" dimensions)
    axLabel = ['$z_0$', '$z_1$', '$z_2$', '$z_3$', '$z_4$', '$z_5$']
    if isinstance(grid, list):
        numDims = len(grid)
        idx = []
        for d in range(numDims):
            if len(grid[d]) <= 1:
                idx.append(d)
        if idx:
            grid = np.delete(grid, idx)
            lower = np.delete(lower, idx)
            upper = np.delete(upper, idx)
            axLabel = np.delete(axLabel, idx)
            values = np.squeeze(values, tuple(idx)) 
            numDims = len(grid)
    else:
        numDims = 1
        grid = grid[0]
        lower = lower[0]
        upper = upper[0]
        axLabel = axLabel[0]

    numComps = values.shape[-1]
    if streamline or quiver:
        step = 2
    else:
        step = 1
    idxComps = range(0, numComps, step)
    numComps = len(idxComps)

    # Prepare the figure
    if figure is None:
        fig = plt.figure()
    elif isinstance(figure, int):
        fig = plt.figure(figure)
    elif isinstance(figure, str) or isinstance(figure, unicode):
        fig = plt.figure(int(figure))
    elif isinstance(figure, matplotlib.figure.Figure):
        fig = figure
    else:
        raise TypeError(("'fig' keyword needs to be one of "
                         "None (default), int, or MPL Figure"))
    # Prepare the axes
    if fig.axes:
        ax = fig.axes
        if squeeze is False and numComps > len(ax):
            raise ValueError(
                "Trying to plot into figure with not enough axes")
    else:
        if squeeze:
            plt.subplots(1, 1, num=fig.number)
            ax = fig.axes
            if xlabel is None:
                ax[0].set_xlabel(axLabel[0])
            else:
                ax[0].set_xlabel(xlabel)
            if ylabel is None:
                if numDims == 2:
                    ax[0].set_ylabel(axLabel[1])
            else:
                ax[0].set_ylabel(ylabel)
            if title is not None:
                ax[0].set_title(title, y=1.08)
        else:  # Not ideal but simple enough algorithm to split subplots
            sr = np.sqrt(numComps)
            if sr == np.ceil(sr):
                numRows = int(sr)
                numCols = int(sr)
            elif np.ceil(sr) * np.floor(sr) >= numComps:
                numRows = int(np.floor(sr))
                numCols = int(np.ceil(sr))
            else:
                numRows = int(np.ceil(sr))
                numCols = int(np.ceil(sr))
            if numDims == 2:
                plt.subplots(numRows, numCols,
                             sharex='all', sharey='all',
                             num=fig.number)
            else:
                plt.subplots(numRows, numCols,
                             sharex='all', num=fig.number)
            ax = fig.axes
            for comp in idxComps:
                if comp >= (numRows-1) * numCols:
                    if xlabel is None:
                        ax[comp].set_xlabel(axLabel[0])
                    else:
                        ax[comp].set_xlabel(xlabel)
                if comp % numCols == 0:
                    if ylabel is None:
                        if numDims == 2:
                            ax[comp].set_ylabel(axLabel[1])
                    else:
                        ax[comp].set_ylabel(ylabel)
                if comp < numCols and title is not None:
                    ax[comp].set_title(title, y=1.08)

    # Main plotting loop
    for comp in idxComps:
        if squeeze:
            cax = ax[0]
        else:
            cax = ax[comp]
        label='{:s}c{:d}'.format(labelPrefix, comp)
            
        # Special plots:
        if contour:  
            im = cax.contour(grid[0], grid[1],
                             values[..., comp].transpose(),
                             *args)
            cb = _colorbar(im, fig, cax)
        elif quiver:
            skip = int(np.max((len(grid[0]), len(grid[1])))//15)
            skip2 = int(skip//2)
            im = cax.quiver(grid[0][skip2::skip], grid[1][skip2::skip],
                            values[skip2::skip,
                                   skip2::skip,
                                   comp].transpose(),
                            values[skip2::skip,
                                   skip2::skip,
                                   comp+1].transpose())
        elif streamline:
            magnitude = np.sqrt(values[..., comp]**2 
                                + values[..., comp + 1]**2)
            im = cax.streamplot(coords[0], coords[1],
                                values[..., comp].transpose(),
                                values[..., comp + 1].transpose(),
                                *args,
                                color=magnitude.transpose())
            cb = _colorbar(im.lines, fig, cax)
        else:  # Basic plots:
            if numDims == 1:
                im = cax.plot(grid[0], values[..., comp],
                               *args, label=label)
            elif numDims == 2:
                im = cax.pcolormesh(grid[0], grid[1],
                                    values[..., comp].transpose(),
                                    *args)
                cb = _colorbar(im, fig, cax)
            else:
                raise ValueError("{:d}D data not yet supported".
                                 format(numDims))

        # Formatting
        cax.grid(True)
        # Legend
        if legend:
            if numDims == 1:
                cax.legend(loc=0)
            else:
                cax.text(0.03, 0.96, label,
                         bbox=dict(facecolor='w', edgecolor='w', alpha=0.8,
                                   boxstyle="round"),
                         verticalalignment='top',
                         horizontalalignment='left',
                         transform=cax.transAxes)

        if logx:
            cax.set_xscale('log')
        if logy:
            cax.set_yscale('log')
            
        # if color is not None:
        #     try:
        #         im.set_color(color)
        #     except:
        #         im.lines.set_color(color)
        #         im.arrows.set_color(color)

        if numDims == 1:
            plt.autoscale(enable=True, axis='x', tight=True)
        elif numDims == 2:
            if fixedaxis:
                cax.axis('image')

    for i in range(numComps, len(ax)):
        ax[i].axis('off')

    plt.tight_layout()
    return im

   
    
    
