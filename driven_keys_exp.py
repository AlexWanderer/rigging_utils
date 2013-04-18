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
#  Author            : Tamir Lousky [ tlousky@gmail.com, tamir@pitchipoy.tv ]
#
#  Homepage(Wiki)    : http://bioblog3d.wordpress.com/
#  Studio (sponsor)  : Pitchipoy Animation Productions (www.pitchipoy.tv)
# 
#  Start of project              : 2013-04-04 by Tamir Lousky
#  Last modified                 : 2013-04-04
#
#  Acknowledgements 
#  ================
#   

bl_info = {    
    "name"       : "Driven Shapekeys",
    "author"     : "Tamir Lousky",
    "version"    : (0, 0, 1),
    "blender"    : (2, 66, 0),
    "category"   : "Rigging",
    "location"   : "3D View >> Tools",
    "wiki_url"   : "",
    "tracker_url": "",
    "description": "Drivers for shapekeys based on relative bone transforms"
}

""" 
This addon creates a driven empty shapekey based on the spacial relatiobship
between two bones. The purpose is to create a semi-automatic mechanism for
corrective shapekeys. There are currently two possible drivers:
1. The distance between the heads of two bones
2. The sum of the difference of rotation, location and scale (delta transforms)
   between a single bone's current position and a recorded "rest" position.

If you choose an existing shapekey, the driver will be added to it, otherwise
an empty shapekey will be created and the driver will be added to it.
"""

import bpy
import math

class DrivenKeysPanel(bpy.types.Panel):
    bl_idname      = "DrivenKeysPanel"
    bl_label       = "Driven Shapekeys"
    bl_space_type  = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_context     = 'posemode'

    def draw( self, context) :
        layout = self.layout
        
        # import external properties
        drv_sk_props = context.scene.corrective_drivenkeys_props

        col = layout.column()

        col.prop_search(          
            drv_sk_props, "mesh_object", # Pick object out of
            context.scene, "objects"     # the list of objects in the scene
        )


class UpdateKeyPanel(bpy.types.Panel):
    bl_idname      = "UpdateKeyPanel"
    bl_label       = "Choose shapekey to drive from selected object"
    bl_space_type  = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_context     = 'posemode'

    drv_sk_props = context.scene.corrective_drivenkeys_props

    @classmethod
    def poll( self, context ):
        # The object name must represent a real object in the scene
        if drv_sk_props.mesh_object in [ obj.name for obj in context.scene.objects ]:
            obj = context.scene.objects[ drv_sk_props.mesh_object ]
            # And it must be a mesh object
            if obj.type == 'MESH':
                return True
        return False

    def draw( self, context ):
        layout = self.layout

        obj = bpy.context.scene.objects[ drv_sk_props.mesh_object ]
        sk  = obj.data.shape_keys

        col.prop_search(          
            drv_sk_props, "update_shapekey", # Pick shapekey out of the list of
            sk,           key_blocks         # shapkeys on the selected object
        )


class DriverPanel(bpy.types.Panel):
    bl_idname      = "DriverPanel"
    bl_label       = "Specify the driver's transform channels"
    bl_space_type  = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_context     = 'posemode'

    drv_sk_props = context.scene.corrective_drivenkeys_props

    @classmethod
    def poll( self, context ):
        selected_bones = [ bone.name for bone in context.object.data.bones if bone.select ]
        
        # Only one bone must be selected     
        return len( selected_bones ) == 1
        
    def draw( self, context ):
        pass
        """
        layout = self.layout
        
        col = layout.column()
        
        col.operator( 'armature.b2bDriver' )
        """


class CreateDriver( bpy.types.Operator ):
    """ Create the driver based on the current bone's maximal position """
    bl_idname      = "armature.create_driver"
    bl_label       = "Create driver"
    bl_description = "Create driver"
    bl_options     = { 'REGISTER', 'UNDO' }

    @classmethod
    def poll( self, context ):
        obj = context.object
        # If the object is of the correct type 
        if obj.type == 'ARMATURE':
            # and it is in the correct selection mode 
            if obj.mode == 'POSE':
                # and if there'mesh_objects exactly 1 pose bone selected
                if len( [ b for b in obj.data.bones if b.select ] ) == 1:
                    # then enable this operator
                    return True
        return False

    def execute( self, context):
        # Get the selected bone
        name = [ b.name for b in obj.data.bones if b.select ].pop()
        pb   = obj.pose.bones[ name ]
                  
        drv_sk_props = context.scene.corrective_drivenkeys_props
        
        # Update external property
        drv_sk_props.rest_pos = matrix
        
        return {'FINISHED'}


