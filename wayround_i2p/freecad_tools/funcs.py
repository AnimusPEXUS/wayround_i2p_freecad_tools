import FreeCAD
import FreeCADGui
import Part as FreeCADPart


def check_freecad(print_error=True):

    g = globals()

    if 'FreeCAD' not in g:
        return False

    fc = g['FreeCAD']
    fc_d = dir(fc)

    if '__name__' not in fc_d:
        return False

    if fc.__name__ != 'FreeCAD':
        return False

    return True


def get_points_list(obj):
    '''
    if obj type is list - it returned without changes.
    if obj type is Feature - obj.Shape.Vertexes is returned.
    None is returned in case of error
    '''

    obj_type = type(obj)

    if obj_type == list:
        return obj
    elif obj_type == FreeCADPart.Feature:
        return obj.Shape.Vertexes
    else:
        return None


def get_edges_list(obj):

    obj_type = type(obj)

    if obj_type == FreeCADPart.Feature:
        return obj.Shape.Edges

    return None


def get_face_list(obj):

    obj_type = type(obj)

    if obj_type.__name__ == 'Feature':
        return obj.Shape.Faces

    return None


def get_minmax_xyz(obj, what, where, ret_type='value'):
    '''
    You pass object and this function searches
    it's points for min or max X, Y or Z and returns
    exact value or list of vectors or vertexes.

    obj can be:
      *. a list of App.Vector
      *. a list of Part.Vertex
      *. a Part.Vertex

    throws exception in case of unrecovarable error.

    returns 
       if nothing found (obj has no points): 
       * None if 'value' requested for a result;
       * empty list, if 'vertex', 'vector' or 'same' is requested.
       else:
       * exect numeric value returned
       * list with all vertixes or vectors

    what: 'min' or 'max'
    where: 'x', 'y' or 'z'
    ret_type: one of 'value', 'vertex', 'vector', 'same'.
        if 'same' is requested, then if input object's points are vertexes - the vertex list is returned;
                               if input object's points are vectors - the vectors list is returned;
        if 'vertex' or 'vector', is requested, then points returned as is or copyed, converted and returned.
    '''

    ##### vvv parameters checking and points (vtxs) acquisition vvv #####

    # actual type of object which was passed
    type_obj = type(obj)

    # calculated type: FreeCADPart.Vertex or FreeCADApp.Vector
    #   - this is needed to check `where' parameter
    input_type = None

    # output type: 'value' or 'list' (this is for debugging)
    output_type = None

    # output point type: the type of point which has to be returned in list
    output_point_type = None

    # vvv calculate input_type

    if type_obj == FreeCADPart.Feature:
        input_type = FreeCADPart.Vertex

    elif type_obj == list:
        len_obj = len(obj)
        if len_obj == 0:
            return list()
            input_type = FreeCADPart.Vertex
        else:
            type_obj_0 = type(obj[0])
            if type_obj_0 in [FreeCADPart.Vertex, FreeCAD.Vector]:
                input_type = type_obj_0
            else:
                raise Exception("invalid 'obj[0]' type: {}".format(type_obj_0))

    else:
        raise Exception("invalid 'obj' type: {}".format(type_obj))

    # vvv validate `ret_type' and calculate output_type and output_point_type

    ret_type = ret_type.lower()

    if ret_type == 'value':
        output_type = 'value'

    elif ret_type == 'same':
        output_type = 'list'
        output_point_type = input_type

    elif ret_type == 'vertex':
        output_type = 'list'
        output_point_type = FreeCADPart.Vertex

    elif ret_type == 'vector':
        output_type = 'list'
        output_point_type = FreeCAD.Vector

    else:
        raise Exception("invalid `ret_type' value")

    # vvv verify 'what' param

    what = what.lower()

    if what not in ['min', 'max']:
        raise Exception("invalid 'what'")

    # vvv verify 'where' param

    if input_type == FreeCADPart.Vertex:
        where = where.upper()
        input_X_name = 'X'
        input_Y_name = 'Y'
        input_Z_name = 'Z'
        if where not in ['X', 'Y', 'Z']:
            raise Exception("invalid `where' value")

    elif input_type == FreeCAD.Vector:
        where = where.lower()
        input_X_name = 'x'
        input_Y_name = 'y'
        input_Z_name = 'z'
        if where not in ['x', 'y', 'z']:
            raise Exception("invalid `where' value")

    else:
        raise Exception("unexpected error")

    vtxs = get_points_list(obj)
    if vtxs is None:
        raise Exception("problem with supplied obj: can't get point list")

    for i in vtxs:
        if type(i) != input_type:
            raise Exception(
                "points inside of `obj' must all be of {} type".format(
                    input_type
                )
            )

    ##### ^^^ parameters checking and points (vtxs) acquisition ^^^ #####

    len_vtxs = len(vtxs)

    if len_vtxs == 0:
        if output_type == 'value':
            return None
        elif output_type == 'list':
            return list()
        else:
            raise Excpetion("unexpected execution")

    # vvv perform actual min/max filtering and find one point

    current = vtxs[0]
    current_to_check = getattr(current, where)

    for i in vtxs[1:]:

        next_to_check = getattr(i, where)

        if what == 'min':
            if next_to_check < current_to_check:
                current_to_check = next_to_check
                current = i
        else:
            if next_to_check > current_to_check:
                current_to_check = next_to_check
                current = i

    # here 'current' is our final point

    # vvv prepare and return result

    if output_type == 'value':
        return getattr(current, where)
    elif output_type == 'list':
        res = [current]
        # print("res 1: {}".format(res))
        # result should contain all duplicated points

        for i in vtxs:
            if (
                    getattr(current, input_X_name) == getattr(i, input_X_name)
                    and getattr(current, input_Y_name) == getattr(i, input_Y_name)
                and getattr(current, input_Z_name) == getattr(i, input_Z_name)
            ):
                res.append(i)
        # print("res 2: {}".format(res))
        for i in vtxs:
            if (getattr(current, where) == getattr(i, where)):
                res.append(i)

        # delete duplicated objects.
        # note: we intentionally don't delete points with same coordinates.
        #       only deduplicating objects
        res2 = res
        res = []
        for i in res2:
            if not i in res:
                res.append(i)

        res2 = res
        res = []
        for i in res2:
            type_i = type(i)
            if ret_type == 'vector':
                if type_i == FreeCADPart.Vertex:
                    t = vertex_to_vector(i)
                    if not t:
                        raise Exception(
                            "Couldn't convert {} ({}) to Vector".format(
                                i, type_i
                            )
                        )
                    res.append(t)
                elif type_i == FreeCAD.Vector:
                    res.append(i)
                else:
                    raise Exception("unexpected")
            elif ret_type == 'vertex':
                if type_i == FreeCADPart.Vertex:
                    res.append(i)
                elif type_i == FreeCAD.Vector:
                    t = vector_to_vertex(i)
                    if not t:
                        raise Exception(
                            "Couldn't convert {} ({}) to Vertex".format(
                                i,
                                type_i
                            )
                        )
                    res.append(t)
                else:
                    raise Exception("unexpected")
            else:
                raise Exception("unexpected")

        return res
    else:
        raise Exception("invalid value for `output_type'")

    raise Exception("unexpected")
    return None


