"""
This is a script to take two input skeletons and constrain the second to the first
In my personal pipeline, this is used to make a skeleton from my hair driven scene follow my animation skeleton,
    or to have a separate clothing skeleton follow the main skeleton
"""

# SYSTEM IMPORTS

# STANDARD LIB IMPORTS
import maya.cmds
import re
import pymel.core as pm

# LOCAL APP IMPORTS

# TODO replace Parent Constraint with a Matrix Constraint for performance and scene cleanliness
# TODO Write data serialize function ([array[array]]> string
# TODO Write data deserialize function (string > [array[array]])
# TODO Rewrite in Pymel

class Skeleton_Connector_Functional():
    def __init__(self):
        self.fileinfo_key = "skeleton_attach"

    def data_in_fileinfo_key(self) -> bool:
        data_exists = True if re.search('[a-zA-Z]', str(maya.cmds.fileInfo(self.fileinfo_key, query=True))) else False
        return data_exists

    def skeleton_attach(self, rig_ns: str, driven_ns: str, top_level_joint: str):
        rig_tlj = f"{rig_ns}:{top_level_joint}"
        driven_tlj = f"{driven_ns}:{top_level_joint}"

        rig_joints = maya.cmds.listRelatives(rig_tlj, children=True, allDescendents=True)
        rig_joints.insert(0, rig_tlj)

        for x in rig_joints:
            joint_name = x.split(":")[1]
            driven = f"{driven_ns}:{joint_name}"
            driver = x

            if maya.cmds.objExists(driven):
                maya.cmds.parentConstraint(driver, driven)

            print(f"Constrained {driver} to {driven}")

        # Get scene info from fileInfo
        if self.data_in_fileinfo_key():
            skel_attach_scene_info = maya.cmds.fileInfo(self.fileinfo_key, query=True)[0]
        else:
            skel_attach_scene_info = ""

        # append new scene info
        new_info = f"{rig_ns}|{driven_ns}|{top_level_joint}"

        if self.data_in_fileinfo_key():
            skel_attach_scene_info = f"{skel_attach_scene_info},{new_info}"
        else:
            skel_attach_scene_info = f"{new_info}"
        maya.cmds.fileInfo(self.fileinfo_key, skel_attach_scene_info)

        print("full info: ", skel_attach_scene_info)


    def load_scene_constraint_data(self):
        scene_data = maya.cmds.fileInfo(self.fileinfo_key, query=True)
        sorted_scene_data = []
        if self.data_in_fileinfo_key():
            scene_data = maya.cmds.fileInfo(self.fileinfo_key, query=True)[0]
            parsed_scene_data = scene_data.split(",")
            for item in parsed_scene_data:
                item_split = item.split("|")
                #       "{rig_ns}|              {driven_ns}|     {top_level_joint}"
                data = f"{item_split[0]}  <--  {item_split[1]}  (tlj:{item_split[2]})"
                sorted_scene_data.append(data)
        return sorted_scene_data


    def skeleton_detach(self, rig_ns: str, driven_ns: str, top_level_joint: str):
        # hate how fileinfo smushes everything down to a single string, actual nightmare
        scene_data = maya.cmds.fileInfo(self.fileinfo_key, query=True)
        print(scene_data)
        sorted_scene_data = []
        if scene_data:
            scene_data = maya.cmds.fileInfo(self.fileinfo_key, query=True)[0]
            parsed_scene_data = scene_data.split(",")
            for item in parsed_scene_data:
                if all(x for x in item.split("|") if x in [rig_ns, driven_ns, top_level_joint]):
                    # remove item from fileinfo
                    temp_remove_string = f"{rig_ns}|{driven_ns}|{top_level_joint}"
                    scene_data_split = scene_data.split(temp_remove_string)

                    if len(scene_data_split) > 1:
                        updated_fileinfo = ",".join(scene_data_split)
                    else:
                        updated_fileinfo = scene_data_split

                    maya.cmds.fileInfo(self.fileinfo_key, updated_fileinfo)

                    # TODO Check that it isn't left with just a "," in the fileinfo

                    print("Updated skeleton_attach fileinfo", maya.cmds.fileInfo(self.fileinfo_key, query=True))

                    # Remove constraints
                    for object in pm.PyNode(f"{driven_ns}:{top_level_joint}").getChildren(ad=True):
                        if pm.objectType(object) == "parentConstraint":
                            pm.delete(object)

    def wipe_relevant_fileinfo(self, are_you_sure=False):
        if are_you_sure:
            maya.cmds.fileInfo(self.fileinfo_key, "")
