"""
This is a script to take two input skeletons and constrain the second to the first
In my personal pipeline, this is used to make a skeleton from my hair driven scene follow my animation skeleton,
    or to have a separate clothing skeleton follow the main skeleton
"""

# SYSTEM IMPORTS

# STANDARD LIB IMPORTS
import maya.cmds
import pymel.core as pm

# LOCAL APP IMPORTS


class SkeletonConnectorFunctional():
    def __init__(self):
        self.WORLD_OBJ_NAME = "SKEL_CONNECTOR"
        self.attrs = ["tx", "ty", "tz", "rx", "ry", "rz", "sx", "sy", "sz"]
        self.ensure_scene_setup()

    def ensure_scene_setup(self):
        if not pm.objExists(self.WORLD_OBJ_NAME):
            pm.createNode(pm.nt.Transform, name=self.WORLD_OBJ_NAME)
        pm.PyNode(self.WORLD_OBJ_NAME).hiddenInOutliner.set(1)

        return None

    def skeleton_attach(self, rig_ns: str, driven_ns: str, top_level_joint: str) -> None:
        self.ensure_scene_setup()

        rig_tlj = f"{rig_ns}:{top_level_joint}"

        rig_joints = maya.cmds.listRelatives(rig_tlj, children=True, allDescendents=True)
        rig_joints.insert(0, rig_tlj)

        for x in rig_joints:
            joint_name = x.split(":")[1]
            driven = f"{driven_ns}:{joint_name}"
            driver = x
            for attr in self.attrs:
                try:
                    pm.connectAttr(f"{driver}.{attr}", f"{driven}.{attr}")
                except RuntimeError:
                    pass
            print(f"Connected TRS of {driver} to {driven}")

        new_info = f"{driven_ns}:{rig_ns}:{top_level_joint}"
        pm.addAttr(self.WORLD_OBJ_NAME, longName=f"SA_{driven_ns}_{top_level_joint}", attributeType="enum", en=new_info)

        print(f"full info: {new_info}")

        return None

    def load_scene_constraint_data(self):
        tool_attr_names = [i for i in pm.listAttr(self.WORLD_OBJ_NAME) if i.startswith("SA_")]

        sorted_scene_data = []

        for attr in tool_attr_names:
            enum_str = pm.attributeQuery(attr, node=self.WORLD_OBJ_NAME, listEnum=True)[0]
            enum_arr = enum_str.split(":")
            driven, driver, tlj = enum_arr[0], enum_arr[1], enum_arr[2]

            sorted_scene_data.append(f"{driven}  <--  {driver}  (tlj:{tlj})")

        return sorted_scene_data

    def skeleton_detach(self, rig_ns: str, driven_ns: str, top_level_joint: str):
        self.ensure_scene_setup()

        pm.deleteAttr(self.WORLD_OBJ_NAME, attribute=f"SA_{rig_ns}_{top_level_joint}")
        for obj in pm.PyNode(f"{driven_ns}:{top_level_joint}").getChildren(ad=True):
            for attr in ["tx", "rx", "sx"]:
                pm.disconnectAttr(obj, attr)

        return None
