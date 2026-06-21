#!/usr/bin/python3

import sys


import FreeCAD
import FreeCADGui
import Part as FreeCADPart


pipe_counter = 0
pipe_length_counter = 0

stripe_counter = 0
stripe_length_counter = 0


def add_stripe(doc, name, ):
    global stripe_counter
    if pnt is None:
        pnt = FreeCAD.Vector([0, 0, 0])
    width = 5
    height = 100
    box = FreeCADPart.makeBox(length, width, height, pnt)
    shape = box
    base = doc.addObject(
        "Part::Feature",
        "Stripe{:03d}".format(stripe_counter)
    )
    stripe_counter += 1
    base.Shape = shape
    return box


def add_square_pipe_big(doc, length, pnt=None, dir=None):
    global pipe_counter
    if pnt is None:
        pnt = FreeCAD.Vector([0, 0, 0])
    side_size = 50
    box = FreeCADPart.makeBox(length, side_size, side_size, pnt)
    shape = box
    base = doc.addObject(
        "Part::Feature",
        "Pipe{:03d}".format(pipe_counter)
    )
    pipe_counter += 1
    base.Shape = shape
    return box


def main():
    sys.path.insert(0, '/home/animus/_local/p/wayround_i2p_freecad_tools/env')

    import wayround_i2p.freecad_tools.funcs

    doc = FreeCAD.newDocument('Small Shack Calculation')

    stripe_width = 50

    '''
    res, err = wayround_i2p.freecad_tools.funcs.make_box_from_vectors(
        doc,
        "box0",
        [
            FreeCAD.Vector(50, 0, 0),
            FreeCAD.Vector(100, 0, 0),
            FreeCAD.Vector(100, 50, 0),
            FreeCAD.Vector(50, 50, 0)
        ],
        [
            FreeCAD.Vector(50, 0, 20),
            FreeCAD.Vector(100, 0, 20),
            FreeCAD.Vector(100, 50, 20),
            FreeCAD.Vector(50, 50, 20)
        ]
    )

    if err != None:
        print("error:", err)
        return
    '''

    v1 = FreeCAD.Vector([10, 0, 0])
    v2 = FreeCAD.Vector([10, 10, 10])

    res, err = wayround_i2p.freecad_tools.funcs.make_box_from_vector_and_direction(
        doc,
        'box1',
        v1,
        v2
    )

    if err != None:
        print("error:", err)
        return

    v1 = FreeCAD.Vector([-10, 0, 0])
    v2 = FreeCAD.Vector([-10, -10, -10])

    res, err = wayround_i2p.freecad_tools.funcs.make_box_from_vector_and_direction(
        doc,
        'box2',
        v1,
        v2
    )

    if err != None:
        print("error:", err)
        return

    doc.recompute()
    view = Gui.ActiveDocument.ActiveView
    view.viewIsometric()
    view.fitAll()

    print('lowest vertexes from {}'.format(res.Name))
    print(wayround_i2p.freecad_tools.funcs.get_min_z(res, 'vertex'))
    print('lowest vectors from {}'.format(res.Name))
    print(wayround_i2p.freecad_tools.funcs.get_min_z(res, 'vector'))
    print('lowest auto from {}'.format(res.Name))
    print(wayround_i2p.freecad_tools.funcs.get_min_z(res, 'same'))

    vector_test_list = [
        FreeCAD.Vector([1, 2, 3]),
        FreeCAD.Vector([4, 5, 6]),
        FreeCAD.Vector([7, 8, 9])
    ]
    vertex_test_list = wayround_i2p.freecad_tools.funcs.copy_vertexes(
        vector_test_list
    )


if __name__ == '__main__':
    main()

# import importlib
# import wayround_i2p.freecad_tools.funcs
# importlib.reload(wayround_i2p.freecad_tools.funcs)
