# For debugging
################

def qtransform_to_string(trans):
    """
    print out matrix
    """
    row1 = f"|{trans.m11():+.2f} {trans.m12():+.2f} {trans.m13():+.2f}|\n"
    row2 = f"|{trans.m21():+.2f} {trans.m22():+.2f} {trans.m23():+.2f}|\n"
    row3 = f"|{trans.m31():+.2f} {trans.m32():+.2f} {trans.m33():+.2f}|"
    return row1 + row2 + row3

def rectangle_to_string(rect):
    """
    print out rect
    """
    top_left = rect.topLeft()
    size = rect.size()
    return f"QRect({top_left.x()}, {top_left.y()}) ({size.width()}, {size.height()})"
