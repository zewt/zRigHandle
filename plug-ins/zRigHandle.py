import sys
import ctypes
import maya.api.OpenMaya as om
import maya.api.OpenMayaUI as omui
import maya.api.OpenMayaAnim as oma
import maya.api.OpenMayaRender as omr

# This is insane.  There are two Python APIs in Maya, and both of them are missing lots of
# stuff, and you can't mix them except in specific careful ways.
import maya.OpenMayaRender as v1omr
glRenderer = v1omr.MHardwareRenderer.theRenderer()
glFT = glRenderer.glFunctionTable()

def maya_useNewAPI():
        """
        The presence of this function tells Maya that the plugin produces, and
        expects to be passed, objects created using the Maya Python API 2.0.
        """
        pass

# Be careful when changing the order of these shapes.  Their index is the value of the .shape
# enum, so this affects the file format.
shapes = []
shapes.append({
    'name': 'Pyramid',
    'geometry': [{
        'type': 'quad',
        'data': [
            (-0.5, -0.333, +0.5),
            (+0.5, -0.333, +0.5),
            (+0.5, -0.333, -0.5),
            (-0.5, -0.333, -0.5),
        ],
    }, {
        'type': omr.MGeometry.kTriangles,
        'data': [
            (-0.5, -0.333, +0.5),
            (-0.5, -0.333, -0.5),
            (+0.0, +0.666, -0.0),

            (+0.5, -0.333, +0.5),
            (+0.5, -0.333, -0.5),
            (+0.0, +0.666, -0.0),

            (-0.5, -0.333, -0.5),
            (+0.5, -0.333, -0.5),
            (+0.0, +0.666, -0.0),

            (+0.5, -0.333, +0.5),
            (-0.5, -0.333, +0.5),
            (+0.0, +0.666, -0.0),
        ]
    }]
})

def _make_ball():
    points = []
    p1 = (1.0) / 2.0
    p2 = (0.5) / 2.0
    for x in (1,-1):
        points.append((x*p1, -p2, -p2))
        points.append((x*p1, +p2, -p2))
        points.append((x*p1, +p2, +p2))
        points.append((x*p1, -p2, +p2))

        points.append((-p2, x*p1, -p2))
        points.append((+p2, x*p1, -p2))
        points.append((+p2, x*p1, +p2))
        points.append((-p2, x*p1, +p2))

        points.append((-p2, -p2, x*p1))
        points.append((+p2, -p2, x*p1))
        points.append((+p2, +p2, x*p1))
        points.append((-p2, +p2, x*p1))

        for y in (1,-1):
            points.append((-p2, x*+p2, y*+p1))
            points.append((+p2, x*+p2, y*+p1))
            points.append((+p2, x*+p1, y*+p2))
            points.append((-p2, x*+p1, y*+p2))

            points.append((x*+p2, -p2, y*+p1))
            points.append((x*+p2, +p2, y*+p1))
            points.append((x*+p1, +p2, y*+p2))
            points.append((x*+p1, -p2, y*+p2))

            points.append((x*+p2, y*+p1, -p2))
            points.append((x*+p2, y*+p1, +p2))
            points.append((x*+p1, y*+p2, +p2))
            points.append((x*+p1, y*+p2, -p2))

    result = [{
        'type': 'quad',
        'data': points,
    }]

    tris = []
    for x in (1, -1):
        for y in (1, -1):
            for z in (1, -1):
                tris.append((x*-p1, y*-p2, z*p2))
                tris.append((x*-p2, y*-p1, z*p2))
                tris.append((x*-p2, y*-p2, z*p1))
    
    result.append({
        'type': omr.MGeometry.kTriangles,
        'data': tris,
    })

    return result

shapes.append({
    'name': 'Ball',
    'geometry': _make_ball()
})

for shape in shapes:
    for item in shape['geometry']:
        item['data'] = [om.MPoint(*v) for v in item['data']]

def getShapeBounds(shape):
    boundingBox = om.MBoundingBox()
    for item in shape:
        for point in item['data']:
            boundingBox.expand(point)

    return boundingBox

def _transformShape(shape, transform):
    result = []
    for item in shape:
        transformed = {key: value for key, value in item.items()}
        result.append(transformed)
        transformed['data'] = [v*transform for v in transformed['data']]

    return result

def _getTransform(node):
    transformPlug = om.MPlug(node, zRigHandle.transformAttr)
    transform = om.MFnMatrixData(transformPlug.asMObject()).matrix()

    sizePlug = om.MPlug(node, zRigHandle.scaleAttr)
    size = om.MFnNumericData(sizePlug.asMObject()).getData()

    mat = om.MTransformationMatrix(transform)
    mat.scaleBy(size, om.MSpace.kObject)

    return mat.asMatrix()

