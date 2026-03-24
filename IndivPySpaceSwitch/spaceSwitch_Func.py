# -*- coding: utf-8 -*-

from __future__ import print_function

import json
import math
import os
import re

import maya.cmds as cmds
import maya.mel as mel

# ---- Save & Load Preset Data Here ---- #
DEFAULT_PRESET = {
	'palette': 0,
	'paletteColor': [1.000,1.000,1.000],
	'shapeIndexEnabled': False,
	'outlinerIndexEnabled': False,
	'controller': [False, False, True],
	'shapeType': 1,
	'ctrlSize': 2,
	'ctrlLineWidth': -1.0,
	'keySetting': [True, False],
	'fromToData': [0, 200],
	'sampleBy': 1.0
}
ROTATE_ORDER_MAP = {
    "XYZ": 0,
    "YZX": 1,
    "ZXY": 2,
    "XZY": 3,
    "YXZ": 4,
    "ZYX": 5
}
SCRIPT_PRESET_FOLDER_PATH  = cmds.internalVar(userAppDir=True)+'scripts/KF_PresetStore'
SCRIPT_PRESET_PATH = os.path.join(SCRIPT_PRESET_FOLDER_PATH, "KF_SpaceSwitchPreset.json")
returnList = DEFAULT_PRESET.copy()

def _warning(message):
    cmds.warning(message)
    return []

def _safe_delete(nodes):
    nodes = [n for n in (nodes or []) if cmds.objExists(n)]
    if nodes:
        cmds.delete(nodes)

def _safe_progress_end():
    if cmds.progressWindow(q=True, exists=True):
        try:
            cmds.progressWindow(endProgress=True)
        except Exception:
            pass

def _set_locked_hidden(attr):
    if cmds.objExists(attr):
        try:
            cmds.setAttr(attr, lock=True, keyable=False, channelBox=False)
        except Exception:
            pass

def _get_selected_time_range(preset):
    if preset["keySetting"][0]:
        return get_safe_time_range()
    return preset["fromToData"][0], preset["fromToData"][-1]

def _bake_nodes(nodes, min_time, max_time, sample_by=1.0):
    if not nodes:
        return
    cmds.bakeResults(
        nodes,
        time=(min_time, max_time),
        simulation=True,
        hierarchy="none",
        oversamplingRate=1,
        disableImplicitControl=False,
        preserveOutsideKeys=True,
        removeBakedAttributeFromLayer=False,
        bakeOnOverrideLayer=False,
        controlPoints=False,
        shape=True,
        sampleBy=sample_by,
    )

def obtainpresetData():
	if not os.path.exists(SCRIPT_PRESET_PATH):
		cmds.warning("Preset file does not exist.")
		return DEFAULT_PRESET.copy()
	try:
		with open(SCRIPT_PRESET_PATH, "r") as f:
			data = json.load(f)
	except Exception as exc:
		cmds.warning("Failed to load preset file: {}".format(exc))
		return DEFAULT_PRESET.copy()
	preset = DEFAULT_PRESET.copy()
	preset.update(data)
	# ---------- VALIDATION ----------
	# ctrlLineWidth
	lw = preset.get('ctrlLineWidth')
	if not isinstance(lw, (int, float)) or lw < -1:
		preset['ctrlLineWidth'] = DEFAULT_PRESET['ctrlLineWidth']
	# ctrlSize
	size = preset.get('ctrlSize')
	if not isinstance(size, (int, float)) or size <= 0:
		preset['ctrlSize'] = DEFAULT_PRESET['ctrlSize']
	# paletteColor
	col = preset.get('paletteColor')
	if (not isinstance(col, (list, tuple))) or len(col) != 3:
		preset['paletteColor'] = DEFAULT_PRESET['paletteColor']
	return preset

def loadpresetCmd():
    return obtainpresetData()

def get_safe_time_range():
    return (
    	int(math.floor(cmds.playbackOptions(q=True, min=True))),
		int(math.ceil(cmds.playbackOptions(q=True, max=True)))
	)

