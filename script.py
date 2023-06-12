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


print(angles)
print(nr_img)



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
    


# pixel input images -> example
img1 = [[0 for i in range(9)] for j in range(9)]
img2 = [[0 for i in range(9)] for j in range(9)]

#square
for i in range(len(img1)):
    for j in range(len(img1[i])):
        if i >= 2 and i < 8:
            if j >= 2 and j < 8:
                img1[i][j] = 1
                img2[i][j] = 1



def create_img(img_name, img, dic, rot_y):
    #1 square of planes which represents 1 img
    for i in range(len(img)):
        for j in range(len(img[i])):
            loc = []
            if img_name == 'img3':
                loc = [-20,j-4,i]
            elif img_name == 'img4':
                loc = [j-4,-20,i]
            elif img_name == 'img1':
                loc = [20,j-4,i]
            else:
                loc = [j-4,20,i]
            # Create planes as pixels

            bpy.ops.mesh.primitive_plane_add(size=1.0, location= loc)
            pixel = bpy.context.object
            pixel.name = "Pixel"
            pixel.rotation_euler[0] = math.radians(90)
            if rot_y != None and (img_name == 'img1' or img_name == 'img3'):
                pixel.rotation_euler[2] = rot_y

            dic[i,j] = loc
            # Assign a unique material to each pixel
            material = bpy.data.materials.new(name="PixelMaterial")
            if img[i][j] == 0:
                material.diffuse_color = (1, 1, 1,1)  # Replace with desired color
            else:
                material.diffuse_color = (0, 0, 0,0)  # Replace with desired color






# Create light rays -> use a mesh and attach it to an object, then insert in collection
# create a ray for each pixel center

# input: grid of binary image pixels
def ray_light(img, name, dic, pos_light):
    #insert rays in a new collection
    for i in range(len(img)):
        for j in range(len(img[i])):
            # vector from point light  to center of pixel
            xi=pos_light[0]
            yi=pos_light[1]
            zi=pos_light[2]

            xf=dic[(i,j)][0]
            yf=dic[(i,j)][1]
            zf=dic[(i,j)][2]

            # create lines from the light point to the center of each pixel. Increase then the length of the lines to know the space
            # to build the hull
            end_point =increase_line_length([xi,yi,zi], [xf,yf,zf],30)
            verts = [(xi, yi, zi), (end_point[0], end_point[1], end_point[2])]
            edges = [(0, 1)]
            ray_light = bpy.data.meshes.new('ray_' + str(name) + '_' +str(i) + str(j))
            ray_light.from_pydata(verts, edges, [])
            ray_light.update()
            mesh_obj = bpy.data.objects.new('obj_' + str(name) + '_' + str(i) + str(j), ray_light)
            lights.objects.link(mesh_obj)


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


# clean scene removing all collections and objects before working
clean()


# collection for light rays
lights = bpy.data.collections.new('lights')
bpy.context.scene.collection.children.link(lights)


dic_img1 = {}
dic_img2 = {}
dic_img3 = {}
dic_img4 = {}

create_img('img1',img1,dic_img1, math.radians(90))
create_img('img2',img2,dic_img2,  math.radians(90))

for i in range(len(angles)):
    create_light(pos_lights[i])


ray_light(img1,'img1', dic_img1, pos_lights[0])
ray_light(img2,'img2',dic_img2, pos_lights[1])

