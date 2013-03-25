# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####
# 
#  Authors           : Kfir Merlaub, Tamir Lousky
#  Homepage(Wiki)    : http://kfirmerlaub.wix.com/     ( Kfir Merlaub (kfir.merlaub@gmail.com) )
#  Homepage(Wiki)    : http://bioblog3d.wordpress.com/ ( Tamir Lousky (tlousky@gmail.com)      )
#
#  Start of project              : 2013-01-25 
#  Last modified                 : 2013-03-20
#
#  Acknowledgements 
#  ================
#
#  Blender: Nathan Vegdahl (who taught us everything we know about blender py-rigging) 
#          


""" TODO:
1. UI:
   checkbox   layer name    theme/color        [ loop this for all layers ]
   Randomize [button] # apply random color for each of the active (checked) layers

2. layer checkbox creates or deletes a bone group with a predefined name: "rig_utils_layer_(X)"

Notes:
armature layers in:
bpy.data.armatures[idx].layers
"""

bl_info = {    
    "name"       : "Armature Utils",
    "authors"    : [ "Kfir, Merlaub", "Tamir Lousky" ],
    "version"    : (1, 0, 0),
    "blender"    : (2, 66, 0),
    "category"   : "Materials",
    "location"   : "Properties >> Armature",
    "wiki_url"   : "",
    "tracker_url": "",
    "description": "Various rigging utilities."
}

import bpy

class random_mat_panel(bpy.types.Panel):
    bl_idname      = 'rigging_utils'
    bl_label       = 'Rigging Utilities'
    bl_space_type  = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context     = 'object'

    @classmethod
    def poll(self, context):
        try:
            return ( context.active_object.type == 'ARMATURE' )
        except:
            return False

    def draw( self, context):                # Draw panel UI elements #
        layout = self.layout                 # Reference to panel layout object
        
#        props = context.scene.face_assigner

        col1 = layout.column()               # Create a column
        col1.label(text="Randomly assign materials to each face on the object")
        
        box = layout.box()                   # Draw a box
        col2 = box.column(align=True)        # Create a column
        col2.prop( props, "rand_seed"  )     # Create randomization seed property on column
        col2.label(text="use this field to filter materials by name")
        col2.prop( props, "mat_prefix" )     # Material prefix property too
        col2.label(text="Distribute materials according to:")
        col2.prop( props, "assign_method" )  # Material assignment method prop


def color_bones( obj ):

    # Assign bone groups and colors
    colors = {
        'red'    : 'THEME01',
        'blue'   : 'THEME04',
        'green'  : 'THEME03',
        'yellow' : 'THEME09',
        'purple' : 'THEME06'
    }

    bpy.ops.object.mode_set(mode='POSE')

    for c in colors:
        bpy.ops.pose.group_add()
        obj.pose.bone_groups[-1].name      = c
        obj.pose.bone_groups[-1].color_set = colors[c]

    for bone in obj.pose.bones:

        # Set bone group by name
        if   '.L' in bone.name:
            bone.bone_group = obj.pose.bone_groups['red'   ]
        elif '.R' in bone.name:
            bone.bone_group = obj.pose.bone_groups['blue'  ]
        else:
            bone.bone_group = obj.pose.bone_groups['yellow']
        
    bpy.ops.object.mode_set(mode='OBJECT') 
