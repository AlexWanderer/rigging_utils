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
#  Authors: 
#       Tamir Lousky
#           Homepage: http://bioblog3d.wordpress.com/
#           Contact:  tlousky@gmail.com
#       Kfir Merlaub
#           Homepage: http://kfirmerlaub.wix.com/
#           Contact:  kfir.merlaub@gmail.com
#
#  Start of project : 2013-01-25 
#  Last modified    : 2013-04-03
#
#  Acknowledgements 
#  ================
#
#  Blender: Nathan Vegdahl (who taught us everything we know about 
#           blender py-rigging)
 
bl_info = {    
    "name"       : "Armature Utils",
    "authors"    : [ "Kfir, Merlaub", "Tamir Lousky" ],
    "version"    : (1, 0, 0),
    "blender"    : (2, 66, 0),
    "category"   : "Rigging",
    "location"   : "Properties >> Armature",
    "wiki_url"   : "",
    "tracker_url": "",
    "description": "Assign bone colors by the rig layers they are on."
}

import bpy

def find_active_layers( obj ):
    ''' This function iterates over all bones in the rig, and returns a list of
         all the layers on which these bones are located '''

    all_active_layers = []

    for bone in obj.data.bones:
        # Find bone's active layers. An active layer has a True value.
        i = 0
        for l in bone.layers:
            # Add an active layer's index to list if its not already there
            if l and i not in all_active_layers:
                all_active_layers.append( i )
            i += 1

    return all_active_layers


class bone_colors( bpy.types.Panel ):
    bl_idname      = 'BoneColorsPanel'
    bl_label       = 'Assign Bone Colors'
    bl_space_type  = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context     = 'posemode'

    @classmethod
    def poll( self, context ):
        try:
            arm  = context.active_object.type == 'ARMATURE'
            pose = context.active_object.mode == 'POSE'
            return( arm and pose )
        except:
            return False

    def draw( self, context ):
        # Draw panel UI elements #
        layout = self.layout               # Reference to panel layout object

        obj         = bpy.context.object   # Ref to active armature
        color_props = obj.bonegroup_colors # Ref to property group
        bgroups     = obj.pose.bone_groups # Ref to bone groups

        # Draw "use colors" checkbox
        col        = layout.column()
        col.prop( color_props, "use_colors", "Create Color Groups by Rig Layer" )

        if color_props.use_colors:
            group_names = sorted( [ g.name for g in bgroups ] )
            
            # each bone group gets a row where you can choose its color
            for group in group_names:
                
                g = bgroups[ group ]
                
                split = layout.split()
                split.active = (obj.proxy is None)

                col = split.column()
                row = col.row()
                row.label( text = g.name )
                row.prop(g, "color_set")  # Choose group color theme

                if g.color_set:
                    col = split.column()
                    sub = col.row( align = True )
                    sub.prop(g.colors, "normal", text="") # Theme normal color
                    sub.prop(g.colors, "select", text="") # Theme select color
                    sub.prop(g.colors, "active", text="") # Theme active color
        

class ColorBones( bpy.types.PropertyGroup ):

    def create_groups( self, context ):
        """ Creates bone groups by rig layers """
        obj = bpy.context.object

        # Exit and do not create groups if "use_colors" is set to False
        if self.use_colors == False:
            return None
        
        active_layers = find_active_layers( obj )

        # Get existing bone group names  
        bgroups = [ g.name for g in obj.pose.bone_groups ]
        
        for l in active_layers:
            
            # Make bone Group name from bone layer number
            if l < 10:
                bgroup_name = 'bone_group_0' + str(l)
            else:
                bgroup_name = 'bone_group_'  + str(l)

            # Create a new bone group if it doesn't exist
            if bgroup_name not in bgroups:
                bpy.ops.pose.group_add()
                obj.pose.bone_groups[-1].name = bgroup_name
                
            ## Add bones to this group (if they're on the appropriate layer )
            
            # Reference all the bones on this layer
            layer_bones = [ b.name for b in obj.data.bones if b.layers[l] ]

            """ Note that this addon will not work as expected if bones are on
                more than one layer. The group representing the highest number
                layer will contain a bone with more than one layer.
            """

            # Add bones to group
            for bone in layer_bones:
                pb = obj.pose.bones[ bone ]
                pb.bone_group = obj.pose.bone_groups[ bgroup_name ]
            
        return None

    use_colors = bpy.props.BoolProperty(
        name        = "use_colors",
        description = "Color bones by rig layers",
        default     = False,
        update      = create_groups
    ) 


def register():
    bpy.utils.register_module(__name__)

    # Ref to prop group via dynamic object property
    bpy.types.Object.bonegroup_colors = bpy.props.PointerProperty( type = ColorBones )
    
def unregister():
    bpy.utils.unregister_module(__name__)