def ctrlCustomEdit(newName,typeCtrl,shapeCtrl):
	# controllerCurve
	shapeType = {
	0 : lambda :cmds.curve(d=1, n=newName, p=[(-1,0,0),(1,0,0),(0,0,0),(0,0,1),(0,0,-1),(0,0,0),(0,1,0),(0,-1,0)]), #locator
	1 : lambda :cmds.curve(d=1, n=newName, p=[(-0.75,0.75,0.75),(-0.75,0.75,-0.75),(0.75,0.75,-0.75),(0.75,0.75,0.75),(-0.75,0.75,0.75),
											(-0.75,-0.75,0.75),(0.75,-0.75,0.75),(0.75,0.75,0.75),(0.75,-0.75,0.75),(0.75,-0.75,-0.75),
											(0.75,0.75,-0.75),(0.75,-0.75,-0.75),(-0.75,-0.75,-0.75),(-0.75,0.75,-0.75),(-0.75,-0.75,-0.75),
											(-0.75,-0.75,0.75)]), #cube
	2 : lambda :cmds.curve(d=1, n=newName, p=[(0,0,-0.9975),(0.1575,0,-0.9835),(0.308,0,-0.9485),(0.4515,0,-0.889),(0.5845,0,-0.805),
											(0.7035,0,-0.7035),(0.805,0,-0.5845),(0.889,0,-0.4515),(0.9485,0,-0.308),(0.9835,0,-0.1575),
											(0.9975,0,0),(0.9835,0,0.1575),(0.9485,0,0.308),(0.889,0,0.4515),(0.805,0,0.5845),(0.7035,0,0.7035),
											(0.5845,0,0.805),(0.4515,0,0.889),(0.308,0,0.9485),(0.1575,0,0.9835),(0,0,0.9975),(-0.1575,0,0.9835),
											(-0.308,0,0.9485),(-0.4515,0,0.889),(-0.5845,0,0.805),(-0.7035,0,0.7035),(-0.805,0,0.5845),(-0.889,0,0.4515),
											(-0.9485,0,0.308),(-0.9835,0,0.1575),(-0.9975,0,0),(-0.9835,0,-0.1575),(-0.9485,0,-0.308),(-0.889,0,-0.4515),
											(-0.805,0,-0.5845),(-0.7035,0,-0.7035),(-0.5845,0,-0.805),(-0.4515,0,-0.889),(-0.308,0,-0.9485),(-0.1575,0,-0.9835),
											(0,0,-0.9975),(0,0.1575,-0.9835),(0,0.308,-0.9485),(0,0.4515,-0.889),(0,0.5845,-0.805),(0,0.7035,-0.7035),(0,0.805,-0.5845),
											(0,0.889,-0.4515),(0,0.9485,-0.308),(0,0.9835,-0.1575),(0,0.9975,0),(0,0.9835,0.1575),(0,0.9485,0.308),(0,0.889,0.4515),
											(0,0.805,0.5845),(0,0.7035,0.7035),(0,0.5845,0.805),(0,0.4515,0.889),(0,0.308,0.9485),(0,0.1575,0.9835),(0,0,0.9975),
											(0,-0.1575,0.9835),(0,-0.308,0.9485),(0,-0.4515,0.889),(0,-0.5845,0.805),(0,-0.7035,0.7035),(0,-0.805,0.5845),(0,-0.889,0.4515),
											(0,-0.9485,0.308),(0,-0.9835,0.1575),(0,-0.9975,0),(0,-0.9835,-0.1575),(0,-0.9485,-0.308),(0,-0.889,-0.4515),(0,-0.805,-0.5845),
											(0,-0.7035,-0.7035),(0,-0.5845,-0.805),(0,-0.4515,-0.889),(0,-0.308,-0.9485),(0,-0.1575,-0.9835),(0,0,-0.9975),(0,0.1575,-0.9835),
											(0,0.308,-0.9485),(0,0.4515,-0.889),(0,0.5845,-0.805),(0,0.7035,-0.7035),(0,0.805,-0.5845),(0,0.889,-0.4515),(0,0.9485,-0.308),
											(0,0.9835,-0.1575),(0,0.9975,0),(0.1575,0.9835,0),(0.308,0.9485,0),(0.4515,0.889,0),(0.5845,0.805,0),(0.7035,0.7035,0),(0.805,0.5845,0),
											(0.889,0.4515,0),(0.9485,0.308,0),(0.9835,0.1575,0),(0.9975,0,0),(0.9835,-0.1575,0),(0.9485,-0.308,0),(0.889,-0.4515,0),(0.805,-0.5845,0),
											(0.7035,-0.7035,0),(0.5845,-0.805,0),(0.4515,-0.889,0),(0.308,-0.9485,0),(0.1575,-0.9835,0),(0,-0.9975,0),(-0.1575,-0.9835,0),(-0.308,-0.9485,0),
											(-0.4515,-0.889,0),(-0.5845,-0.805,0),(-0.7035,-0.7035,0),(-0.805,-0.5845,0),(-0.889,-0.4515,0),(-0.9485,-0.308,0),(-0.9835,-0.1575,0),
											(-0.9975,0,0),(-0.9835,0.1575,0),(-0.9485,0.308,0),(-0.889,0.4515,0),(-0.805,0.5845,0),(-0.7035,0.7035,0),(-0.5845,0.805,0),(-0.4515,0.889,0),
											(-0.308,0.9485,0),(-0.1575,0.9835,0),(0,0.9975,0)]), #sphere
	3 : lambda :cmds.curve(d=1, n=newName, p=[(0,1,0),(1,0,0),(0,0,1),(-1,0,0),(0,0,-1),(0,1,0),(0,0,1),(0,-1,0),(0,0,-1),(1,0,0),(0,1,0),(-1,0,0),(0,-1,0),(1,0,0)]), #rhombus
	4 : lambda :cmds.curve(d=1, n=newName, p=[(0,0.75,-0.786),(0.123,0.75,-0.777),(0.243,0.75,-0.747),(0.357,0.75,-0.699),
											(0.462,0.75,-0.636),(0.555,0.75,-0.555),(0.636,0.75,-0.462),(0.699,0.75,-0.357),(0.747,0.75,-0.243),(0.777,0.75,-0.123),
											(0.786,0.75,0),(0.777,0.75,0.123),(0.747,0.75,0.243),(0.699,0.75,0.357),(0.636,0.75,0.462),(0.555,0.75,0.555),
											(0.462,0.75,0.636),(0.357,0.75,0.699),(0.243,0.75,0.747),(0.123,0.75,0.777),(0,0.75,0.786),(-0.123,0.75,0.777),
											(-0.243,0.75,0.747),(-0.357,0.75,0.699),(-0.462,0.75,0.636),(-0.555,0.75,0.555),(-0.636,0.75,0.462),(-0.699,0.75,0.357),
											(-0.747,0.75,0.243),(-0.777,0.75,0.123),(-0.786,0.75,0),(-0.777,0.75,-0.123),(-0.747,0.75,-0.243),(-0.699,0.75,-0.357),
											(-0.636,0.75,-0.462),(-0.555,0.75,-0.555),(-0.462,0.75,-0.636),(-0.357,0.75,-0.699),(-0.243,0.75,-0.747),(-0.123,0.75,-0.777),
											(0,0.75,-0.786),(0,-0.75,-0.786),(0.123,-0.75,-0.777),(0.243,-0.75,-0.747),(0.357,-0.75,-0.699),(0.462,-0.75,-0.636),
											(0.555,-0.75,-0.555),(0.555,0.75,-0.555),(0.555,-0.75,-0.555),(0.636,-0.75,-0.462),(0.699,-0.75,-0.357),(0.747,-0.75,-0.243),
											(0.777,-0.75,-0.123),(0.786,-0.75,0),(0.786,0.75,0),(0.786,-0.75,0),(0.777,-0.75,0.123),(0.747,-0.75,0.243),
											(0.699,-0.75,0.357),(0.636,-0.75,0.462),(0.555,-0.75,0.555),(0.555,0.75,0.555),(0.555,-0.75,0.555),(0.462,-0.75,0.636),
											(0.357,-0.75,0.699),(0.243,-0.75,0.747),(0.123,-0.75,0.777),(0,-0.75,0.786),(0,0.75,0.786),(0,-0.75,0.786),
											(-0.123,-0.75,0.777),(-0.243,-0.75,0.747),(-0.357,-0.75,0.699),(-0.462,-0.75,0.636),(-0.555,-0.75,0.555),
											(-0.555,0.75,0.555),(-0.555,-0.75,0.555),(-0.636,-0.75,0.462),(-0.699,-0.75,0.357),(-0.747,-0.75,0.243),
											(-0.777,-0.75,0.123),(-0.786,-0.75,0),(-0.786,0.75,0),(-0.786,-0.75,0),(-0.777,-0.75,-0.123),(-0.747,-0.75,-0.243),
											(-0.699,-0.75,-0.357),(-0.636,-0.75,-0.462),(-0.555,-0.75,-0.555),(-0.555,0.75,-0.555),(-0.555,-0.75,-0.555),
											(-0.462,-0.75,-0.636),(-0.357,-0.75,-0.699),(-0.243,-0.75,-0.747),(-0.123,-0.75,-0.777),(0,-0.75,-0.786)]) #cylinder
	}
	ctrlType = {
	0: lambda: cmds.spaceLocator(n=newName)[0],
	1: lambda: cmds.group(n=newName,em=True), #unicode
	2: shapeType[shapeCtrl] 
	}

	ctrlCreate = ctrlType[typeCtrl]()
	shape_children = cmds.listRelatives(ctrlCreate, children=True, type="shape") or []
	for index, child in enumerate(shape_children, start=1):
		desired_name = "{}Shape".format(ctrlCreate) if len(shape_children) == 1 else "{}Shape{}".format(ctrlCreate, index)
		cmds.rename(child, desired_name)
	return ctrlCreate

