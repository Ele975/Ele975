import bpy
import math
import bmesh
import sys

# assumption 1 -> light positions are fixed with angle of 90 degrees
# assumption 2 -> can add from 1 up to 4 images

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
    empty = True
    px_plane_coord[img_name] = []
    #1 square of planes which represents 1 img
    for i in range(len(img)):
        for j in range(len(img[i])):
            loc = []
            # in px_plane insert corners of plane
            if img_name == 'img3':
                loc = [-20,j-4,i]
                if (img[i][j] == 1):
                    empty = False
                    #upper left
                    temp.append([loc[0], loc[1], loc[2],loc[0], loc[1]+0.5, loc[2]+0.5])
                    #upper right
                    temp.append([loc[0], loc[1], loc[2],loc[0], loc[1]-0.5, loc[2]+0.5])
                    #bottom left
                    temp.append([loc[0], loc[1], loc[2],loc[0], loc[1]+0.5, loc[2]-0.5])
                    #bottom right
                    temp.append([loc[0], loc[1], loc[2],loc[0], loc[1]-0.5, loc[2]-0.5])

            elif img_name == 'img4':
                loc = [j-4,-20,i]
                if (img[i][j] == 1):
                    empty = False
                    #upper left
                    temp.append([loc[0], loc[1], loc[2],loc[0]-0.5, loc[1], loc[2]+0.5])
                    #upper right
                    temp.append([loc[0], loc[1], loc[2],loc[0]+0.5, loc[1], loc[2]+0.5])
                    #bottom left
                    temp.append([loc[0], loc[1], loc[2],loc[0]-0.5, loc[1], loc[2]-0.5])
                    #bottom right
                    temp.append([loc[0], loc[1], loc[2],loc[0]+0.5, loc[1], loc[2]-0.5])

            elif img_name == 'img1':
                loc = [20,j-4,i]
                if (img[i][j] == 1):
                    empty = False
                    #upper left
                    temp.append([loc[0], loc[1], loc[2],loc[0], loc[1]-0.5, loc[2]+0.5])
                    #upper right
                    temp.append([loc[0], loc[1], loc[2],loc[0], loc[1]+0.5, loc[2]+0.5])
                    #bottom left
                    temp.append([loc[0], loc[1], loc[2],loc[0], loc[1]-0.5, loc[2]-0.5])
                    #bottom right
                    temp.append([loc[0], loc[1], loc[2],loc[0], loc[1]+0.5, loc[2]-0.5])
            else:
                loc = [j-4,20,i]
                if (img[i][j] == 1):
                    empty = False
                    #upper left
                    temp.append([loc[0], loc[1], loc[2],loc[0]+0.5, loc[1], loc[2]+0.5])
                    #upper right
                    temp.append([loc[0], loc[1], loc[2],loc[0]-0.5, loc[1], loc[2]+0.5])
                    #bottom left
                    temp.append([loc[0], loc[1], loc[2],loc[0]+0.5, loc[1], loc[2]-0.5])
                    #bottom right
                    temp.append([loc[0], loc[1], loc[2],loc[0]-0.5, loc[1], loc[2]-0.5])
            #if active pixel, insert in px_plane_coord corner coordinates of pixels
            if (len(temp) > 0):
                px_plane_coord[img_name].append(temp)
                temp = []
            

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


    # if no active pixel found in the current image, remove image from dictionary px_plane_coord because empty value
    if empty:
        px_plane_coord.pop(img_name)




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
                # verts = [(init_coord), (end_point[0], end_point[1], end_point[2])]
                # edges = [(0, 1)]
                # ray_light = bpy.data.meshes.new('ray' + str(name))
                # ray_light.from_pydata(verts, edges, [])
                # ray_light.update()
                # mesh_obj = bpy.data.objects.new('obj_' + str(name), ray_light)
                # lights.objects.link(mesh_obj)

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


# find total hull square space in the middle of all images
def hull_space():
    # hull space of 20x20x60 (to be sure because of projection) -> used to visualise entire hull space
    # loc=[0,0,5]
    # bpy.ops.mesh.primitive_cube_add(size=20.0, location= loc)
    # voxels of size 1
    for i in range(20): 
        for j in range(20):
            for k in range(20):
                #center of cubes
                loc = [10-i, 10-j, k-5]
                # for each voxel create ray from voxel center to each light center
                for l in range(len(pos_lights)):
                    ray = [loc[0], loc[1], loc[2], pos_lights[l][0] - loc[0], pos_lights[l][1] - loc[1], pos_lights[l][2] - loc[2]]
                    cubes_ray.append(ray)




