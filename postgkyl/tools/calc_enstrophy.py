#!/usr/bin/env python
# coding: utf-8

import numpy as np
import postgkyl


def calc_enstrophy(info_file, initFrame, finalFrame):
    #input from the info_matrix containing rho, px, py, pz, and energy
    #calculates the enstrophy in 2D in the general form (integral of the magnitude squared of the curl of the velocity
    #over the surface) and incompressible form (integral of the magnitude of the gradient of velocity squared over the
    #surface)
    #only for 3D
    #compares the two results and determines if incompressibility is conserved
    
    #get the matrices: rho, px, py, pz
    frame = postgkyl.GData(info_file + str(initFrame) + '.bp')
    data = frame.getValues()
    grid = frame.getGrid()
    dx = grid[0][1]-grid[0][0]
    dy = grid[1][1]-grid[1][0]
    dz = grid[2][1]-grid[2][0]

    r = 0
    enstrophy = np.zeros((1, (finalFrame-initFrame+1)))
    incom_enstrophy = enstrophy
    incom_mag = np.zeros((len(data[:,0,0,0]),len(data[0,:,0,0]),len(data[0,0,:,0])))

    for i in range(initFrame, finalFrame+1):
        frame = postgkyl.GData(info_file + "%d.bp" %i)
        data = frame.getValues()

        rho = data[:,:,:,0]
        px = data[:,:,:,1]
        py = data[:,:,:,2]
        pz = data[:,:,:,3]
        #calculate ux, uy, uz
        u = px/rho
        v = py/rho
        w = pz/rho
        #calculate the gradient
        u_gradient = (np.gradient(u, dx, dy, dz, edge_order=2))
        v_gradient = (np.gradient(v, dx, dy, dz, edge_order=2))
        w_gradient = (np.gradient(w, dx, dy, dz, edge_order=2))
        A = [u_gradient, v_gradient, w_gradient]
        A = np.array(A)
        
        u_x = np.array(u_gradient[0])
        u_y = np.array(u_gradient[1])
        u_z = np.array(u_gradient[2])
        v_x = np.array(v_gradient[0])
        v_y = np.array(v_gradient[1])
        v_z = np.array(v_gradient[2])
        w_x = np.array(w_gradient[0])
        w_y = np.array(w_gradient[1])
        w_z = np.array(w_gradient[2])
        
        #find enstrophy in terms of curl magnitude squared integrand
        curl_mag =((w_y-v_z)**2 + (u_z-w_x)**2 + (v_x - u_y)**2)
        enstrophy[0,r] = (np.sum(curl_mag, axis=(0,1,2))*dx*dy*dz)
        
        #find incompressible enstrophy magnitude squared integrand
        for c in range(0, (len(u[:,0,0])-1)):
            for j in range(0, (len(u[0,:,0])-1)):
                for k in range(0, (len(u[0,0,:])-1)):
                    incom_mag[c,j,k] = np.trace(np.transpose(A[:,:,c,j,k])*A[:,:,c,j,k])*rho[c,j,k]
        incom_enstrophy[0,r] = (np.sum(incom_mag, axis=(0,1,2))*dx*dy*dz)
        r += 1
      
    return enstrophy, incom_enstrophy; 
