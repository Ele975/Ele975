CF_project

**Introduction**
This computational fabrication project tries to reproduce the one developed in the scientific paper 'Shadow Art' by Niloy J. Mitra, Mark Pauly.
A Python script is associated with Blender in order to create a shadow hull: a 3D figure of voxels which shape depends on the shape and number of images passed as input parameters as well as their angles.
The purpose of the shadow hull is to reproduce the shape of active pixels in each image, and if printed and a light is placed behind it, depending on the angle of the light it is possible to project the shadow of the input image on a wall or any other surfaces.

# run the application from terminal in the folder where the script is placed
blender --python script.py -- [nr_images] [angles] [filenames]

before running this command, it is required to install Blender and add it to the path (to use the command 'blender').

# 4 files example are provided in the repository called img1.txt, img2.txt, img3.txt, img4.txt