# define active voxels checking for each voxel ray the point of intersection with each image, and having all corner coordinates of each pixel, check within which pixel is it and store True if is in an active pixel
# if the cube ray intersect an active pixel in each image, set it to true
# for each ray, for each active corner pixel positions check if they intersect
def active_voxels(epsilon=1e-6):
    nr_rays_per_voxel = nr_images
    counter = 0
    intersection = False
    active_check = []
    active_pixels = []
    temp = []
    temp_inconsistent = {}
    temp_empty_voxels = {}
    for e in img_names:
        temp_inconsistent[e] = []

    for i in range(len(cubes_ray)):
        # more same ray origin because more rays per voxel, then check if active voxel when all its rays intersect active pixels (nr rays = nr imgs))
        counter += 1
        origin = [cubes_ray[i][j] for j in range(3)]
        ray = [cubes_ray[i][j] for j in range(3,6)]
        # cube ray doesn't intesect all valid pixels in all images
        invalid = False
        point = []

        for k in px_plane_coord.keys():
            # random point on plane to get point of intersection if any -> corner point
            ref_px = [px_plane_coord[k][0][0][i] for i in range(3,6)]
            # get normal of plane knowing the name of the image depending on its orientation
            normal = []
            if k == 'img1': 
                # image on positive x axis
                normal = [1,0,0]
            elif k == 'img2':
                #image on negative y axis
                normal = [0,1,0]
            elif k == 'img3':
                #image on negative y axis
                normal = [-1,0,0]
            else:
                normal = [0,-1,0]
            # check if voxel ray intersect image 
            # dot product between plane normal and ray cube, intersect if > epsilon, otherwise they're parallel
            dot = (ray[0] * normal[0]) +(ray[1] * normal[1]) + (ray[2] * normal[2])

            if dot > epsilon:
                # find point of intersection
                # difference between point on plane and origin of ray
                w = [origin[i] - ref_px[i] for i in range(3)]
                fac = - dot_v3v3(normal,w)/dot
                u = mul_v3_fl(ray,fac)
                point = add_v3v3(origin, u)

                # check in which pixel the intersection point is, set one value True for the cube if active pixel
                for i in range(len(px_plane_coord[k])):
                    # pixel center
                    center = [px_plane_coord[k][i][0][m] for m in range(3)]
                    #cannot use array as keys, then transform in string
                    center_str = "{},{},{}".format(center[0], center[1],center[2])
                    if center_str not in temp_empty_voxels.keys():
                        temp_empty_voxels[center_str] = []
                    # print(temp_empty_voxels)
                    # structure pl_plane_coord[img] = [[corner_ul1,corner_ur1,corner_bl1,corner_br1], [corner_ul2,corner_ur2,corner_bl2,corner_br2], ...]
                    # check z coordinate bottom and up boundary
                    if point[2] < px_plane_coord[k][i][0][5] and point[2] >= px_plane_coord[k][i][2][5]:
                        # check y coordinates for img1 and img3 and x coordinates for img2 and img4. Append if intersection found
                        if k == 'img1':
                            if point[1] < px_plane_coord[k][i][1][4] and point[1] >= px_plane_coord[k][i][0][4]:
                                intersection = True
                        elif k == 'img3':
                            if point[1] >= px_plane_coord[k][i][1][4] and point[1] < px_plane_coord[k][i][0][4]:
                                intersection = True
                        elif k == 'img2':
                            if point[0] < px_plane_coord[k][i][0][3] and point[0] >= px_plane_coord[k][i][1][3]:
                                intersection = True
                        else:
                            if point[0] >= px_plane_coord[k][i][0][3] and point[0] < px_plane_coord[k][i][1][3]:
                                intersection = True

                    if intersection:
                        active_check.append(k)
                        temp.append(center)
                        temp_empty_voxels[center_str].append(origin)
                        #save center of pixel as temporary inconsistent, add to correct dictionary if truely inconsistent
                        if center not in temp_inconsistent[k]:
                            temp_inconsistent[k].append(center)
                    intersection = False

        # check that all rays (depending on the number of imgs) of each voxel intersect active pixels. If yes, make them active (create them)
        if counter % nr_images == 0:
            for e in img_names:
                if e not in active_check:
                    invalid = True
                    break
            if invalid:
                active_check = []
                temp = []
                continue
            else:
                active_cubes.append(origin)
                for e in temp:
                    if e not in active_pixels:
                        active_pixels.append(e)



                verts = [(origin[0], origin[1], origin[2]), (pos_lights[0][0], pos_lights[0][1], pos_lights[0][2])]
                edges = [(0, 1)]
                ray_light = bpy.data.meshes.new('ray')
                ray_light.from_pydata(verts, edges, [])
                ray_light.update()
                mesh_obj = bpy.data.objects.new('obj_', ray_light)
                lights.objects.link(mesh_obj)

                verts = [(origin[0], origin[1], origin[2]), ([0,50,4])]
                edges = [(0, 1)]
                ray_light = bpy.data.meshes.new('ray')
                ray_light.from_pydata(verts, edges, [])
                ray_light.update()
                mesh_obj = bpy.data.objects.new('obj_', ray_light)
                lights.objects.link(mesh_obj)


            active_check = []
            temp = []
            # add unique active pixels

    # temp_inconsistent contains all active and inconsistent pixels (creates voxels and cannot create voxels because voxels ray doesn't intersect with active pixel of
    # one/more other images)
    # remove all active pixels to get only inconsistent pixels
    inconsistent = True
    for k in temp_inconsistent.keys():
        for i in range(len(temp_inconsistent[k])):
            for j in range(len(active_pixels)):
                if temp_inconsistent[k][i] not in active_pixels and temp_inconsistent[k][i] not in inconsistent_pixels[k]:
                    inconsistent_pixels[k].append(temp_inconsistent[k][i])

    # find empty voxels -> NOT WORKING
    # remove active pixels as keys
    temp = {}
    for k in temp_empty_voxels.keys():
        k_int = [int(x) for x in (k.split(','))]
        if k_int not in active_pixels:
            temp[k] = temp_empty_voxels[k]
    
    temp_empty_voxels = temp
    empty = True
    for k in temp_empty_voxels.keys():
        for i in range(len(temp_empty_voxels[k])):
            for j in range(len(active_cubes)):
                if temp_empty_voxels[k][i][0] == active_cubes[j][0] and temp_empty_voxels[k][i][1] == active_cubes[j][1] and temp_empty_voxels[k][i][2] == active_cubes[j][2]:
                    empty = False
            if empty:
                k_int = [int(x) for x in (k.split(','))]
                if k not in empty_voxels.keys():
                    empty_voxels[k] = []
                    empty_voxels[k].append(temp_empty_voxels[k][i])
                else:
                    if temp_empty_voxels[k][i] not in empty_voxels[k]:
                        empty_voxels[k].append(temp_empty_voxels[k][i])

        

    bpy.data.collections.new('voxels')
    bm = bmesh.new()
    for idx, location in enumerate(active_cubes):
        new_mesh = bpy.data.meshes.new(f'result ${idx}')
        # pass vertices of cube, edges which connect vertices and faces
        new_mesh.from_pydata(
            [
            [location[0]-0.5,location[1]-0.5, location[2]+0.5],
            [location[0]+0.5,location[1]-0.5, location[2]+0.5],
            [location[0]+0.5,location[1]-0.5, location[2]-0.5],
            [location[0]-0.5,location[1]-0.5, location[2]-0.5],
            [location[0]-0.5,location[1]+0.5, location[2]+0.5],
            [location[0]+0.5,location[1]+0.5, location[2]+0.5],
            [location[0]+0.5,location[1]+0.5, location[2]-0.5],
            [location[0]-0.5,location[1]+0.5, location[2]-0.5],
            
            ], [
                [0,1],
                [1,2],
                [2,3],
                [3,0],
                [4,5],
                [5,6],
                [6,7],
                [0,4],
                [1,5],
                [2,6],
                [3,7],
                [4,7],


            ], [
                [0,1,2,3],
                [0,4,5,1],
                [1,2,6,5],
                [7,3,2,6],
                [4,5,6,7],
                [0,4,7,3],

            ])
        new_mesh.validate()
        new_mesh.update()
        bm.from_mesh(new_mesh)

    m3 = bpy.data.meshes.new('nmesh')
    bm.to_mesh(m3)
    theObj = bpy.data.objects.new("result", m3)
    for collection in bpy.data.collections:
        print(collection.name)
        bpy.data.collections[collection.name].objects.link(theObj)
        break

                             
