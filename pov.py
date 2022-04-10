def pov(c, w, ss):  # YX
    y = c[0]
    x = c[1]
    s = (ss - 1) // 2

    def pov_line(x, w):
        if x - s >= 0 and len(w) - 1 >= x + s:
            return w[x - s: x + s + 1]
        elif x - s < 0:
            return w[:ss]
        else:
            return w[-ss:]

    ww = pov_line(y, w)
    www = []
    for l in ww:
        www.append(pov_line(x, l))
    return www
