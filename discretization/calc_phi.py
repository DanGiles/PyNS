"""
Discretizes and solves generic transport equation.

Note:
  I hope that, one day, it will replace "calc_t".
"""

# Standard Python modules
from pyns.standard import *

# PyNS modules
from pyns.constants import *
from pyns.operators import *

from pyns.discretization.adj_n_bnds     import adj_n_bnds
from pyns.discretization.advection      import advection
from pyns.discretization.create_matrix  import create_matrix
from pyns.solvers                       import cg, cgs, bicgstab

# =============================================================================
def calc_phi(phi, uvwf, density, gamma, dt, dxyz, 
             obst = None, 
             src  = None):
# -----------------------------------------------------------------------------
    """
    Args:
      phi:     Generic unknown (from "create_unknown" function)
      uvwf:    a tuple with three staggered velocity components (where each
               component is created with "create_unknown" function.
      density: Three-dimensional matrix holding density times thermal
               capactity for all cells.
      dt:      Time step.
      dxyz:    Tuple holding cell dimensions in "x", "y" and "z" directions.
               Each cell dimension is a three-dimensional matrix.
      obst:    Obstacle, three-dimensional matrix with zeros and ones.
               It is zero in fluid, one in solid.
      src:     Right hand side term.

    Returns:
      none, but input argument phi is modified!
    """

    # Unpack tuple(s)
    dx, dy, dz = dxyz

    # Fetch the resolution
    r_phi = phi.val.shape

    # Discretize the diffusive part
    A_phi = create_matrix(phi, density/dt, gamma, dxyz, obst, NEUMANN)
    b_phi = zeros(r_phi)

    # The advective fluxes
    c_phi = advection(density, phi, uvwf, dxyz, dt, 'minmod')

    # Innertial term for enthalpy
    i_phi = phi.old * avg(phi.pos, density) * avg(phi.pos, dx*dy*dz) / dt

    # Handle external source
    if src == None:
        s_phi = zeros(r_phi)
    else:
        s_phi = src * avg(phi.pos, dx*dy*dz)

    # The entire source term
    f_phi = b_phi - c_phi + i_phi + s_phi
    
    # Solve for temperature
    phi.val[:] = bicgstab(A_phi, phi, f_phi, TOL)

    adj_n_bnds(phi)

    return  # end of function