def dot_v3v3(v0, v1):
    return ((v0[0] * v1[0]) + (v0[1] * v1[1]) + (v0[2] * v1[2]))

def mul_v3_fl(v0, f):
    return (v0[0] * f, v0[1] * f, v0[2] * f)

def add_v3v3(v0, v1):
    return (v0[0] + v1[0], v0[1] + v1[1], v0[2] + v1[2])                


            
            
# --------------OPTIMISATION--------------

            
# def find_empty_voxels():
#     for k in inconsistent_pixels.keys():
#         # center and corners inconsistent pixel 
#         for v in range(len(inconsistent_pixels[k])):
#             # find corners of inconsistent pixel from px_plane_coord by finding corresponding center
#             info = None

#             for k2 in px_plane_coord.keys():
#                 for i in range(len(px_plane_coord[k2])):
#                     if px_plane_coord[k2][i][0][0] == inconsistent_pixels[k][v][0] and px_plane_coord[k2][i][0][1] == inconsistent_pixels[k][v][1] and px_plane_coord[k2][i][0][2] == inconsistent_pixels[k][v][2]:
#                         info = px_plane_coord[k2][i]
            
#             # find ray of voxel which intersect inconsistent pixel and save voxel in empty_voxels


#     # print(info)





    
    
            





# --------------RUN CODE --------------