def ctrlSettingFunc(sel,rotOrder,preset=None):
	preset = preset or loadpresetCmd()
	ctrlList = []
	
	shape_type = int(preset["shapeType"]) - 1
	ctrl_type_flags = preset["controller"]
	index_color = preset["paletteColor"]
	use_shape_color = bool(preset["shapeIndexEnabled"])
	use_outliner_color = bool(preset["outlinerIndexEnabled"])
	ctrl_size = float(preset["ctrlSize"])
	ctrl_line_width = float(preset["ctrlLineWidth"])
	
	for ctrl_mode, is_enabled in enumerate(ctrl_type_flags):
		if not is_enabled:
			continue

		newCreatedName = "{}_locBake_{}".format(sel,rotOrder)
		newName = ctrlCustomEdit(newCreatedName,ctrl_mode,shape_type)
		ctrlList.append(newName)
		shape_nodes = cmds.listRelatives(newName, children=True, type="shape") or []
		first_shape = shape_nodes[0] if shape_nodes else None
		
		if use_shape_color and ctrl_mode != 1 and first_shape:
			cmds.setAttr("{}.overrideEnabled".format(first_shape), 1)
			cmds.setAttr("{}.overrideRGBColors".format(first_shape), 1)
			cmds.setAttr("{}.overrideColorRGB".format(first_shape),index_color[0],index_color[1],index_color[2],)
		if use_outliner_color:
			cmds.setAttr("{}.useOutlinerColor".format(newName), 1)
			cmds.setAttr("{}.outlinerColor".format(newName),index_color[0],index_color[1],index_color[2],)
		if ctrl_mode in (0, 2):
			for axis in ("sx", "sy", "sz"):
				cmds.setAttr("{}.{}".format(newName, axis), ctrl_size)
			if ctrl_mode == 2 and first_shape and ctrl_line_width >= 0:
				cmds.setAttr("{}.lineWidth".format(first_shape), ctrl_line_width)
		_set_locked_hidden("{}.v".format(newName))
	return ctrlList

