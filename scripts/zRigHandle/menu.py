import maya.cmds as cmds
import maya.mel as mel

# Thanks to https://github.com/chadmv/cvwrap/ for showing how to add items to a menu
# in the right place.  Angry glares to Autodesk for having a menu API so bad that
# you need to find third-party example code just to add items to it.
menuItems = []
def createMenuItems():
    global menuItems
    if menuItems:
        return

    mel.eval('ModCreateMenu "mainCreateMenu"')
    menu = 'mainCreateMenu'
    for item in cmds.menu(menu, q=True, ia=True):
        if cmds.menuItem(item, q=True, divider=True):
            section = cmds.menuItem(item, q=True, label=True)

        menuLabel = cmds.menuItem(item, q=True, label=True)
        if menuLabel == 'Locator' and section == 'Construction Aids':
            create = cmds.menuItem(label="Rig Handle", command=create_zRigHandle, sourceType='python', insertAfter=item, parent=menu)
            menuItems.append(create)

def create_zRigHandle(arg):
    cmds.loadPlugin('zRigHandle', quiet=True)
    sel = cmds.ls(sl=True)
    return cmds.createNode('zRigHandle')