class b2bDriver( bpy.types.Operator ):
    """ Records the rest position of a bone for a delta transforms driver """
    bl_idname      = "armature.b2bDriver"
    bl_label       = "Create a B2B distance based shapekey driver"
    bl_description = "Create a B2B distance based shapekey driver"
    bl_options     = { 'REGISTER', 'UNDO' }

    drv_sk_props = context.scene.corrective_drivenkeys_props
    sk_obj       = context.scene.objects[ drv_sk_props.mesh_object ]

    @classmethod
    def poll( self, context ):

        if drv_sk_props.update_key and not drv_sk_props.update_shakepey:
            # If the "update key" options was selected but no specific 
            # shakepey was chosen to accept the driver, lock this operator
            return False
            
        obj = context.object
        # If the object is of the correct type 
        if obj.type == 'ARMATURE':
            # and it is in the correct selection mode 
            if obj.mode == 'POSE':
                # and if there's exactly 2 pose bones selected
                if len( [ b for b in obj.data.bones if b.select ] ) == 2:
                    # Make sure the user selected a proper obj for shapekeying
                    if drv_sk_props.mesh_object and sk_obj.type = 'MESH':
                        # then enable this operator
                        return True
        return False

    def execute( self, context):
        # Get the selected bones
        bones    = [ b.name for b in obj.data.bones if b.select ]
        pb1, pb2 = [ obj.pose.bones[ b ] for b in bones ]
        
        rest_dist = pb1.head - pb2.head
        rest_len  = rest_dist.length
        
        shapekey_name = ''
        
        # If the user chose a shapekey, add driver to it,
        if drv_sk_props.update_key:
            shapekey_name = drv_sk_props.update_shapekey
        else: # otherwise create a new one
            sk_obj.shape_key_add( name = 'Blah', from_mix = False )
        
        

        
        shapekey = sk_obj.data.shape_keys.key_blocks[ shapekey_name ]
        
        update_shapekey
        
        # Create driver
        drv                          = pb[mch_drv].driver_add("rotation_euler", options[axis]["axis"]).driver
        drv.type                     = 'SCRIPTED'
        drv.expression               = options[axis]["expr"]
        drv_var                      = drv.variables.new()
        drv_var.name                 = 'sy'
        drv_var.type                 = "SINGLE_PROP"
        drv_var.targets[0].id        = self.obj
        drv_var.targets[0].data_path = pb[master_name].path_from_id() + '.scale.y'

        matrix = []
        
        # A transformation matrix is composed of 4 vectors of 4 points each
        # These are stored as a simple array here
        for v in pb.matrix:
            for p in v:
                matrix.append( p )
                
        drv_sk_props = context.scene.corrective_drivenkeys_props
        
        # Update external property
        drv_sk_props.rest_pos = matrix
        
        return {'FINISHED'}




class correctiveDrivenkeysProps( bpy.types.PropertyGroup ):
    # Create a new shapekey or add a driver to an existing one
    update_key = bpy.props.BoolProperty(
        name        = "update_key",
        description = "Add driver to an existing shapekey", 
        default     = False
    )
    
    # These two will be used to select existing objects and shapekeys to
    # add drivers to
    mesh_object     = bpy.props.StringProperty()
    update_shapekey = bpy.props.StringProperty()
    
    locX = bpy.props.BoolProperty(
        name        = "locX",
        description = "use X location for driving the shapekey", 
        default     = False
    )
    locXmax = bpy.props.FloatProperty(
        name        = "locXmax", 
        description = "value for full shapekey activation" 
    )
    locY = bpy.props.BoolProperty(
        name        = "locY",
        description = "use Y location for driving the shapekey", 
        default     = False
    ) 
    locYmax = bpy.props.FloatProperty(
        name        = "locYmax", 
        description = "value for full shapekey activation" 
    ) 
    locZ = bpy.props.BoolProperty(
        name        = "locZ",
        description = "use Z location for driving the shapekey", 
        default     = False
    )
    locZmax = bpy.props.FloatProperty(
        name        = "locZmax", 
        description = "value for full shapekey activation" 
    )
    rotX = bpy.props.BoolProperty(
        name        = "rotX",
        description = "use X rotation (degrees) for driving the shapekey", 
        default     = False
    )
    rotXmax = bpy.props.FloatProperty(
        name        = "rotXmax", 
        description = "value for full shapekey activation",
        subtype     = 'ANGLE'
    )
    rotY = bpy.props.BoolProperty(
        name        = "rotY",
        description = "use Y rotation (degrees) for driving the shapekey", 
        default     = False
    )
    rotYmax = bpy.props.FloatProperty(
        name        = "rotYmax", 
        description = "value for full shapekey activation",
        subtype     = 'ANGLE'
    )
    rotZ = bpy.props.BoolProperty(
        name        = "rotZ",
        description = "use Z rotation (degrees) for driving the shapekey", 
        default     = False
    )
    rotZmax = bpy.props.FloatProperty(
        name        = "rotZmax", 
        description = "value for full shapekey activation",
        subtype     = 'ANGLE'
    )
    sclX = bpy.props.BoolProperty(
        name        = "sclX",
        description = "use X scale for driving the shapekey", 
        default     = False
    )
    sclXmax = bpy.props.FloatProperty(
        name        = "sclXmax", 
        description = "value for full shapekey activation" 
    )
    sclY = bpy.props.BoolProperty(
        name        = "sclY",
        description = "use Y scale for driving the shapekey", 
        default     = False
    )
    sclYmax = bpy.props.FloatProperty(
        name        = "sclYmax", 
        description = "value for full shapekey activation" 
    )
    sclZ = bpy.props.BoolProperty(
        name        = "sclZ",
        description = "use Z scale for driving the shapekey", 
        default     = False
    )
    sclZmax = bpy.props.FloatProperty(
        name        = "sclZmax", 
        description = "value for full shapekey activation" 
    )


def register():
    bpy.utils.register_module(__name__)
    bpy.types.Scene.corrective_drivenkeys_props = bpy.props.PointerProperty( 
        type = correctiveDrivenkeysProps )
    
def unregister():
    bpy.utils.unregister_module(__name__)

# Registers the class and panel when you run the script from the text editor
# bpy.utils.register_module(__name__)