def get_max_x(obj, ret_type='value'):
    return get_minmax_xyz(obj, 'max', 'X', ret_type)


def get_min_x(obj, ret_type='value'):
    return get_minmax_xyz(obj, 'min', 'X', ret_type)


def get_max_y(obj, ret_type='value'):
    return get_minmax_xyz(obj, 'max', 'Y', ret_type)


def get_min_y(obj, ret_type='value'):
    return get_minmax_xyz(obj, 'min', 'Y', ret_type)


def get_max_z(obj, ret_type='value'):
    return get_minmax_xyz(obj, 'max', 'Z', ret_type)


def get_min_z(obj, ret_type='value'):
    return get_minmax_xyz(obj, 'min', 'Z', ret_type)


def get_max_x_vect(obj):
    return get_max_x(obj, ret_type='vector')


def get_min_x_vect(obj):
    return get_min_x(obj, ret_type='vector')


def get_max_y_vect(obj):
    return get_max_y(obj, ret_type='vector')


def get_min_y_vect(obj):
    return get_min_y(obj, ret_type='vector')


def get_max_z_vect(obj):
    return get_max_z(obj, ret_type='vector')


def get_min_z_vect(obj):
    return get_min_z(obj, ret_type='vector')


def get_xxx_vect(obj, lst):

    for i in lst:
        if not i in [
            'min_x', 'min_y', 'min_z',
            'max_x', 'max_y', 'max_z'
        ]:
            raise Exception("invalid `lst' item")

    ret = get_points_list(obj)

    for i in lst:
        ret = eval('get_{}_vect(ret)'.format(i))

    return ret


