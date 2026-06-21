#!/usr/bin/python3

import sys

import FreeCAD
import FreeCADGui
import Part as FreeCADPart

np = '/home/animus/_local/p/wayround_i2p_freecad_tools/env'
while np in sys.path:
    sys.path.remove(np)
sys.path.insert(0, np)
del np

import wayround_i2p.freecad_tools.funcs as fc_funcs

parts_counters = {}


def part_format_name(name):
    global parts_counters

    if not name in parts_counters:
        parts_counters[name] = 1
    else:
        parts_counters[name] += 1

    return '{}_{:02d}'.format(name, parts_counters[name])


def _add_part_x(func_z, doc, reg, reg_key, name, *args, **kwargs):

    res, err = func_z(
        doc, name, *args, **kwargs
    )

    if err != None:
        return None, err

    edge_l, err = fc_funcs.get_obj_length(res)

    if err != None:
        return None, err

    reg[reg_key] = reg.get(reg_key, 0) + edge_l

    return res, None


def add_part(doc, reg, reg_key, name, rect1, rect2):
    return _add_part_x(
        fc_funcs.funcs.make_box_from_vectors,
        doc, reg, reg_key,
        name, rect1, rect2
    )


def add_part_vd(doc, reg, reg_key, name, v1, direction):
    '''
    by vector and direction
    '''
    return _add_part_x(
        fc_funcs.make_box_from_vector_and_direction,
        doc, reg, reg_key,
        name, v1, direction
    )


def draw_arc(
        doc, part_registry,
        position,
        add_top_bars, top_bars_length,
        add_double_central_vertical_bars,
        add_single_central_vertical_bars,
        std_sizes
):

    base_p1 = position.sub(
        FreeCAD.Vector(
            [
                0,
                std_sizes['profile_pipe1_size']/2,
                0
            ]
        )
    )

    base_p2 = base_p1.add(
        FreeCAD.Vector(
            [
                std_sizes['construction_width_wor'],
                0,
                0
            ]
        )
    )

    # bottom stripe

    p1 = fc_funcs.copy_point(base_p1)

    p2 = FreeCAD.Vector(
        [
            std_sizes['construction_width_wor'],
            std_sizes['stripe_width'],
            std_sizes['stripe_thickness']
        ]
    )

    p, err = add_part_vd(
        doc,
        part_registry,
        'stripe',
        part_format_name('stripe'),
        p1,
        p2
    )

    # vertical west

    p1 = base_p1.add(
        FreeCAD.Vector(
            [
                0,
                0,
                std_sizes['stripe_thickness']
            ]
        )
    )

    p2 = FreeCAD.Vector(
        [
            std_sizes['profile_pipe1_size'],
            std_sizes['profile_pipe1_size'],
            std_sizes['room_height']
        ]
    )

    p, err = add_part_vd(
        doc,
        part_registry,
        'profile_pipe_50x50',
        part_format_name('profile_pipe_50x50'),
        p1,
        p2
    )

    vertical_length_result = fc_funcs.get_obj_length(p)

    p3 = fc_funcs.return_one_or_None(
        fc_funcs.get_xxx_vect(
            p,
            ['max_z', 'min_y', 'min_x']
        )
    )

    # vertical east

    p1 = p1.add(
        FreeCAD.Vector(
            [
                std_sizes['construction_width_wor'],
                0,
                0
            ]
        )
    )

    p2 = fc_funcs.copy_point(p2)

    p2.x = -p2.x

    p, err = add_part_vd(
        doc,
        part_registry,
        'profile_pipe_50x50',
        part_format_name('profile_pipe_50x50'),
        p1,
        p2
    )

    p4 = fc_funcs.return_one_or_None(
        fc_funcs.get_xxx_vect(
            p,
            ['max_z', 'max_y', 'max_x']
        )
    )

    p4.z += std_sizes['profile_pipe1_size']

    p4 = p4.sub(p3)

    # top

    p, err = add_part_vd(
        doc,
        part_registry,
        'profile_pipe_50x50',
        part_format_name('profile_pipe_50x50'),
        p3,
        p4
    )

    top_pipe = p

    top_pipe_l, err = fc_funcs.get_obj_length(top_pipe)
    if err != None:
        raise Exception("error")

    top_pipe_l_middle = top_pipe_l / 2

    # top bars

    if add_top_bars == True:

        p5 = fc_funcs.return_one_or_None(
            fc_funcs.get_xxx_vect(
                top_pipe,
                ['max_z', 'max_y', 'min_x']
            )
        )

        top_pipe_l_div_3 = top_pipe_l / 3

        ep1 = p5.add(
            FreeCAD.Vector(
                [
                    top_pipe_l_div_3,
                    0,
                    0
                ]
            )
        )

        ep2 = ep1.add(
            FreeCAD.Vector(
                [
                    top_pipe_l_div_3,
                    0,
                    0
                ]
            )
        )

        ep1 = ep1.sub(
            FreeCAD.Vector(
                [
                    std_sizes['profile_pipe1_size']/2,
                    0,
                    0
                ]
            )
        )

        ep2 = ep2.sub(
            FreeCAD.Vector(
                [
                    std_sizes['profile_pipe1_size']/2,
                    0,
                    0
                ]
            )
        )

        ep1_1 = FreeCAD.Vector(
            [
                std_sizes['profile_pipe1_size'],
                top_bars_length,
                -std_sizes['profile_pipe1_size']
            ]
        )

        ep2_1 = fc_funcs.copy_point(ep1_1)

        p, err = add_part_vd(
            doc,
            part_registry,
            'profile_pipe_50x50',
            part_format_name('profile_pipe_50x50'),
            ep1,
            ep1_1
        )

        p, err = add_part_vd(
            doc,
            part_registry,
            'profile_pipe_50x50',
            part_format_name('profile_pipe_50x50'),
            ep2,
            ep2_1
        )

    if add_double_central_vertical_bars:
        door_half_length = std_sizes['door_size'] / 2

        p1 = fc_funcs.return_one_or_None(
            fc_funcs.get_xxx_vect(
                top_pipe,
                ['min_z', 'min_y', 'min_x']
            )
        )

        p2 = fc_funcs.copy_point(p1)
        p2.x = p2.x + top_pipe_l_middle - door_half_length

        p3 = fc_funcs.copy_point(p1)
        p3.x = p3.x + top_pipe_l_middle + door_half_length

        p2_1 = FreeCAD.Vector(
            [
                -std_sizes['profile_pipe1_size'],
                std_sizes['profile_pipe1_size'],
                -std_sizes['room_height']
            ]
        )

        p3_1 = FreeCAD.Vector(
            [
                std_sizes['profile_pipe1_size'],
                std_sizes['profile_pipe1_size'],
                -std_sizes['room_height']
            ]
        )

        p, err = add_part_vd(
            doc,
            part_registry,
            'profile_pipe_50x50',
            part_format_name('profile_pipe_50x50'),
            p2,
            p2_1
        )

        p, err = add_part_vd(
            doc,
            part_registry,
            'profile_pipe_50x50',
            part_format_name('profile_pipe_50x50'),
            p3,
            p3_1
        )

    if add_single_central_vertical_bars:

        p1 = fc_funcs.return_one_or_None(
            fc_funcs.get_xxx_vect(
                top_pipe,
                ['min_z', 'min_y', 'min_x']
            )
        )

        p2 = fc_funcs.copy_point(p1)
        p2.x = p2.x + top_pipe_l_middle

        p2_1 = FreeCAD.Vector(
            [
                -std_sizes['profile_pipe1_size'],
                std_sizes['profile_pipe1_size'],
                -std_sizes['room_height']
            ]
        )

        p, err = add_part_vd(
            doc,
            part_registry,
            'profile_pipe_50x50',
            part_format_name('profile_pipe_50x50'),
            p2,
            p2_1
        )