def confirmExistingLocators(selList, rotateOrder):
    existingList = []
    for sel in selList:
        newCreatedName = "{}_locBake_{}".format(sel, rotateOrder)
        if cmds.objExists(newCreatedName):
            existingList.append(newCreatedName)
    if not existingList:
        return True, []   # nothing exists, safe to continue
    msg = "These locator(s) already exist:\n\n"
    msg += "\n".join(existingList)
    msg += "\n\nThese locators already exist and will be skipped. Continue creating only the missing ones?"
    result = cmds.confirmDialog(
        title="Object Already Exists",
        message=msg,
        button=["Yes", "No"],
        defaultButton="No",
        cancelButton="No",
        dismissString="No"
    )
    return (result == "Yes"), existingList

#    ____________________
# __/__FunctionColumn __/__
# Modify so every button will share the same function 
def createLocatorSingle(rotateOrder):
	preset = loadpresetCmd()
	objectsel = cmds.ls(sl=True) or []
	if not objectsel:
		return _warning("SELECT A CONTROLLER TO FUNCTION")
	proceed, _ = confirmExistingLocators(objectsel, rotateOrder) # Do not use exitingList
	if not proceed:
		return _warning("This step is cancel")
	# only keep non-existing objects for creation
	buildList = []
	existingList = []
	for obj in objectsel:
		locName = "{}_locBake_{}".format(obj, rotateOrder)
		if not cmds.objExists(locName):
			buildList.append(obj)
		else:
			existingList.append(obj)
	if not buildList:
		if existingList:
			cmds.select(existingList,r=True)
		return _warning("All selected locators already exist. Nothing to create.")

	min_time, max_time = _get_selected_time_range(preset)
	sample_data = preset["sampleBy"]

	createdCtrls = []
	tempConstraints = []
	ctrlObjPairs = []
	cancelled = False
	total_steps = len(buildList) * 2
	
	def _cleanup():
		try:
			if cmds.progressWindow(q=True, exists=True):
				cmds.progressWindow(endProgress=True)
		except Exception:
			pass
		try:
			cmds.refresh(suspend=False)
		except Exception:
			pass
		try:
			cmds.refresh()
		except Exception:
			pass

	cmds.undoInfo(openChunk=True)
	_cleanup()
	cmds.progressWindow(title='Working...',progress=0,maxValue=total_steps,status='Progress : 0%',isInterruptable=True)
	cmds.refresh(force=True)
	# Create controllers #
	try:
		for index,obj in enumerate(buildList,start=1):
			if cmds.progressWindow(q=True,isCancelled=True):
				cancelled = True
				break
			ctrlList = ctrlSettingFunc(obj,rotateOrder)
			if not ctrlList:
				continue
			ctrl = ctrlList[0]
			createdCtrls.append(ctrl)
			ctrlObjPairs.append((ctrl,obj))

			prtCnt = cmds.parentConstraint(obj, ctrl, mo=False)[0]
			cmds.setAttr("{}.rotateOrder".format(ctrl), ROTATE_ORDER_MAP[rotateOrder])
			tempConstraints.append(prtCnt)
			cmds.progressWindow(e=True,progress=index,status='Preparing : {}%'.format(int((float(index) / total_steps ) * 100)))
		if createdCtrls and not cancelled:
			cmds.progressWindow(e=True,status='Baking all locators...')
			_bake_nodes(createdCtrls, min_time, max_time, sample_data)
		
		_safe_delete(tempConstraints)
		tempConstraints = []

		for index,(ctrl,obj) in enumerate(ctrlObjPairs, start=1):
			if cmds.progressWindow(q=True, isCancelled=True):
				cancelled = True
				break
			cmds.parentConstraint(ctrl,obj,mo=True)
			animCurves = cmds.listConnections(ctrl, d=False, type='animCurve') or []
			if animCurves:
				cmds.filterCurve(animCurves)
			current_step = len(buildList) + index
			cmds.progressWindow(e=True,progress=current_step,status='Finishing : {}%'.format(int((float(current_step) / total_steps ) * 100)))
	finally:
		_cleanup()
		cmds.progressWindow(endProgress=True)
		cmds.undoInfo(closeChunk=True)
	if cancelled:
		return []
	if createdCtrls:
		mel.eval('print("RESULT: <{}> locator CREATED\\n")'.format(len(createdCtrls)))	
	return createdCtrls

