import numpy as np
import matplotlib.pyplot as plt
import matplotlib.figure
import os.path

def _colorbar(obj, fig, ax, label=""):
    from mpl_toolkits.axes_grid1 import make_axes_locatable

    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="3%", pad=0.05)
    return fig.colorbar(obj, cax=cax, label=label)

def plot(grid, values, *args, figure=None, squeeze=False,
         streamline=False, quiver=False, contour=False,
         style=None, **kwargs):
    """Plots Gkyl data

    Unifies the plotting across a wide range of Gkyl applications. Can
    be used for both 1D an 2D data. Uses a proper colormap by default.

    Args:
    """
    if style is None:
        plt.style.use(os.path.dirname(os.path.realpath(__file__)) \
                      + "/postgkyl.mplstyle")
    else:
        plt.style.use(style)

    if isinstance(grid, list):
        numDims = len(grid)

        idx = []
        for d in range(numDims):
            if len(grid[d]) == 1:
                idx.append(d)
        if idx:
            grid = np.delete(grid, idx)
            values = np.squeeze(values, tuple(idx)) 
            numDims = len(grid)
    else:
        numDims = 1
        grid = grid[0]

    numComps = values.shape[-1]
    if streamline or quiver:
        step = 2
    else:
        step = 1
    idxComps = range(0, numComps, step)
    numComps = len(idxComps)

    if figure is None:
        fig = plt.figure()
    elif isinstance(figure, int):
        fig = plt.figure(figure)
    elif isinstance(figure, matplotlib.figure.Figure):
        fig = figure
    else:
        raise TypeError(("'fig' keyword needs to be one of "
                         "None (default), int, or MPL Figure"))
    if squeeze is False:
        if fig.axes:
            ax = fig.axes
            if numComs > len(ax):
                raise ValueError(
                    "Trying to plot into figure with not enough axes")
        else:
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
    else:
        if not fig.axes:
            plt.subplots(1, 1, num=fig.number)
    ax = fig.axes

    for comp in idxComps:
        if squeeze:
            cax = ax[0]
        else:
            cax = ax[comp]

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
        else:
            if numDims == 1:
                im, = cax.plot(grid[0], values[..., comp],
                               *args)
            elif numDims == 2:
                im = cax.pcolormesh(grid[0], grid[1],
                                    values[..., comp].transpose(),
                                    *args)
                cb = _colorbar(im, fig, cax)
            else:
                raise ValueError("{:d}D data not yet supported".
                                 format(numDims))
    plt.tight_layout()
    return im

   
    
    
