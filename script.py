import bpy
import math
import bmesh
import sys

# assumption 1 -> light positions are fixed with angle of 90 degrees
# assumption 2 -> can add from 1 up to 4 images

# read command-line arguments
# 1 param -> number of images
# 2-5 param -> angles. Can be: 0,90,180,270, where 0 is positive x axis and the other in clockwise direction with steps of 90 degrees
print(sys.argv)
nr_img = sys.argv[4]
angles=[]
for i in range(int(nr_img)):
    angles.append(int(sys.argv[i + 5]))

img_name= []
for e in angles:
    if e == 0:
        img_name.append('img1')
    if e == 90:
        img_name.append('img2')
    if e == 180:
        img_name.append('img3')
    if e == 270:
        img_name.append('img4')




C = bpy.context
D = bpy.data


# clean scene from all objects and new collections
def clean():
    # Deselect all objects
    bpy.ops.object.select_all(action='DESELECT')

    # Delete all objects in the scene
    bpy.ops.object.select_by_type(type='MESH')
    bpy.ops.object.delete()
    bpy.ops.object.select_by_type(type='LIGHT')
    bpy.ops.object.delete()

    # Delete all materials
    for material in bpy.data.materials:
        bpy.data.materials.remove(material)

    # Delete all collections (except the default collection)
    for collection in bpy.data.collections:
        if collection.name != 'Collection':
            bpy.data.collections.remove(collection)



def create_light(pos):
    # create light
    light_data = bpy.data.lights.new(name="my-light-data", type='POINT')
    light_data.energy = 100
    # Create new object, pass the light data 
    light_object = bpy.data.objects.new(name="my-light", object_data=light_data)

    light_object.location = pos
    # Link object to collection in context
    bpy.data.collections['lights'].objects.link(light_object)


def create_img(img_name, img, dic, rot_y):
    temp = []
    #1 square of planes which represents 1 img
    for i in range(len(img)):
        for j in range(len(img[i])):
            loc = []
            # in px_plane insert corners of plane
            if img_name == 'img3':
                loc = [-20,j-4,i]
                if (img[i][j] == 1):
                    #upper left
                    temp.append([loc[0], loc[1]+0.5, loc[2]+0.5])
                    #upper right
                    temp.append([loc[0], loc[1]-0.5, loc[2]+0.5])
                    #bottom left
                    temp.append([loc[0], loc[1]+0.5, loc[2]-0.5])
                    #bottom right
                    temp.append([loc[0], loc[1]-0.5, loc[2]-0.5])

            elif img_name == 'img4':
                loc = [j-4,-20,i]
                if (img[i][j] == 1):
                    #upper left
                    temp.append([loc[0]-0.5, loc[1], loc[2]+0.5])
                    #upper right
                    temp.append([loc[0]+0.5, loc[1], loc[2]+0.5])
                    #bottom left
                    temp.append([loc[0]-0.5, loc[1], loc[2]-0.5])
                    #bottom right
                    temp.append([loc[0]+0.5, loc[1], loc[2]-0.5])

            elif img_name == 'img1':
                loc = [20,j-4,i]
                if (img[i][j] == 1):
                    #upper left
                    temp.append([loc[0], loc[1]-0.5, loc[2]+0.5])
                    #upper right
                    temp.append([loc[0], loc[1]+0.5, loc[2]+0.5])
                    #bottom left
                    temp.append([loc[0], loc[1]-0.5, loc[2]-0.5])
                    #bottom right
                    temp.append([loc[0], loc[1]+0.5, loc[2]-0.5])
            else:
                loc = [j-4,20,i]
                if (img[i][j] == 1):
                    #upper left
                    temp.append([loc[0]+0.5, loc[1], loc[2]+0.5])
                    #upper right
                    temp.append([loc[0]-0.5, loc[1], loc[2]+0.5])
                    #bottom left
                    temp.append([loc[0]+0.5, loc[1], loc[2]-0.5])
                    #bottom right
                    temp.append([loc[0]-0.5, loc[1], loc[2]-0.5])

            # Create planes as pixels
            bpy.ops.mesh.primitive_plane_add(size=1.0, location= loc)
            pixel = bpy.context.object
            pixel.name = "Pixel"
            pixel.rotation_euler[0] = math.radians(90)
            if rot_y != None and (img_name == 'img1' or img_name == 'img3'):
                pixel.rotation_euler[2] = rot_y

            dic[i,j] = loc


            # add color for active pixels (black)
            material = bpy.data.materials.new(name="PixelMaterial")
            if img[i][j] == 0:
                material.diffuse_color = (1, 1, 1,0)  
            else:
                material.diffuse_color = (0, 0, 0,0)  
            pixel.data.materials.append(material) 

    px_plane_coord[img_name] = temp






