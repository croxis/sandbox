'''Extra helpful math functions'''


'''Returns value unless it exceeds min or max, then returns min or max'''
def clamp(value, min_value, max_value):
    return max(min(value, max_value), min_value)


'''Returns the signed angular distance between two angles of a circle'''
def signedAngularDistance(target, origin):
    return ((target - origin) + 180) % 360 - 180