class zRigHandle(om.MPxSurfaceShape):
        id = om.MTypeId(0x124743)
        drawDbClassification = "drawdb/geometry/zRigHandle"
        drawRegistrantId = "zRigHandlePlugin"

        def __init__(self):
                om.MPxSurfaceShape.__init__(self)

        @classmethod
        def creator(cls):
                return cls()

        @classmethod
        def initialize(cls):
                nAttr = om.MFnNumericAttribute()
                enumAttr = om.MFnEnumAttribute()
                matAttr = om.MFnMatrixAttribute()

                cls.shapeAttr = enumAttr.create('shape', 'sh', 0)
                for idx, shape in enumerate(shapes):
                    enumAttr.addField(shape['name'], idx)
                enumAttr.channelBox = True

                cls.addAttribute(cls.shapeAttr)

                cls.transformAttr = matAttr.create('transform', 't', om.MFnMatrixAttribute.kFloat)
                cls.addAttribute(cls.transformAttr)

                scaleX = nAttr.create('sizeX', 'sx', om.MFnNumericData.kFloat, 1)
                scaleY = nAttr.create('sizeY', 'sy', om.MFnNumericData.kFloat, 1)
                scaleZ = nAttr.create('sizeZ', 'sz', om.MFnNumericData.kFloat, 1)

                cls.scaleAttr = nAttr.create('scale', 's', scaleX, scaleY, scaleZ)
                nAttr.channelBox = True
                nAttr.keyable = True
                cls.addAttribute(cls.scaleAttr)

                cls.colorAttr = nAttr.createColor('color', 'dc')
                nAttr.default = (.38,0,0.02)
                cls.addAttribute(cls.colorAttr)

                cls.alphaAttr = nAttr.create('alpha', 'a', om.MFnNumericData.kFloat, 0.333)
                nAttr.setSoftMin(0)
                nAttr.setSoftMax(1)
                cls.addAttribute(cls.alphaAttr)

        def postConstructor(self):
                self.isRenderable = True

        def setDependentsDirty(self, plug, affectedPlugs):
                if plug.isChild:
                    plug = plug.parent()

                if plug in (zRigHandle.transformAttr, zRigHandle.shapeAttr, zRigHandle.scaleAttr,
                    zRigHandle.colorAttr, zRigHandle.alphaAttr):
                    self.childChanged(self.kBoundingBoxChanged)
                    omr.MRenderer.setGeometryDrawDirty(self.thisMObject(), False)

                return super(zRigHandle, self).setDependentsDirty(plug, affectedPlugs)


        def isBounded(self):
                return True

        def boundingBox(self):
                transform = _getTransform(self.thisMObject())
            
                shapeIdx = om.MPlug(self.thisMObject(), zRigHandle.shapeAttr).asInt()
                shape = shapes[shapeIdx]['geometry']
                
                bounds = getShapeBounds(shape)
                bounds.transformUsing(transform)
                return bounds

def _hitTestShape(view, shape):
    # Hit test shape within view.
    for part in shape:
        view.beginSelect()

        data = part['data']
        itemType = part['type']
        if itemType == 'quad':
            itemType = omr.MGeometry.kTriangles
            tris = []
            for i in xrange(0, len(data), 4):
                tris.append(data[i+0])
                tris.append(data[i+1])
                tris.append(data[i+2])

                tris.append(data[i+2])
                tris.append(data[i+3])
                tris.append(data[i+0])
            data = tris

        glFT.glBegin(v1omr.MGL_TRIANGLES)
        for v in data:
            glFT.glVertex3f(v.x, v.y, v.z)
        glFT.glEnd()

        # Check the hit test.
        if view.endSelect() > 0:
            return True

    return False


class zRigHandleShapeUI(omui.MPxSurfaceShapeUI):
        def __init__(self):
                omui.MPxSurfaceShapeUI.__init__(self)

        @staticmethod
        def creator():
                return zRigHandleShapeUI()

        def select(self, selectInfo, selectionList, worldSpaceSelectPts):
            transform = _getTransform(self.surfaceShape().thisMObject())

            shapeIdx = om.MPlug(self.surfaceShape().thisMObject(), zRigHandle.shapeAttr).asInt()
            shape = _transformShape(shapes[shapeIdx]['geometry'], transform)

            # Hit test the selection against the shape.
            if not _hitTestShape(selectInfo.view(), shape):
                return False

            item = om.MSelectionList()
            item.add(selectInfo.selectPath())

            # Get the world space position of the node.  We'll set the position of the selection here,
            # so the camera focuses on it.
            mat = item.getDagPath(0).inclusiveMatrix()
            transformation = om.MTransformationMatrix(mat)
            pos = transformation.translation(om.MSpace.kWorld)

            priorityMask = om.MSelectionMask(om.MSelectionMask.kSelectJoints)
            selectInfo.addSelection(item, om.MPoint(pos), selectionList, worldSpaceSelectPts, priorityMask, False)

            return True