def return_one_or_None(lst):
    if len(lst) != 1:
        return None
    else:
        return lst[0]


def make_box_from_vectors(doc, name, list1, list2):

    if (len(list1) != 4 or len(list2) != 4):
        return None, Exception("list1 and list2 must both have 4 vectors")

    for j in [list1, list2]:
        for i in j:
            if type(i) != FreeCAD.Vector:
                return None, Exception("list1 and list2 must each have 4 vectors")

    v1_1 = list1[0]
    v1_2 = list1[1]
    v1_3 = list1[2]
    v1_4 = list1[3]

    v2_1 = list2[0]
    v2_2 = list2[1]
    v2_3 = list2[2]
    v2_4 = list2[3]

    l1 = FreeCADPart.LineSegment(v1_1, v1_2)
    e1 = l1.toShape()
    l2 = FreeCADPart.LineSegment(v1_2, v1_3)
    e2 = l2.toShape()
    l3 = FreeCADPart.LineSegment(v1_3, v1_4)
    e3 = l3.toShape()
    l4 = FreeCADPart.LineSegment(v1_4, v1_1)
    e4 = l4.toShape()

    l5 = FreeCADPart.LineSegment(v2_1, v2_2)
    e5 = l5.toShape()
    l6 = FreeCADPart.LineSegment(v2_2, v2_3)
    e6 = l6.toShape()
    l7 = FreeCADPart.LineSegment(v2_3, v2_4)
    e7 = l7.toShape()
    l8 = FreeCADPart.LineSegment(v2_4, v2_1)
    e8 = l8.toShape()

    l9 = FreeCADPart.LineSegment(v1_1, v2_1)
    e9 = l9.toShape()
    l10 = FreeCADPart.LineSegment(v1_2, v2_2)
    e10 = l10.toShape()
    l11 = FreeCADPart.LineSegment(v1_3, v2_3)
    e11 = l11.toShape()
    l12 = FreeCADPart.LineSegment(v1_4, v2_4)
    e12 = l12.toShape()

    w1 = FreeCADPart.Wire([e1, e2, e3, e4])
    w2 = FreeCADPart.Wire([e5, e6, e7, e8])

    w3 = FreeCADPart.Wire([e9, e5, e10, e1])
    w4 = FreeCADPart.Wire([e10, e6, e11, e2])
    w5 = FreeCADPart.Wire([e11, e7, e12, e3])
    w6 = FreeCADPart.Wire([e12, e8, e9, e4])

    f1 = FreeCADPart.Face(w1)
    f2 = FreeCADPart.Face(w2)
    f3 = FreeCADPart.Face(w3)
    f4 = FreeCADPart.Face(w4)
    f5 = FreeCADPart.Face(w5)
    f6 = FreeCADPart.Face(w6)

    s = FreeCADPart.Shape(
        [
            f1, f2, f3, f4, f5, f6
        ]
    )

    ret = doc.addObject(
        "Part::Feature",
        name
    )

    ret.Shape = s

    return ret, None