# Create light rays -> use a mesh and attach it to an object, then insert in collection
# create a ray for each pixel center

def ray_light(name, dic, pos_light, corners):
            # light position
            init_coord = [pos_light[0], pos_light[1], pos_light[2]]
            # boundary piyel positions
            end_coord_bl = [dic[(0,0)][0],dic[(0,0)][1],dic[(0,0)][2]]
            end_coord_br = [dic[(0,img_size-1)][0],dic[(0,img_size-1)][1],dic[(0,img_size-1)][2]]
            end_coord_tl = [dic[(img_size-1,0)][0],dic[(img_size-1,0)][1],dic[(img_size-1,0)][2]]
            end_coord_tr = [dic[(img_size-1, img_size-1)][0],dic[(img_size-1, img_size-1)][1],dic[(img_size-1, img_size-1)][2]]

            end_coords = [end_coord_bl, end_coord_br, end_coord_tl, end_coord_tr]

            info = [name,init_coord]

            # create lines from the light point to the center of each pixel. Increase then the length of the lines to know the space
            # to build the hull
            for i in range(len(end_coords)):
                end_point =increase_line_length(init_coord, end_coords[i],30)
                info.append(end_point)
                verts = [(init_coord), (end_point[0], end_point[1], end_point[2])]
                edges = [(0, 1)]
                ray_light = bpy.data.meshes.new('ray' + str(name))
                ray_light.from_pydata(verts, edges, [])
                ray_light.update()
                mesh_obj = bpy.data.objects.new('obj_' + str(name), ray_light)
                lights.objects.link(mesh_obj)

            corners.append(info)


def increase_line_length(start_point, end_point, length_increase):
    # Calculate direction vector of the line
    direction = [(end_point[i] - start_point[i]) for i in range(3)]
    
    # Calculate current length of the line
    current_length = math.sqrt(sum([direction[i] ** 2 for i in range(3)]))
    
    # Calculate scaling factor to increase the line length
    scaling_factor = (current_length + length_increase) / current_length
    
    # Scale direction vector
    scaled_direction = [direction[i] * scaling_factor for i in range(3)]
    
    # Calculate new end point of the line
    new_end_point = [(start_point[i] + scaled_direction[i]) for i in range(3)]
    
    return new_end_point


# fins total hull square space in the middle of all images
def hull_space():
    # hull space of 20x20x60 (to be sure because of projection) -> used to visualise entire hull space
    # loc=[0,0,5]
    # bpy.ops.mesh.primitive_cube_add(size=20.0, location= loc)

    # voxels of size 1
    for i in range(20): 
        for j in range(20):
            for k in range(20):
                loc = [10-i, 10-j, k-5]
                cubes_coord.append(loc)
                # for each voxel create ray from voxel center to each light center
                for i in range(len(pos_lights)):
                    ray = [loc[0], loc[1], loc[2], pos_lights[i][0] - loc[0], pos_lights[i][1] - loc[1], pos_lights[i][2] - loc[2]]
                    cubes_ray.append(ray)