def createLocatorDouble(rotateOrder):
	preset = loadpresetCmd()
	objectsel = cmds.ls(sl=True)
	if not objectsel:
		return _warning("SELECT A CONTROLLER TO FUNCTION")
	
	proceed, _ = confirmExistingLocators(objectsel, rotateOrder)
	if not proceed:
		return _warning("This step is cancel")
	
	# keep only items whose locator does not already exist
	buildList = []
	existingList = []
	for obj in objectsel:
		locName = "{}_locBake_{}".format(obj, rotateOrder)
		if cmds.objExists(locName):
			existingList.append(obj)
		else:
			buildList.append(obj)
	if not buildList:
		if existingList:
			cmds.select(existingList,r=True)
		return _warning("All selected locators already exist. Nothing to create.")

	min_time, max_time = _get_selected_time_range(preset)
	sample_data = preset["sampleBy"]

	createdCtrls = []
	tempConstraints = []
	ctrlObjPairs = []
	cancelled = False
	total_steps = len(buildList) * 2

	cmds.undoInfo(openChunk=True)
	cmds.refresh(suspend=True)
	_safe_progress_end()
	cmds.progressWindow(title='Working...',progress=0,maxValue=total_steps,status='Progress : 0%',isInterruptable=True)
	cmds.refresh(force=True)

	try:
		for index,obj in enumerate(buildList, start=1):
			if cmds.progressWindow(q=True,isCancelled=True):
				cancelled = True
				break
			
			ctrlList = ctrlSettingFunc(obj,rotateOrder,preset)
			if not ctrlList:
				cancelled = True
				return []

			ctrl = ctrlList[0]
			prtCnt = cmds.parentConstraint(obj, ctrl, mo=False)[0]
			cmds.delete(prtCnt)
			cmds.setAttr("{}.rotateOrder".format(ctrl),ROTATE_ORDER_MAP[rotateOrder])
			
			ctrlChild = cmds.duplicate(ctrl,n="{}_child".format(ctrl))[0]
			cmds.parent(ctrlChild,ctrl)
			for attr in ['tx', 'ty', 'tz', 'rx', 'ry', 'rz']:
				cmds.setAttr("{}.{}".format(ctrlChild, attr), 0)

			prtChildCnt = cmds.parentConstraint(obj, ctrlChild, mo=True)[0]

			createdCtrls.append(ctrlChild)
			ctrlObjPairs.append((ctrlChild,obj))
			tempConstraints.append(prtChildCnt)

			cmds.progressWindow(e=True,progress=index,status='Creating : {}%'.format(int((float(index) / total_steps) * 100)))

		if createdCtrls and not cancelled:
			cmds.progressWindow(e=True,status='Baking all locators...')
			_bake_nodes(createdCtrls, min_time, max_time, sample_data)
		
		_safe_delete(tempConstraints)
		tempConstraints = []
		
		for index,(ctrlChild,obj) in enumerate(ctrlObjPairs, start=1):
			if cmds.progressWindow(q=True, isCancelled=True):
				cancelled = True
				break
			cmds.orientConstraint(ctrlChild,obj,mo=True)
			animCurves = cmds.listConnections(ctrlChild, d=False, type='animCurve') or []
			if animCurves:
				cmds.filterCurve(animCurves)
			cmds.progressWindow(e=True,progress=index,status='Finishing : {}%'.format(int((float(index) / len(ctrlObjPairs)) * 100)))
	finally:
		_safe_progress_end()
		cmds.progressWindow(endProgress=True)
		cmds.refresh(suspend=False)
		cmds.undoInfo(closeChunk=True)
	if cancelled:
		return [] 
	if createdCtrls:
		mel.eval('print("RESULT: <{}> locator CREATED\\n")'.format(len(createdCtrls)))	
	return createdCtrls

