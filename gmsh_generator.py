"""
Generates a Gmsh .geo file and calls Gmsh to produce a 2D mesh (.msh).

Configured below for a rectangular channel (lx × lw).
"""

import os
from subprocess import call


def gmsh_generator(outline,resolution):
    """
    Simple gmsh generator script
    :param outline:  array with boundary edge coordinates
    :param resolution:  resolution around these edges
    :return:
    """
    call(["mkdir", "mesh"])
    os.chdir("mesh")
    call(["rm", "mesh.msh"])

    f1 = open("mesh.geo","w")

    for i in range (len(outline)):
        f1.write('Point('+str(i+1)+') = { ' +"{}, {}, 0, {}".format(outline[i][0], outline[i][1],resolution[i]) + "}; \n")

    for i in range (len(outline)-1):
        f1.write('Line('+str(i+1)+') = { ' +"{}, {}".format(len(outline)-i, len(outline)-1-i,) + "}; \n")

    # Final connection
    f1.write('Line('+str(len(outline))+') = { ' +"{}, {}".format(1 , len(outline),) + "}; \n")
    f1.write('Line Loop(1) = {')
    for i in range (len(outline)):
        f1.write(str(i+1))
        if i < len(outline)-1:
            f1.write(", ")
    f1.write('};\n')

    f1.write('Plane Surface(6) = {1};\n')
    for i in range (len(outline)):
        f1.write('Physical Line('+str(i+1)+') = { '+"{}".format(i+1) + "}; \n")

    f1.write('Physical Surface(11) = {6};\n' )
    f1.write('Mesh.Algorithm = 6; // frontal=6, delannay=5, meshadapt=1')

    f1.close()

lx = 30000  # length of channel
lw = 2000   # width of channel
if __name__ == '__main__':

    # Example 1
    outline = [[0,0],[lx,0],[lx,lw],[0,lw]]  #insert here the boundary coordinates of the mesh

    # Example 2
    # outline = [[0,0],[140000,0],[140000,2500],[180000,2500],[180000,10000],[0,10000]] #here for the tetrix mesh
    resolution = [500 for i in range(len(outline))]       #initial resolution was 750
    print (len(outline), resolution)

    gmsh_generator(outline,resolution)

    call(["gmsh", "mesh.geo", "-2", "mesh.msh"])

    print("done")