def isPathSelected(objPath):
        sel1 = om.MSelectionList()
        sel1.add(objPath)
        path = sel1.getDagPath(0)
        sel = om.MGlobal.getActiveSelectionList()
        if sel.hasItem(path):
            return True

        path.pop()
        if sel.hasItem(path):
            return True
        return False

class zRigHandleDrawOverride(omr.MPxDrawOverride):
	@staticmethod
	def creator(obj):
		return zRigHandleDrawOverride(obj)

	@staticmethod
	def draw(context, data):
		return

	def __init__(self, obj):
		omr.MPxDrawOverride.__init__(self, obj, zRigHandleDrawOverride.draw)

	def supportedDrawAPIs(self):
		return omr.MRenderer.kOpenGL | omr.MRenderer.kDirectX11 | omr.MRenderer.kOpenGLCoreProfile

	def isBounded(self, objPath, cameraPath):
		return True

	def boundingBox(self, objPath, cameraPath):
		shape = self.getShape(objPath, _getTransform(objPath.node()))
                return getShapeBounds(shape)

	def disableInternalBoundingBoxDraw(self):
		return True

	def prepareForDraw(self, objPath, cameraPath, frameContext, oldData):
		self.isSelected = isPathSelected(objPath)

                plug = om.MPlug(objPath.node(), zRigHandle.colorAttr)
                self.color = om.MColor(om.MFnNumericData(plug.asMObject()).getData())

                alpha = om.MPlug(objPath.node(), zRigHandle.alphaAttr).asFloat()
                self.color.a = alpha

                if self.isSelected:
                    self.borderColor = omr.MGeometryUtilities.wireframeColor(objPath)
                else:
                    self.borderColor = om.MColor(self.color)
                    self.borderColor.a = 1

                transform = _getTransform(objPath.node())
		self.shape = self.getShape(objPath, transform)

	def hasUIDrawables(self):
		return True

	def addUIDrawables(self, objPath, drawManager, frameContext, data):
                drawManager.beginDrawInXray()

		for item in self.shape:
                    drawManager.beginDrawable()
                    drawManager.setColor(self.color)

                    data = om.MPointArray()
                    for point in item['data']:
			data.append(point)
                    itemType = item['type']
                    if itemType == 'quad':
                        itemType = omr.MGeometry.kTriangles
                        tris = om.MPointArray()
                        for i in xrange(0, len(data), 4):
                            tris.append( data[i+0] )
                            tris.append( data[i+1] )
                            tris.append( data[i+2] )

                            tris.append( data[i+2] )
                            tris.append( data[i+3] )
                            tris.append( data[i+0] )
                        data = tris

                    drawManager.mesh(itemType, data)

                    drawManager.endDrawable()

                # XXX: This will overdraw overlapping lines, which will reduce antialiasing
                # quality.
                for item in self.shape:
                    drawManager.beginDrawable()
                    drawManager.setColor(self.borderColor)

                    data = om.MPointArray()

                    points = item['data']
                    if item['type'] == 'quad':
                        for i in xrange(0, len(points), 4):
                            data.append(points[i+0])
                            data.append(points[i+1])
                            data.append(points[i+1])
                            data.append(points[i+2])
                            data.append(points[i+2])
                            data.append(points[i+3])
                            data.append(points[i+3])
                            data.append(points[i+0])
                    else:
                        for idx in xrange(0, len(points), 3):
                            data.append(points[idx+0])
                            data.append(points[idx+1])

                            data.append(points[idx+1])
                            data.append(points[idx+2])

                            data.append(points[idx+2])
                            data.append(points[idx+0])

                    drawManager.mesh(omr.MUIDrawManager.kLines, data)
                    drawManager.endDrawable()

                drawManager.endDrawInXray()

	def getShape(self, objPath, transform):
            idx = self.getShapeIdx(objPath)
            return _transformShape(shapes[idx]['geometry'], transform)

	def getShapeIdx(self, objPath):
            return om.MPlug(objPath.node(), zRigHandle.shapeAttr).asInt()

def initializePlugin(obj):
        plugin = om.MFnPlugin(obj)
        plugin.registerShape('zRigHandle', zRigHandle.id, zRigHandle.creator, zRigHandle.initialize, zRigHandleShapeUI.creator, zRigHandle.drawDbClassification)
        omr.MDrawRegistry.registerDrawOverrideCreator(zRigHandle.drawDbClassification, zRigHandle.drawRegistrantId, zRigHandleDrawOverride.creator)

def uninitializePlugin(obj):
        plugin = om.MFnPlugin(obj)
        omr.MDrawRegistry.deregisterDrawOverrideCreator(zRigHandle.drawDbClassification, zRigHandle.drawRegistrantId)
        plugin.deregisterNode(zRigHandle.id)