#=========================================================================================================================================
#    _________________________
# __/__ManualLocator SETUP __/__
def pivRot(obj):
	if cmds.objectType(obj) in ("transform", "joint"):                             
		piv= cmds.xform(obj, q=1, rp=1, ws=1)
		rot = cmds.getAttr("{}.rotate".format(obj))[0]
		rotOr= cmds.getAttr("{}.rotateOrder".format(obj))
	elif cmds.objectType(obj) in ("mesh", "nurbsCurve", "nurbsSurface"):  
		tempPiv= cmds.exactWorldBoundingBox(obj)
		piv = [
            round((tempPiv[0] + tempPiv[3]) / 2.0, 3),
            round((tempPiv[1] + tempPiv[4]) / 2.0, 3),
            round((tempPiv[2] + tempPiv[5]) / 2.0, 3),
        ]
		rot= [0,0,0]
		rotOr= 0 # xyz
	else:
		raise RuntimeError("Unsupported object type for pivRot: {}".format(obj))
	return piv, rot, rotOr

def pivCent(objects):
    px, py, pz = [], [], []
    for each in objects:
        piv, _, _ = pivRot(each)
        px.append(piv[0])
        py.append(piv[1])
        pz.append(piv[2])
    return [
        round((min(px) + max(px)) / 2, 3),
        round((min(py) + max(py)) / 2, 3),
        round((min(pz) + max(pz)) / 2, 3),
    ]

def clean_name(name):
    return re.sub("_+", "_", name).strip("_")

def clean_name_keep_namespace(obj_name):
    if ":" in obj_name:
        ns, base = obj_name.rsplit(":", 1)
        return "{}:{}".format(ns, clean_name(base))
    return clean_name(obj_name)

def createLocatorManual(rotOrder):
	preset = loadpresetCmd()
	sel_objs  = cmds.ls(sl=True) or []
	if not sel_objs :
		return _warning("SELECT SOMETHING TO FUNCTION")
	cmds.undoInfo(openChunk=True)
	createdCtrls = []
	try:
		center_piv = pivCent(sel_objs)
		ctrlList = ctrlSettingFunc(sel_objs[0], rotOrder, preset)  # just pass first selection
		if not ctrlList:
			return []

		ctrl = ctrlList[0]
		cmds.xform(ctrl, ws=True, t=center_piv)
		cmds.matchTransform(ctrl, sel_objs[0], rot=True)
		cmds.setAttr("{}.rotateOrder".format(ctrl), ROTATE_ORDER_MAP[rotOrder])
		ctrl = cmds.rename(ctrl,"{}_Manual".format(clean_name_keep_namespace(ctrl)))
		createdCtrls.append(ctrl)
		mel.eval('print("RESULT: <{}> locator CREATED\\n")'.format(ctrl))
	finally:
		cmds.undoInfo(closeChunk=True)
	return createdCtrls

