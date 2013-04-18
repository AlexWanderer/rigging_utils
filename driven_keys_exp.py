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
#  Authors         : Tamir Lousky [ tlousky@gmail.com, tamir@pitchipoy.tv     ]
#                    Kfir Merlaub [ kfir.merlaub@gmail.com, kfir@pitchipoy.tv ]
#
#  Homepage(Wiki)    : [Tlousky] http://bioblog3d.wordpress.com/
#  Homepage(Wiki)    : [KfirMer] http://kfirmerlaub.wix.com/kfirconceptart
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
    "authors"    : [ "Tamir Lousky", "Kfir Merlaub" ],
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
import re

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

    @classmethod
    def poll( self, context ):
        drv_sk_props = context.scene.corrective_drivenkeys_props
        
        # The object name must represent a real object in the scene
        if drv_sk_props.mesh_object in [ obj.name for obj in context.scene.objects ]:
            obj = context.scene.objects[ drv_sk_props.mesh_object ]
            # And it must be a mesh object
            if obj.type == 'MESH':
                return True
        return False

    def draw( self, context ):
        drv_sk_props = context.scene.corrective_drivenkeys_props
         
        layout = self.layout

        obj = bpy.context.scene.objects[ drv_sk_props.mesh_object ]
        sk  = obj.data.shape_keys

        col = layout.column()

        col.prop_search(          
            drv_sk_props, "update_shapekey", # Pick shapekey out of the list of
            sk,           "key_blocks"       # shapkeys on the selected object
        )


class DriverPanel(bpy.types.Panel):
    bl_idname      = "DriverPanel"
    bl_label       = "Specify the driver's transform channels"
    bl_space_type  = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_context     = 'posemode'

    @classmethod
    def poll( self, context ):
        drv_sk_props   = context.scene.corrective_drivenkeys_props
        selected_bones = [ bone.name for bone in context.object.data.bones if bone.select ]
        
        name = drv_sk_props.mesh_object
        
        obj_exists = name in [ obj.name for obj in context.scene.objects ]

        obj_type = ''
        if obj_exists:
            obj_type = context.scene.objects[ name ].type
        
        correct_type = obj_type == 'MESH'
        
        # Only one bone must be selected     
        return len( selected_bones ) == 1 and obj_exists and correct_type
        
    def draw( self, context ):
        drv_sk_props = context.scene.corrective_drivenkeys_props

        layout = self.layout
        
        col = layout.column()
        
        for trans_channel in [ 'loc', 'rot', 'scl' ]:
            for axis in [ 'X', 'Y', 'Z' ]:
                row = col.row()
                
                row.label( text = trans_channel + " " + axis )
                
                prop1 = trans_channel + axis
                prop2 = prop1 + 'max'
                
                row.prop( drv_sk_props, prop1 )
                row.prop( drv_sk_props, prop2 )
        
        col.separator()
        
        col.prop( drv_sk_props, 'symmetrize' )
        
        col.operator( 'armature.create_driver' )