def calc_arc_points(std_sizes, middle_arcs_count):

    if not middle_arcs_count > 0:
        raise Exception("invalid `middle_arcs_count'. must be > 0")

    middle_arcs_count += 1

    ret = list()

    p1 = std_sizes['profile_pipe1_size']/2
    p2 = (std_sizes['construction_length'] -
          std_sizes['profile_pipe1_size']/2)

    ret.append(p1)
    ret.append(p2)

    p1_p2_diff = p2-p1

    if p1_p2_diff <= 0:
        raise Exception("invalid `construction_length' size")

    space_length = p1_p2_diff / middle_arcs_count

    for i in range(1, middle_arcs_count):
        ret.append(p1+(space_length*i))

    ret.sort()

    return ret, space_length


def main():

    doc = FreeCAD.newDocument('Small Shack Calculation')

    # std_sizes setup

    std_sizes = {
        'construction_length': 4000,
        'construction_width_max': 3000,
        'stripe_width': 50,
        'stripe_thickness': 5,
        'profile_pipe1_size': 50,
        'room_height': 2500,
        'still_rod_size': 10,
        'door_size': 800
    }

    # wor - without rods
    std_sizes['construction_width_wor'] = (
        std_sizes['construction_width_max']
        - (std_sizes['still_rod_size']*2)
    )

    # std_sizes setup end

    # bottom_west_stripe starting point
    start_point1 = FreeCAD.Vector([0, 0, 0])

    # bottom_east_stripe starting point
    start_point2 = start_point1.add(
        FreeCAD.Vector(
            [
                std_sizes['construction_width_wor'],
                0,
                0
            ]
        )
    )

    part_registry = dict()

    def add_part_vd_s(reg_key, name, v1, direction):
        return add_part_vd(
            doc,
            part_registry,
            reg_key,
            name,
            v1,
            direction
        )

    bottom_west_stripe, err = add_part_vd_s(
        'stripe',
        part_format_name('stripe'),
        start_point1,
        FreeCAD.Vector(
            [
                std_sizes['stripe_width'],
                std_sizes['construction_length'],
                std_sizes['stripe_thickness']
            ]
        )
    )

    if err:
        raise Exception(err)

    bottom_east_stripe, err = add_part_vd_s(
        'stripe',
        part_format_name('stripe'),
        start_point2,
        FreeCAD.Vector(
            [
                -std_sizes['stripe_width'],
                std_sizes['construction_length'],
                std_sizes['stripe_thickness']
            ]
        )
    )

    arc_points, space_length = calc_arc_points(std_sizes, 3)
    arc_points_len = len(arc_points)

    for i in range(arc_points_len):
        draw_arc(
            doc, part_registry,
            FreeCAD.Vector(
                [
                    0,
                    arc_points[i],
                    std_sizes['stripe_thickness']
                ]
            ),
            i < arc_points_len-1,
            space_length - std_sizes['profile_pipe1_size'],
            i == 0,
            i == arc_points_len-1,
            std_sizes
        )

    doc.recompute()
    view = Gui.ActiveDocument.ActiveView
    view.viewIsometric()
    view.fitAll()

    print("reg: {}".format(part_registry))


if __name__ == '__main__':
    main()

# import importlib
# import wayround_i2p.freecad_tools.funcs
# importlib.reload(wayround_i2p.freecad_tools.funcs)