# define active voxels checking for each voxel ray the point of intersection with each image, and having all corner coordinates of each pixel, check within which pixel is it and store True if is in an active pixel
# if the cube ray intersect an active pixel in each image, set it to true
def active_voxels(epsilon=1e-6):
    # for each ray, for each active corner pixel positions check if they intersect
    for i in range(len(cubes_ray)):
        origin = [cubes_ray[i][0], cubes_ray[i][1], cubes_ray[i][2]]
        ray = [cubes_ray[i][3],cubes_ray[i][4],cubes_ray[i][5]]
        # insert names of images for which the voxel ray intersect an active pixel -> it is possible to have more rays that insersect the same pixel, then store names to ensure ray intersect at least one active pixel for each img
        active_check = []
        # cube raz doesn't intesect all valid pixels in all images
        invalid = False

        for k in px_plane_coord.keys():
            # random point on plane to get point of intersection if any
            ref_px = px_plane_coord[k][0]
            # get normal of plane knowing the name of the image
            normal = []
            img_name = None
            if k == 'img1' or k == 'img3':
                img_name = 'img13'
                # image on x axis
                normal = [1,0,0]
            else:
                img_name = 'img24'
                #image on y axis
                normal = [0,1,0]
            # check if voxel ray intersect image 
            # dot product between plane normal and ray cube, intersect if > epsilon, otherwise they're parallel
            dot = (ray[0] * normal[0]) +(ray[1] * normal[1]) + (ray[2] * normal[2])
            if dot > epsilon:
                # find point of intersection
                # difference between point on plane and origin of ray
                w = [ref_px[0] - origin[0], ref_px[1] - origin[1], ref_px[2] - origin[2]]
                # distance
                t = ((w[0] * norma[0]) + (w[1] * normal[1]) + (w[2] * normal[2]))/dot
                # general formula for ray -> td + o
                td = (t[0] * ray[0]) + (t[1] * ray[1]) + (t[2] * ray[2])

                point = [td[0] + origin[0], td[1] + origin[1], td[2] + origin[2]]

                # check in which pixel the intersection point is, set one value True for the cube if active pixel
                for i in range(px_plane_coord[k]):
                    # pl_plane_coord[img] = [[corner_ul1,corner_ur1,corner_bl1,corner_br1], [corner_ul2,corner_ur2,corner_bl2,corner_br2], ...]
                        # check z coordinate bottom and up boundary
                        if point[2] < px_plane_coord[k][i][0][2] and point[2] >= pl_plane_coord[k][i][2][2]:
                            if img_name == 'img13':
                                # check y coordinate left and right boundary
                                if point[1] < px_plane_coord[k][i][1][1] and point[1] >= px_plane_coord[k][i][0][1]:
                                    # append name of img the active pixel belongs to
                                    active_check.append(img_name)
                            else:
                                if point[0] < px_plane_coord[k][i][1][0] and point[1] >= px_plane_coord[k][i][0][0]:
                                    active_check.append(img_name)
        # check that ray intersect valid pixels of all images, if not set invalid to false and go to next cube ray
        for e in img_names:
            if e not in active_check:
                invalid = True
                break
        if invalid:
            continue
        # else:
            # create activ voxel





                                









                


            
            

            

    
    
            






# clean scene removing all collections and objects before working
clean()

# collection for light rays
lights = bpy.data.collections.new('lights')
bpy.context.scene.collection.children.link(lights)
    
# pixel input images -> example
img_size = 9
img1 = [[0 for i in range(img_size)] for j in range(img_size)]
img2 = [[0 for i in range(img_size)] for j in range(img_size)]
img3 = [[0 for i in range(img_size)] for j in range(img_size)]
# img4 = [[0 for i in range(img_size)] for j in range(img_size)]

#square NEED TO CHANGE
for i in range(img_size):
    for j in range(img_size):
        if i >= 2 and i < 8:
            if j >= 2 and j < 8:
                img1[i][j] = 1
                img2[i][j] = 1


# coordinates of all lights depending on angle
pos_lights = []

for i in range(len(angles)):
    if angles[i] == 0:
        pos_lights.append([50,0,4])
    elif angles[i] == 90:
        pos_lights.append([0,50,4])
    elif angles[i] == 180:
        pos_lights.append([-50,0,4])
    else:
        pos_lights.append([0,-50,4])


# call functions

# dictionary containing as key the i,j coordinates of the pixels and as value their cartesian coordinates
dic_img1 = {}
dic_img2 = {}
dic_img3 = {}
dic_img4 = {}

# using img name as key, contains all corners coordinates of each pixel of each img
px_plane_coord = {}
# for i in range(nr_img):
create_img('img1',img1,dic_img1, math.radians(90))
create_img('img2',img2,dic_img2,  math.radians(90))
create_img('img3',img3,dic_img3,  math.radians(90))

for i in range(len(angles)):
    create_light(pos_lights[i])


# array containing name of the image the rays belong to and starting_point(light), ending_point1,ending_point2... of corner pixels for each img (4 for each img)
corners_coord = []

ray_light('img1', dic_img1, pos_lights[0], corners_coord)
ray_light('img2',dic_img2, pos_lights[1], corners_coord)
ray_light('img3',dic_img3, pos_lights[2], corners_coord)

# coordinates of voxels
cubes_coord=[]
# for each voxel rays from voxel center to each light source. The first 3 elements contains the origin of the ray (cube coordinates)
cubes_ray = []
hull_space()

# cubes which rays passes through active pixels for each image
active_cubes = {}
