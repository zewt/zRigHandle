A shape node for visible, easily selected rig controls.

Installation
------------

Install by copying zRigHandle.mod into Maya's modules
directory and setting the correct path, and adding this to your userSetup.mel:

```
source "zRigHandle.mel";
```

A "Rig Handle" menu item will be added to the Create menu.

Note that this node is only tested in Viewport 2.0, and isn't expected to work
in obsolete viewports.

Usage
-----

This node can be used in place of shape nodes and nurbs curves for rig controls.

- This control is drawn in X-ray, like HumanIK controls, to make it easy to see
and select.  This can be turned off in the attribute editor.
- Like HumanIK viewport handles, a solid object is displayed and selectable, so
you don't have to click on an awkward thin wireframe like with joint controls.
- The color and opacity of the control in the viewport can be set.  These can be
keyed, for example to brighten a control as it gets further away from its bind
position.
- A separate local transform attribute is provided.  This controls the orientation
of the control independently from its transform.  For example, you can put an aim
constraint on a helper node underneath the rig control and connect its local matrix
to .translate, which will make the displayed control follow the aim constraint without
affecting its transform.
- Local transform, rotate and scale attributes allow adjusting the displayed
control, without affecting objects constrained to it.
- A custom mesh can be used.  Connect its outMesh to .inCustomMesh, and set the
shape to "Custom" in the AE.  Only the faces of the mesh will be used, not its
material, and only tris and quads are supported.