def make_box_from_vector_and_direction(doc, name, v1, direction):
    '''
    v1, direction age both App.Vector

    via v1 you designate base vector of box
    via v2 you designate directions and sizes

    function automatically calculates other vectors and
    passes to make_box_from_vectors()
    '''

    for i in ['x', 'y', 'z']:
        if getattr(direction, i) == 0:
            return None, Exception("each of xyz of `direction' must be non-zero")

    v1_1 = copy_vector(v1)

    v1_2 = copy_vector(v1_1)
    v1_2.x += direction.x

    v1_3 = copy_vector(v1_1)
    v1_3.x += direction.x
    v1_3.y += direction.y

    v1_4 = copy_vector(v1_1)
    v1_4.y += direction.y

    # ---

    v2_1 = copy_vector(v1_1)
    v2_1.z += direction.z

    v2_2 = copy_vector(v1_2)
    v2_2.z += direction.z

    v2_3 = copy_vector(v1_3)
    v2_3.z += direction.z

    v2_4 = copy_vector(v1_4)
    v2_4.z += direction.z

    ret, err = make_box_from_vectors(
        doc,
        name,
        [v1_1, v1_2, v1_3, v1_4],
        [v2_1, v2_2, v2_3, v2_4]
    )
    return ret, None


def calc_vector_distance(v1, v2):
    x1 = v1.x
    x2 = v2.x
    y1 = v1.Y
    y2 = v2.y
    z1 = v1.z
    z2 = v2.z

    if x1 > x2:
        z = x1
        x1 = x2
        x2 = z

    if y1 > y2:
        z = y1
        y1 = y2
        y2 = z

    if z1 > z2:
        z = z1
        z1 = z2
        z2 = z

    x_diff = x2-x1
    y_diff = y2-y1
    z_diff = z2-z1

    diff = math.sqrt(
        math.pow(x_diff, 2) +
        math.pow(y_diff, 2) +
        math.pow(z_diff, 2)
    )

    return diff


def calc_edge_length(e):
    return calc_vector_distance(e.Vertexes[0], e.Vertexes[1])


def get_longest_edge(obj):
    '''
    this uses FreeCAD functionality, unlike calc_longest_edge()
    '''

    edges = get_edges_list(obj)

    len_edges = len(edges)

    if len_edges == 0:
        return None, Exception("no edges")

    ret = edges[0]

    for i in range(1, len_edges):
        e = edges[i]
        if e.Length > ret.Length:
            ret = e

    return ret, None


def calc_longest_edge(obj):
    '''
    this calculates longest edge manually, unlike get_longest_edge()
    '''

    edges = get_edges_list(obj)

    len_edges = len(edges)

    if len_edges == 0:
        return None, Exception("no edges")

    ret = edges[0]

    for i in range(1, len_edges):
        e = edges[i]
        if (calc_edge_length(e) > calc_edge_length(ret)):
            ret = e

    return ret, None


def get_obj_length(obj):
    e, err = get_longest_edge(obj)
    if err:
        return None, err
    return e.Length, None


def calc_obj_length(obj):
    e, err = calc_longest_edge(obj)
    if err:
        return None, err
    return e.Length, None


def copy_vector(obj):
    '''
    obj must be FreeCAD.Vector or Part.Vertex. - in both cases new Vector is returned.
    if error - None is returned
    '''
    type_obj = type(obj)
    if type_obj in [FreeCAD.Vector, FreeCADPart.Vertex]:
        return FreeCAD.Vector(obj)
    else:
        return None


def copy_vertex(obj):
    '''
    obj must be FreeCAD.Vector or Part.Vertex. - in both cases new Part.Vertex is returned.
    if error - None is returned
    '''
    type_obj = type(obj)
    if type_obj in [FreeCAD.Vector, FreeCADPart.Vertex]:
        return FreeCADPart.Vertex(obj)
    else:
        return None


def copy_point(obj):

    type_obj = type(obj)
    if not type_obj in [FreeCAD.Vector, FreeCADPart.Vertex]:
        return None

    if type_obj == FreeCAD.Vector:
        return copy_vector(obj)

    if type_obj == FreeCADPart.Vertex:
        return copy_vertex(obj)

    raise Exception("unexpected error")


def vertex_to_vector(vert):
    '''
     if error - None is returned
    '''
    if type(vert) != FreeCADPart.Vertex:
        return None
    return FreeCAD.Vector([vert.X, vert.Y, vert.Z])
