"""
This is a script to take two input skeletons and constrain the second to the first
In my personal pipeline, this is used to make a skeleton from my hair groom scene follow my animation skeleton,
    or to have a separate clothing skeleton follow the main skeleton
"""

# SYSTEM IMPORTS

# STANDARD LIB IMPORTS
import maya.cmds
import re
import pymel.core as pm

# LOCAL APP IMPORTS


# TODO Write data serialize function ([array[array]]> string
# TODO Write data deserialize function (string > [array[array]])
# TODO Make this into a class to have classs-wide variables (fileinfo variable name for example)
# TODO replace re.search('[a-zA-Z]', str(maya.cmds.fileInfo("skeleton_attach", query=True))) with a short function call
# TODO Rewrite in Pymel

# I know this code sucks currently! Been struggling to get my data to work with fileInfo and want to get it functional
#   before I get it looking pretty lol. I will give it a once over when I have all the basic functionality I want.

def skeleton_attach(rig_ns: str, groom_ns: str, top_level_joint: str):
    rig_tlj = f"{rig_ns}:{top_level_joint}"
    groom_tlj = f"{groom_ns}:{top_level_joint}"

    rig_joints = maya.cmds.listRelatives(rig_tlj, children=True, allDescendents=True)
    rig_joints.insert(0, rig_tlj)

    for x in rig_joints:
        joint_name = x.split(":")[1]
        driven = f"{groom_ns}:{joint_name}"
        driver = x

        if maya.cmds.objExists(driven):
            # todo replace this with a matrix constraint for performance and scene cleanliness
            maya.cmds.parentConstraint(driver, driven)

        print(f"Constrained {driver} to {driven}")

    # SCENE DATA ORGANIZATION
    # get scene info from fileInfo
    if re.search('[a-zA-Z]', str(maya.cmds.fileInfo("skeleton_attach", query=True))):
        skel_attach_scene_info = maya.cmds.fileInfo("skeleton_attach", query=True)[0]
    else:
        skel_attach_scene_info = ""
    # append new scene info
    new_info = f"{rig_ns}|{groom_ns}|{top_level_joint}"
    # old_info = skel_attach_scene_info
    if re.search('[a-zA-Z]', str(maya.cmds.fileInfo("skeleton_attach", query=True))):
        skel_attach_scene_info = f"{skel_attach_scene_info},{new_info}"
    else:
        skel_attach_scene_info = f"{new_info}"
    maya.cmds.fileInfo("skeleton_attach", skel_attach_scene_info)

    print("full info: ", skel_attach_scene_info)


def load_scene_constraint_data():
    scene_data = maya.cmds.fileInfo("skeleton_attach", query=True)
    sorted_scene_data = []
    if re.search('[a-zA-Z]', str(maya.cmds.fileInfo("skeleton_attach", query=True))):
        scene_data = maya.cmds.fileInfo("skeleton_attach", query=True)[0]
        parsed_scene_data = scene_data.split(",")
        for item in parsed_scene_data:
            item_split = item.split("|")
            #       "{rig_ns}|              {groom_ns}|     {top_level_joint}"
            data = f"{item_split[0]}  <--  {item_split[1]}  (tlj:{item_split[2]})"
            sorted_scene_data.append(data)
    return sorted_scene_data


def skeleton_detach(rig_ns: str, groom_ns: str, top_level_joint: str):
    # hate how fileinfo smushes everything down to a single string, actual nightmare
    scene_data = maya.cmds.fileInfo("skeleton_attach", query=True)
    print(scene_data)
    sorted_scene_data = []
    if scene_data:
        scene_data = maya.cmds.fileInfo("skeleton_attach", query=True)[0]
        parsed_scene_data = scene_data.split(",")
        for item in parsed_scene_data:
            if all(x for x in item.split("|") if x in [rig_ns, groom_ns, top_level_joint]):
                # remove item from fileinfo
                temp_remove_string = f"{rig_ns}|{groom_ns}|{top_level_joint}"
                scene_data_split = scene_data.split(temp_remove_string)

                if len(scene_data_split) > 1:
                    updated_fileinfo = ",".join(scene_data_split)
                else:
                    updated_fileinfo = scene_data_split

                maya.cmds.fileInfo("skeleton_attach", updated_fileinfo)

                # TODO Check that it isn't left with just a "," in the fileinfo

                print("Updated skeleton_attach fileinfo", maya.cmds.fileInfo("skeleton_attach", query=True))

                # Remove constraints
                for object in pm.PyNode(f"{groom_ns}:{top_level_joint}").getChildren(ad=True):
                    if pm.objectType(object) == "parentConstraint":
                        pm.delete(object)

def wipe_relevant_fileinfo(are_you_sure=False):
    if are_you_sure:
        maya.cmds.fileInfo("skeleton_attach", "")