# clean scene removing all collections and objects before working
clean()

# collection for light rays
lights = bpy.data.collections.new('lights')
bpy.context.scene.collection.children.link(lights)
    

# read command-line arguments -> nr_images angles filenames
# nr_images -> number of images
# angles -> 1-4 angles. Can be: 0,90,180,270, where 0 is positive x axis and the other in clockwise direction with steps of 90 degrees
print(sys.argv)

img_size = 9
nr_images = None
img_names = []
images = []
angles = []
pos_lights = []
filenames = []
# read command-line arguments
for i in range(4,len(sys.argv)):
    if i == 4:
        nr_images = int(sys.argv[i])
    elif i > 4 and i <= 4 + nr_images:
        angles.append(int(sys.argv[i]))
        if int(sys.argv[i]) == 0:
            img_names.append('img1')
        elif int(sys.argv[i]) == 90:
            img_names.append('img2')
        elif int(sys.argv[i]) == 180:
            img_names.append('img3')
        elif int(sys.argv[i]) == 270:
            img_names.append('img4')
        else:
            sys.exit('Invalid angle value. Pass a valid parameter: 0,90,180,270')
    elif i > 4 + nr_images and i <= 4 + 2*nr_images:
        filenames.append(sys.argv[i])
    else:
        sys.exit('Invalid number of parameters. Pass: nr_images, angles for each light (one for image), file for each image respecting the corresponding angle.')
    
print(nr_images)
print(angles)
print(img_names)
print(filenames)

# store lights coordinates based on angles
for i in range(len(angles)):
    if angles[i] == 0:
        pos_lights.append([50,0,4])
    elif angles[i] == 90:
        pos_lights.append([0,50,4])
    elif angles[i] == 180:
        pos_lights.append([-50,0,4])
    else:
        pos_lights.append([0,-50,4])

# read txt files 
lines = []
for e in filenames:
    with open(e, 'r') as f:
        lines.append(f.readline())
# append int array of images
for i,e in enumerate(lines):
    if i >= 0 and i < nr_images:
        images.append(eval(e))
    else:
        sys.exit('Invalid number of files. Respect number given as first parameter.')

# using img name as key
# structure -> img1 : [[param1,param2,param3,param4], [parm1,param2,param3,param4]...]
# where param -> [p1,p2,p3,p4,p5,p6]
# where p's: 3 first parameters are the coordinates of the pixel center, last 3 parameters are corners coordinates of the pixel (then pixel center repeated for all corners)
px_plane_coord = {}

corners_coord = []
# origin of voxels and rays from voxels centers to light origin
cubes_ray = []

