import numpy as np
from typing import Union

# ---- Postgkyl imports ------------------------------------------------
from postgkyl.data import GData
from postgkyl.tools import _input_parser
# ----------------------------------------------------------------------

def transform_frame(in_f : Union[GData, tuple],
                    in_u : Union[GData, tuple],
                    c_dim : int,
                    out_f : GData = None) -> tuple:
  """Shift a distribution function to a different frame of reference.

  Shifsts the frame of reference for specified distribution function
  with a supplied bulk velocity (a direction of magnetic field will be
  added in future update).

  Args:
    in_f: Particle distribution function to be shifted.
    in_u: PBulk velocity.
    c_dim: Number of the configuration space dimensions.
    out_f: (Optional) GData to store output.

  Returns:
    A tuple of grid (which is itself a tuple of nupy arrays for each
    dimension) and a numpy array with values.
  """
  in_f_grid, in_f_values = _input_parser(in_f)
  _, u = _input_parser(in_u)
  v_dim = len(in_f_grid) - c_dim
  out_grid = np.meshgrid(*in_f_grid, indexing='ij')

  # There might be a better way to do this but hopefully such hardcoding
  # is ok in this instance -- PC
  if c_dim == 1:
    for v_idx in range(v_dim):
      nx = in_f_grid[0].shape[0]

      ext_u = np.zeros(nx)
      ext_u[:-1] += u[..., v_idx]
      ext_u[1:] += u[..., v_idx]
      ext_u[1:-1] = ext_u[1:-1] / 2

      for i in range(nx):
        out_grid[c_dim+v_idx][i, ...] += ext_u[i]
      #end
    #end
  elif c_dim == 2:
    for v_idx in range(v_dim):
      nx = in_f_grid[0].shape[0]
      ny = in_f_grid[0].shape[1]

      ext_u = np.zeros((nx, ny))
      ext_u[:-1, :-1] += u[..., v_idx]
      ext_u[1:, 1:] += u[..., v_idx]
      ext_u[1:-1, 1:-1] = ext_u[1:-1, 1:-1] / 2

      for i in range(nx):
        for j in range(ny):
          out_grid[c_dim+v_idx][i, j, ...] += ext_u[i, j]
        #end
      #end
    #end
  else:
    for v_idx in range(v_dim):
      nx = in_f_grid[0].shape[0]
      ny = in_f_grid[0].shape[1]
      nz = in_f_grid[0].shape[2]

      ext_u = np.zeros((nx, ny, nz))
      ext_u[:-1, :-1, :-1] += u[..., v_idx]
      ext_u[1:, 1:, 1:] += u[..., v_idx]
      ext_u[1:-1, 1:-1, 1:-1] = ext_u[1:-1, 1:-1, 1:-1] / 2

      for i in range(nx):
        for j in range(ny):
          for k in range(nz):
            out_grid[c_dim+v_idx][i, j, k, ...] += ext_u[i, j, k]
          #end
        #end
      #end
    #end
  #end

  if (out_f):
    out_f.push(out_grid, in_f_values)
  #end
  return out_grid, in_f_values
#end