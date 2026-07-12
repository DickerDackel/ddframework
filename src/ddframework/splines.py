import pygame

from glm import lerp, normalize, vec2

# How the lerping in decasteljau works comes from the Freya Holmer talk about
# splines and is also visualized in the Wikipedia article about Bezier Curves:
#
#   https://www.youtube.com/watch?v=aVwxzDHniEw
#   https://www.youtube.com/watch?v=jvPPXbo87ds
#   https://en.wikipedia.org/wiki/B%C3%A9zier_curve#Constructing_B%C3%A9zier_curves
#
# The bernstein polynomials come from the wikipedia article:
#
#   https://en.wikipedia.org/wiki/Bernstein_polynomial#Bernstein_polynomials
#
# The Berstein variants are the polynomal solution of the lerped functions and
# result in the same curve


# Stolen from Lucysir/kadir014
def catmull_rom(t: float, p0: vec2, p1: vec2, p2: vec2, p3: vec2) -> vec2:
    t2 = t * t
    t3 = t2 * t

    x = 0.5 * ((2.0 * p1.x) +
              (-p0.x + p2.x) * t +
              (2.0 * p0.x - 5.0 * p1.x + 4.0 * p2.x - p3.x) * t2 +
              (-p0.x + 3.0 * p1.x - 3.0 * p2.x + p3.x) * t3)

    y = 0.5 * ((2 * p1.y) +
              (-p0.y + p2.y) * t +
              (2.0 * p0.y - 5.0 * p1.y + 4.0 * p2.y - p3.y) * t2 +
              (-p0.y + 3.0 * p1.y - 3.0 * p2.y + p3.y) * t3)

    return vec2(x, y)


def quadratic_bezier_decasteljau(t: float, p0: vec2, p1: vec2, p2: vec2, with_momentum: bool = False):
    """return the quadratic bezier in p0/p1/p2 at time t.

    :param t: The lerp time from 0-1
    :param p0: First control point of the spline
    :param p1: Second control point of the spline
    :param p2: Third control point of the spline
    :param with_momentum: If true, return a point, momentum tuple instead of just the point
    :return: Depending on with_momentum, the spline point, or a point, momentum tuple

    """

    v0 = vec2(p0)
    v1 = vec2(p1)
    v2 = vec2(p2)

    a = lerp(v0, v1, t)
    b = lerp(v1, v2, t)
    p = lerp(a, b, t)

    if with_momentum:
        return p, normalize(b - a)
    else:
        return p


def quadratic_bezier_bernstein(t, p0, p1, p2):
    """return the quad bezier in p0/p1/p2 at time t

        quadratic_bezier_bernstein(t, p0, p1, p2) -> vec2

    Arguments:

        t               Time within the spline 0.0 <= t <= 1
        p0, p1, p2      The spline's control points (vec2)
    """
    v0 = vec2(p0)
    v1 = vec2(p1)
    v2 = vec2(p2)

    # cache
    t2 = t * t

    # b0,2(x) = 1 - 2 x + 1x^2
    # b1,2(x) = 0 + 2x - 2x^2
    # b2,2(x) = 0 + 0x + 1x^2
    p = (  v0 * (1 - 2 * t + t2)
         + v1 * (2 * t - 2 * t2)
         + v2 * t2)

    return p


def cubic_bezier_decasteljau(t: float, p0: vec2, p1: vec2, p2: vec2, p3: vec2, with_momentum: bool = False):
    """return the quad bezier in p0/p1/p2/p3 at time t.

    :param t: The lerp time from 0-1
    :param p0: First control point of the spline
    :param p1: Second control point of the spline
    :param p2: Third control point of the spline
    :param p3: Fourth control point of the spline
    :param with_momentum: If true, return a point, momentum tuple instead of just the point
    :return: Depending on with_momentum, the spline point, or a point, momentum tuple

    """

    v0 = vec2(p0)
    v1 = vec2(p1)
    v2 = vec2(p2)
    v3 = vec2(p3)

    a = lerp(v0, v1, t)
    b = lerp(v1, v2, t)
    c = lerp(v2, v3, t)
    d = lerp(a, b, t)
    e = lerp(b, c, t)
    p = lerp(d, e, t)

    if with_momentum:
        return p, normalize(e - d)
    else:
        return p


def cubic_bezier_decasteljau_normal(t, p0, p1, p2, p3):
    # B'(t) = 3(1-t)² (P₁ - P₀) + 6t(1-t) (P₂ - P₁) + 3t² (P₃ - P₂)
    v0 = vec2(p0)
    v1 = vec2(p1)
    v2 = vec2(p2)
    v3 = vec2(p3)

    # cache
    t2 = t * t

    d10 = v1 - v0
    d21 = v2 - v1
    d32 = v3 - v2

    m = ((3 - 6 * t + 3 * t2) * d10
         + (6 * t - 6 * t2) * d21
         + 3 * t2 * d32)

    return m


def cubic_bezier_bernstein(t, p0, p1, p2, p3):
    """return the quad bezier in p0/p1/p2 at time t

        cubic_bezier(t, p0, p1, p2, p3) -> vec2

    Arguments:

        t               Time within the spline 0.0 <= t <= 1
        p0, p1, p2, p3  The spline's control points (vec2)
    """
    v0 = vec2(p0)
    v1 = vec2(p1)
    v2 = vec2(p2)
    v3 = vec2(p3)

    # cache
    t2 = t * t
    t3 = t2 * t

    # This is the function below broken up into parts:
    # bernstein coefficients:
    # b0 = 1 - 3 * t + 3 * t2 - t3
    # b1 = 3 * t - 6 * t2 + 3 * t3
    # b2 = 3 * t2 - 3 * t3
    # b3 = t3
    #
    # Apply coefficients to vectors
    # a = v0 * b0
    # b = v1 * b1
    # c = v2 * b2
    # d = v3 * b3
    #
    # sum everything up
    # p = a + b + c + d

    p = (  v0 * (1 - 3 * t + 3 * t2 - t3)
         + v1 * (3 * t - 6 * t2 + 3 * t3)
         + v2 * (3 * t2 - 3 * t3)
         + v3 * t3)

    return p


quadratic_bezier = quadratic_bezier_bernstein
cubic_bezier = cubic_bezier_bernstein

# For compatibility.  Renamed, since bspline != bezier curve
quadratic_bspline = quadratic_bezier
cubic_bspline = cubic_bezier