def LocManualBake():
    preset = loadpresetCmd()
    minTime, maxTime = get_safe_time_range()
    locBakeAXYZ = cmds.ls(sl=True) or []
    if not locBakeAXYZ:
        return _warning("Please select locator(s) to bake")

    createdCtrls = []
    tempConstraints = []
    ctrlObjPairs = []

    cmds.undoInfo(openChunk=True)
    cmds.refresh(suspend=True)
    _safe_progress_end()
    cmds.progressWindow(title='Baking Manual Locators',
                        progress=0,
                        maxValue=len(locBakeAXYZ),
                        status='Progress : 0%',
                        isInterruptable=True)
    try:
        for i, each in enumerate(locBakeAXYZ, start=1):
            if cmds.progressWindow(q=True, isCancelled=True):
                break

            parts = each.split(":")
            ns = parts[0] if len(parts) > 1 else ""
            base_name = parts[-1]

            # check suffix pattern
            if not re.match(r".*_locBake_.*_Manual$", base_name):
                cmds.warning("Selection locator suffix different, please check the naming: {}".format(each))
                continue

            # rebuild source object (with namespace if exists)
            source_base = base_name.split("_locBake_")[0]
            source = "{}:{}".format(ns, source_base) if ns else source_base
            prtCnt = cmds.parentConstraint(source, each, mo=True)

            createdCtrls.append(each)
            ctrlObjPairs.append((each, source))
            tempConstraints.append(prtCnt[0])

        _bake_nodes(createdCtrls, minTime, maxTime, preset["sampleBy"])
        _safe_delete(tempConstraints)

        for i, (each, source) in enumerate(ctrlObjPairs, start=1):
            if cmds.progressWindow(q=True, isCancelled=True):
                break

            cmds.parentConstraint(each, source, mo=True)
            animCurves = cmds.listConnections(each, d=False, type='animCurve')
            if animCurves:
                cmds.filterCurve(animCurves)

            for attr in ['sx', 'sy', 'sz', 'v']:
                _set_locked_hidden("{}.{}".format(each, attr))

            cmds.progressWindow(e=True,
                                progress=i,
                                status='Progress : {}%'.format(int((float(i) / len(locBakeAXYZ)) * 100)))
            mel.eval('print("RESULT: <{}> locator bake complete\\n")'.format(each))
    finally:
        _safe_progress_end()
        cmds.progressWindow(endProgress=True)
        cmds.refresh(suspend=False)
        cmds.undoInfo(closeChunk=True)

    return createdCtrls

#    _____________________________
# __/__ManualLocator SETUP END __/__
#=========================================================================================================================================

#=========================================================================================================================================
#    _______________________________
# __/__AnimationLayer SETUP START__/__
# Select object from layers
def selectObjectsFromLayers(anim_layers):
	objects = set()
	for anim_layer in anim_layers:
		attrs = cmds.animLayer(anim_layer, q=True, attribute=True) or []
		for attr in attrs:
			objects.add(attr.split('.', 1)[0])
	objects = list(objects)
	if objects:
		cmds.select(objects)
	return objects

def getAllLayers(depth=0):
	root = cmds.animLayer(q=True,r=True)
	if not root:
		return []
	result = []
	def walk(layer):
		children = cmds.animLayer(layer,q=True,children=True) or []
		for child in children:
			result.append(child)
			walk(child)
	walk(root)
	return result

def checkEmptyAnimLayerAllTheWay(layer):
    if cmds.animLayer(layer, q=True, attribute=True):
        return False
    children = cmds.animLayer(layer, q=True, children=True) or []
    return all(checkEmptyAnimLayerAllTheWay(c) for c in children)

def deleteEmptyLayers():
    allLayers = getAllLayers()
    if not allLayers:
        return
    toDelete = [l for l in allLayers if checkEmptyAnimLayerAllTheWay(l)]
    if toDelete:
        cmds.delete(toDelete)

def removeFromAnimLayer(node):
    cmds.select(node)
    affected = cmds.animLayer(q=True, affectedLayers=True) or []
    if not affected:
        mel.eval('print ("REMINDER : {} does not belong to any animation layer\\n")'.format(node))
        return
    root = cmds.animLayer(q=True, root=True)
    if root in affected:
        affected.remove(root)
    
    attrs = cmds.listAttr(node, keyable=True) or []
    attrs = ["{}.{}".format(node, a) for a in attrs]
    locked = cmds.listAttr(node, locked=True, keyable=True) or []
    locked = {"{}.{}".format(node, a) for a in locked}
    attrs = [a for a in attrs if a not in locked]
    
    for layer in affected:
        cmds.animLayer(layer, e=True, removeAttribute=attrs)
    
    if cmds.animLayer(q=True, affectedLayers=True):
        cmds.warning("got error")
    else:
        mel.eval('print ("REMINDER : {} Animation Layers merged\\n")'.format(node))

# Get back target constraint list
def getTargetConstraint(sel):
    cons = cmds.listConnections(sel, type='constraint', plugs=True) or []
    return list({c.split('.', 1)[0] for c in cons if '.targetParentMatrix' in c})

def getActualTarget(sel):
    if not cmds.objExists(sel):
        return []

    driven = set()
    constraints = cmds.listConnections(sel, type='constraint') or []
    for con in constraints:
        # get all downstream connections from the constraint
        outputs = cmds.listConnections(con, s=False, d=True) or []
        for out in outputs:
            if cmds.objExists(out) and cmds.nodeType(out) == 'transform':
                if out != sel:  # skip the constrained object itself
                    driven.add(out)
    return list(driven)

