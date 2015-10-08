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
and select.
- Like HumanIK viewport handles, a solid object is displayed and selectable, so
you don't have to click on an awkward thin wireframe like with joint controls.
- The color and opacity of the control in the viewport can be set.  These can be
keyed, for example to brighten a control as it gets further away from its bind
position.
- A separate transform attribute is provided.  This can be used to control the
orientation of the control independently from its transform, which is useful for
some kinds of rig controls.
- A size attribute is provided, so the size of the control can be adjusted quickly
without affecting the size of objects constrained to it.

