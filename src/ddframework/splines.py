import pygame

from pygame.math import Vector2

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


def quadratic_bezier_decasteljau(t, p0, p1, p2):
    """return the quad bezier in p0/p1/p2 at time t

        quadratic_bezier_decasteljau(t, p0, p1, p2) -> Vector2

    Arguments:

        t               Time within the spline 0.0 <= t <= 1
        p0, p1, p2      The spline's control points (Vector2)
    """

    v0 = Vector2(p0)
    v1 = Vector2(p1)
    v2 = Vector2(p2)

    a = v0.lerp(v1, t)
    b = v1.lerp(v2, t)
    p = a.lerp(b, t)

    return p


def quadratic_bezier_bernstein(t, p0, p1, p2):
    """return the quad bezier in p0/p1/p2 at time t

        quadratic_bezier_bernstein(t, p0, p1, p2) -> Vector2

    Arguments:

        t               Time within the spline 0.0 <= t <= 1
        p0, p1, p2      The spline's control points (Vector2)
    """
    v0 = Vector2(p0)
    v1 = Vector2(p1)
    v2 = Vector2(p2)

    # cache
    t2 = t * t

    # b0,2(x) = 1 - 2 x + 1x^2
    # b1,2(x) = 0 + 2x - 2x^2
    # b2,2(x) = 0 + 0x + 1x^2
    p = (  v0 * (1 - 2 * t + t2)
         + v1 * (2 * t - 2 * t2)
         + v2 * t2)

    return p


def cubic_bezier_decasteljau(t, p0, p1, p2, p3):
    """return the quad bezier in p0/p1/p2 at time t

        cubic_bezier(t, p0, p1, p2, p3) -> Vector2

    Arguments:

        t               Time within the spline 0.0 <= t <= 1
        p0, p1, p2, p3  The spline's control points (Vector2)
    """
    v0 = Vector2(p0)
    v1 = Vector2(p1)
    v2 = Vector2(p2)
    v3 = Vector2(p3)

    a = v0.lerp(v1, t)
    b = v1.lerp(v2, t)
    c = v2.lerp(v3, t)
    d = a.lerp(b, t)
    e = b.lerp(c, t)
    p = d.lerp(e, t)

    return p


def cubic_bezier_bernstein(t, p0, p1, p2, p3):
    """return the quad bezier in p0/p1/p2 at time t

        cubic_bezier(t, p0, p1, p2, p3) -> Vector2

    Arguments:

        t               Time within the spline 0.0 <= t <= 1
        p0, p1, p2, p3  The spline's control points (Vector2)
    """
    v0 = Vector2(p0)
    v1 = Vector2(p1)
    v2 = Vector2(p2)
    v3 = Vector2(p3)

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
