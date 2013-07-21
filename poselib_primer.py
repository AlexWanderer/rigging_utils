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
    "blender"    : (2, 68, 0),
    "category"   : "Rigging",
    "location"   : "3D View >> Tools",
    "wiki_url"   : "",
    "tracker_url": "",
    "description": "Drivers for shapekeys based on relative bone transforms"
}

""" Create a base pose library with common empty poses, that will later
be easy to populate with real actions """

import bpy

class BasicPoseLibPanel(bpy.types.Panel):
    bl_idname      = "BasicPoseLibPanel"
    bl_label       = "Create a Basic Pose Library"
    bl_space_type  = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context     = 'data'

    @classmethod
    def poll( self, context ):
        return context.object.type == 'ARMATURE'
    

    def draw( self, context) :
        layout = self.layout
        

        col = layout.column()

        col.operator( BasicPoseLib.Button ) # Create new / update shakepey

### Need to add:
#   Operator