for i in range(nr_images):
    # dictionary containing as key the i,j coordinates of the pixels and as value their cartesian coordinates
    dic_img = {}
    # display images in blender
    create_img(img_names[i],images[i],dic_img, math.radians(90))
    # display lights in blender
    create_light(pos_lights[i])
    # create and display lights rays which intersect center of each pixel
    ray_light(img_names[i], dic_img, pos_lights[i], corners_coord)

# ---------- SHADOW HULL ----------
# define all voxels in a suitable space
hull_space()

# cubes which rays passes through active pixels for each image
active_cubes = []

# ---------- SHADOW HULL AND PART OF OPTIMISATION ----------
# set of incosistent pixels -> active pixels in the images but empty in the corresponding shadow (= the voxel cannot be created because its ray doesn't intersect an active pixel of one/more other image/s)
inconsistent_pixels = {}
for e in img_names:
    inconsistent_pixels[e] = []

# store inconsistent pixels as key and corresponding empty voxels as value
empty_voxels = {}
active_voxels()

# # # pixel input images -> example
# # img1 = [[0 for i in range(img_size)] for j in range(img_size)]
# # img2 = [[0 for i in range(img_size)] for j in range(img_size)]
# # # img3 = [[0 for i in range(img_size)] for j in range(img_size)]
# # # img4 = [[0 for i in range(img_size)] for j in range(img_size)]

# # #square NEED TO CHANGE -> PASS AS PARAMETER
# # for i in range(img_size):
# #     for j in range(img_size):
# #         # img4[i][j] = 1
# #         # if i >= 2 and i < 8:
# #         #     if j >= 2 and j < 8:
# #         if i == 0 and j == 0:
# #             img1[i][j] = 1
# #             img2[i][j] = 1
# #             # img2[i][j] = 1
# #         # if i == 4:
# #         #     img2[i][j] = 1
# #                 # img3[i][j] = 1
# #                 # img4[i][j] = 1
                



# # # coordinates of all lights depending on angle
# # pos_lights = []

# # for i in range(len(angles)):
# #     if angles[i] == 0:
# #         pos_lights.append([50,0,4])
# #     elif angles[i] == 90:
# #         pos_lights.append([0,50,4])
# #     elif angles[i] == 180:
# #         pos_lights.append([-50,0,4])
# #     else:
# #         pos_lights.append([0,-50,4])


# # call functions

# # dictionary containing as key the i,j coordinates of the pixels and as value their cartesian coordinates
# # dic_img1 = {}
# # dic_img2 = {}
# # dic_img3 = {}
# # dic_img4 = {}

# # px_plane_coord = {}
# # for i in range(nr_images):

# # for e in img_names:
# #     create_img(e, )
# create_img('img1',img1,dic_img1, math.radians(90))
# create_img('img2',img2,dic_img2,  math.radians(90))
# # create_img('img3',img3,dic_img3,  math.radians(90))
# # create_img('img4',img4,dic_img4,  math.radians(90))

# for i in range(len(angles)):
#     create_light(pos_lights[i])


# # array containing name of the image the rays belong to and starting_point(light), ending_point1,ending_point2... of corner pixels for each img (4 for each img)
# # corners_coord = []

# # ray_light('img1', dic_img1, pos_lights[0], corners_coord)
# # ray_light('img2',dic_img2, pos_lights[1], corners_coord)
# # ray_light('img3',dic_img3, pos_lights[2], corners_coord)
# # ray_light('img4',dic_img4, pos_lights[3], corners_coord)

# # coordinates of voxels
# # for each voxel rays from voxel center to each light source. The first 3 elements contains the origin of the ray (cube coordinates)
# cubes_ray = []
# hull_space()

# # cubes which rays passes through active pixels for each image
# active_cubes = []
# # set of incosistent pixels -> active pixels in the images but empty in the corresponding shadow (= the voxel cannot be created because its ray doesn't intersect an active pixel one/more other image/s)
# inconsistent_pixels = {}
# for e in img_names:
#     inconsistent_pixels[e] = []

# empty_voxels = {}

# active_voxels()

# # print(inconsistent_pixels)
# # print('-----')
# # print(empty_voxels)

# # using center of invalid pixels as key, as value we have the list of empty voxels (could have been created if no contraints by other images given)
# # find_empty_voxels()