def filterTransforms(nodes):
    return [n for n in nodes if cmds.objExists(n) and cmds.nodeType(n) == 'transform']

def getPairDrivenTarget(sel):
    if not cmds.objExists(sel):
        return []

    final_drivers = set()
    constraints = cmds.listConnections(sel, type='constraint') or []
    for con in constraints:
        downstream = cmds.listConnections(con, s=False, d=True) or []
        for node in downstream:
            if not cmds.objExists(node):
                continue
            node_type = cmds.nodeType(node)
            if node_type == 'pairBlend':
                # follow pairBlend output to find the actual transform
                pairblend_outputs = cmds.listConnections(node, s=False, d=True) or []
                for out in pairblend_outputs:
                    if cmds.objExists(out) and cmds.nodeType(out) == 'transform':
                        final_drivers.add(out)
    return list(final_drivers)
#    _____________________________
# __/__AnimationLayer SETUP END__/__
#=========================================================================================================================================
def bakeFunction(progressBar=None):
	preset = loadpresetCmd()
	selectionReplacesNew = []
	bakePairs = []
	deletedTargets = set()

	sels = cmds.ls(sl=True) or []
	if not sels:
		return cmds.warning("SELECT OBJECT TO BAKE ANIMATION")

	min_time, max_time = _get_selected_time_range(preset)
	sample_data = preset["sampleBy"]

	for obj in sels:
		targets = getActualTarget(obj)
		if not targets:
			targets = getPairDrivenTarget(obj)
		if not targets:
			continue

		targets = filterTransforms(targets)
		for source in targets:
			bakePairs.append((source,obj))
			selectionReplacesNew.append(source)

	if not selectionReplacesNew:
		return cmds.warning("NO CONSTRAINT SOURCES FOUND TO BAKE ANIMATION")

	total = len(bakePairs)
	if not total:
		return cmds.warning("No valid transforms to bake.")
	
	if progressBar and cmds.progressBar(progressBar, exists=True):
		cmds.progressBar(progressBar, e=True, progress=0)
	
	cmds.undoInfo(openChunk=True)
	cmds.refresh(suspend=True)
	
	try:
		for i, (source, target) in enumerate(bakePairs,1):
			_bake_nodes([source], min_time, max_time, sample_data)

			if cmds.objExists(target) and target not in deletedTargets:
				cmds.delete(target)
				deletedTargets.add(target)
				removeFromAnimLayer(source)

			if progressBar and cmds.progressBar(progressBar, exists=True):
				percent = int((float(i) / total) * 100)
				cmds.progressBar(progressBar, e=True, progress=percent)
	finally:
		if progressBar and cmds.progressBar(progressBar, exists=True):
			cmds.progressBar(progressBar, e=True, progress=100)
		cmds.refresh(suspend=False)
		cmds.undoInfo(closeChunk=True)

	deleteEmptyLayers()

	selectionReplacesNew = [obj for obj in selectionReplacesNew if cmds.objExists(obj)]
	if selectionReplacesNew:
		cmds.select(selectionReplacesNew)
		showBakeCompleteWindow(selectionReplacesNew)
	return selectionReplacesNew

def showBakeCompleteWindow(objects):
	if not objects:
		return
	num = len(objects)
	win = "ControllerBake_List"
	if cmds.window(win, exists=True):
		cmds.deleteUI(win)
	window = cmds.window(win, title="Bake Complete", widthHeight=(400, 200))
	form = cmds.formLayout()
	frame = cmds.frameLayout(label="[{}] Objects baked successfully".format(num),marginWidth=10,marginHeight=10, bgc=(0.2, 0.35, 0.2))
	scroll = cmds.textScrollList(allowMultiSelection=True,append=objects,dcc=lambda *_: cmds.select(cmds.textScrollList(scroll, q=True, selectItem=True)))
	cmds.formLayout(form, e=True,attachForm=[(frame, 'top', 5),(frame, 'bottom', 5),(frame, 'left', 5),(frame, 'right', 5)])
	cmds.showWindow(window)
	mel.eval('print ("REMINDER : Selection COMPLETE BAKE :D\\n")')

def setupFunction():
	cmds.refresh(suspend=True) # Off
	try:
		baked_list = bakeFunction()
		if baked_list:
			cmds.select(baked_list)
			mel.eval( 'print ("\\nREMINDER : SpaceSwitch <CREATED> \\n")')
	except Exception as exc:
		cmds.refresh(suspend=False)
		cmds.error("Error during the Bake: {}".format(exc))
	finally:
		try:
			cmds.refresh(suspend=False)
		except Exception:
			pass
