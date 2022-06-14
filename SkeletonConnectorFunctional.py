"""
This is a script to take two input skeletons and constrain the second to the first
In my personal pipeline, this is used to make a skeleton from my hair groom scene follow my animation skeleton
"""

# SYSTEM IMPORTS

# STANDARD LIB IMPORTS
import maya.cmds


# LOCAL APP IMPORTS


def skeleton_attach(rig_ns="", groom_ns="", top_level_joint=""):
    rig_tlj = f"{rig_ns}:{top_level_joint}"
    groom_tlj = f"{groom_ns}:{top_level_joint}"

    rig_joints = maya.cmds.listRelatives(rig_tlj, children=True, allDescendents=True)
    rig_joints.insert(0, rig_tlj)

    for x in rig_joints:
        driven = "{}:{}".format(groom_ns, x.split(":")[1])
        driver = x

        if maya.cmds.objExists(driven):
            # todo replace this with a matrix constraint for performance and scene cleanliness
            maya.cmds.parentConstraint(driver, driven)

        print("Constrained {} to {}".format(driver, driven))

    ### SCENE DATA ORGANIZATION
    # get scene info from fileInfo
    if maya.cmds.fileInfo("skeleton_attach", query=True):
        skel_attach_scene_info = maya.cmds.fileInfo("skeleton_attach", query=True)[0]
    else:
        skel_attach_scene_info = ""
    # append new scene info
    new_info = f"{rig_ns}|{groom_ns}|{top_level_joint}"
    # old_info = skel_attach_scene_info
    if skel_attach_scene_info:
        skel_attach_scene_info = f"{skel_attach_scene_info},{new_info}"
    else:
        skel_attach_scene_info = f"{new_info}"
    maya.cmds.fileInfo("skeleton_attach", skel_attach_scene_info)

    print("full info: ", skel_attach_scene_info)

def load_scene_constraint_data():
    scene_data = maya.cmds.fileInfo("skeleton_attach", query=True)
    sorted_scene_data = []
    if scene_data:
        scene_data = maya.cmds.fileInfo("skeleton_attach", query=True)[0]
        parsed_scene_data = scene_data.split(",")
        for item in parsed_scene_data:
            item_split = item.split("|")
            data = f"{item_split[0]}:{item_split[2]}   <--   {item_split[1]}:{item_split[2]}"
            sorted_scene_data.append(data)
    return sorted_scene_data