class CreateDriver( bpy.types.Operator ):
    """ Create the driver based on the current bone's maximal position """
    bl_idname      = "armature.create_driver"
    bl_label       = "Create driver"
    bl_description = "Create driver"
    bl_options     = { 'REGISTER', 'UNDO' }

    @classmethod
    def poll( self, context ):
        drv_sk_props = context.scene.corrective_drivenkeys_props
        
        driver_options = {
                'LOC_X'   : [ drv_sk_props.locX, drv_sk_props.locXmax ],
                'LOC_Y'   : [ drv_sk_props.locY, drv_sk_props.locYmax ],  
                'LOC_Z'   : [ drv_sk_props.locZ, drv_sk_props.locZmax ],
                'ROT_X'   : [ drv_sk_props.rotX, drv_sk_props.rotXmax ],
                'ROT_Y'   : [ drv_sk_props.rotY, drv_sk_props.rotYmax ],
                'ROT_Z'   : [ drv_sk_props.rotZ, drv_sk_props.rotZmax ],
                'SCALE_X' : [ drv_sk_props.sclX, drv_sk_props.sclXmax ],
                'SCALE_Y' : [ drv_sk_props.sclY, drv_sk_props.sclYmax ],
                'SCALE_Z' : [ drv_sk_props.sclZ, drv_sk_props.sclZmax ]
        }

        obj = context.object
        active_options = [ o for o in driver_options if driver_options[ o ][0] ]
        
        # If the object is of the correct type 
        if obj.type == 'ARMATURE':
            # and it is in the correct selection mode 
            if obj.mode == 'POSE':
                # and if there's exactly 1 pose bone selected
                if len( [ b for b in obj.data.bones if b.select ] ) == 1:
                    # Ensure the user chose at least one driver transform chan.
                    if len( active_options ) > 0:
                        # then enable this operator
                        return True
        return False

    def create_driver( self, context, obj, rig, bone, shapekey_name ):
        drv_sk_props = context.scene.corrective_drivenkeys_props

        driver_options = {
                'LOC_X'   : [ drv_sk_props.locX, drv_sk_props.locXmax ],
                'LOC_Y'   : [ drv_sk_props.locY, drv_sk_props.locYmax ],  
                'LOC_Z'   : [ drv_sk_props.locZ, drv_sk_props.locZmax ],
                'ROT_X'   : [ drv_sk_props.rotX, drv_sk_props.rotXmax ],
                'ROT_Y'   : [ drv_sk_props.rotY, drv_sk_props.rotYmax ],
                'ROT_Z'   : [ drv_sk_props.rotZ, drv_sk_props.rotZmax ],
                'SCALE_X' : [ drv_sk_props.sclX, drv_sk_props.sclXmax ],
                'SCALE_Y' : [ drv_sk_props.sclY, drv_sk_props.sclYmax ],
                'SCALE_Z' : [ drv_sk_props.sclZ, drv_sk_props.sclZmax ]
        }
                  
        shapekeys          = obj.data.shape_keys
        existing_shapekeys = [ sk.name for sk in shapekeys.key_blocks ]

        # If sk exists use it, else create a new one        
        if shapekey_name not in existing_shapekeys:
            obj.shape_key_add( name = shapekey_name, from_mix = False )
            
        shapekey = shapekeys.key_blocks[ shapekey_name ]

        # Create driver    
        drv      = shapekey.driver_add( "value" ).driver
        drv.type = 'SCRIPTED'        

        expression = ""

        active_options = [ o for o in driver_options if driver_options[ o ][0] ]
        last = len( active_options )

        i = 1
        for opt in active_options:
            drv_var                            = drv.variables.new()
            drv_var.name                       = opt
            drv_var.type                       = 'TRANSFORMS'
            drv_var.targets[0].id              = rig
            drv_var.targets[0].bone_target     = bone
            drv_var.targets[0].transform_type  = opt
            drv_var.targets[0].transform_space = 'LOCAL_SPACE'       
           
            convertor = str( round( driver_options[ opt ][1], 3 ) )
                
            if last == 1:
                expression = opt + "/" + convertor
            elif i == 1:
                expression += "(" + opt + "/" + convertor
            elif i == last:
                expression += "+" + opt + "/" + convertor + ")"
                expression += "/" + str(last)
            else:
                expression += "+" + opt + "/" + convertor
            
            i += 1
  
        drv.expression = expression

        return {'FINISHED'}        
    
    def execute( self, context ):
        drv_sk_props = context.scene.corrective_drivenkeys_props

        obj          = context.scene.objects[ drv_sk_props.mesh_object ]
        rig          = context.object

        # Get the selected bone
        bone = [ b.name for b in rig.data.bones if b.select ].pop()

        shapekey_name = drv_sk_props.update_shapekey

        self.create_driver( context, obj, rig, bone, shapekey_name )
        
        if drv_sk_props.symmetrize:
            pattern     = '^(\w+[-_]?\w+?)(\.)?([LR])?(\.\d*)?$'
            bone_pieces = re.match( pattern, bone )

            opposite = { 'L' : 'R', 'R' : 'L' }
            
            if bone_pieces:
                groups = [ g for g in bone_pieces.groups() ]
                
                if groups[2]:
                    groups[2]      = opposite[ groups[2] ]
                    congroups      = [ p for p in groups if p ]
                    opposite_name  = "".join( congroups )
                    
                    shapekey_name += "." + opposite[ groups[2] ]
                    
                    if opposite_name in [ b.name for b in rig.data.bones ]:
                        self.create_driver( context, obj, rig, opposite_name, shapekey_name )

        return {'FINISHED'} 

class correctiveDrivenkeysProps( bpy.types.PropertyGroup ):
    # These two will be used to select existing objects
    # and shapekeys to add drivers to
    mesh_object     = bpy.props.StringProperty()
    update_shapekey = bpy.props.StringProperty()
    
    # Driver options
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

    # Create a matching shapekey and driver for the opposite bone
    symmetrize = bpy.props.BoolProperty(
        name        = "symmetrize",
        description = "create driver on the corresponding mirror side bone", 
        default     = False
    )


def register():
    bpy.utils.register_module(__name__)
    bpy.types.Scene.corrective_drivenkeys_props = bpy.props.PointerProperty( 
        type = correctiveDrivenkeysProps )
    
def unregister():
    bpy.utils.unregister_module(__name__)

# Registers the class and panel when you run the script from the text editor
# bpy.utils.register_module(__name__)
