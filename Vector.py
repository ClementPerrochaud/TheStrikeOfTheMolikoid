# Vector 2.3
# !! NO TYPE CHECK will be implemented to avoid useless calculations ( vector.__class__.__name__ == 'Vector' )
from math import acos, cos, sin

class Vector:

    # init
    def __init__(self, *coo):
        self.coo = list(coo)

    # attributs
    def __getattr__(self, name): # avoid useless calculations
        if name == 'dim':
            self.dim = len(self.coo)
            return self.dim
        if name == 'magnitude':
            self.magnitude = (self*self)**(1/2)
            return self.magnitude
        if name == 'length': # alias
            self.length = self.magnitude
            return self.length

    # string representation
    def __str__(self):
        return '[' + ", ".join([str(x) for x in self]) + ']'
    def __repr__(self): return str(self)
    
    # composants
    def __getitem__(self, i):    return self.coo[i]
    def __setitem__(self, i, x): self[i] = x
    def __contains__(self, x):   return x in self.coo
    def __iter__(self): # for ... in
        for x in self.coo:
            yield x

    # logic
    def __eq__(self, vect):
        return all([ x!=y for x, y in zip(self, vect) ])
    def __ne__(self,v):
        return not self == v
    
    # convert (return another vector !)
    def float(self):   return Vector( *(float(x.real) if type(x)==complex else float(x) for x in self) )
    def int(self):     return Vector( *(int(x.real)   if type(x)==complex else int(x)   for x in self) )
    def complex(self): return Vector( *(complex(x) for x in self) )
    def __abs__(self):      return Vector( *(abs(x)     for x in self) )
    def __neg__(self):      return Vector( *(-x         for x in self) )
    def __round__(self, n): return Vector( *(round(x,n) for x in self) )

    # additions
    def __add__(self, vect):  return Vector( *(x+y for x, y in zip(self, vect)) )
    def __radd__(self, vect): return self + vect
    def __iadd__(self, vect): return self + vect
    def __sub__(self, vect):  return Vector( *(x-y for x, y in zip(self, vect)) )
    def __rsub__(self, vect): return self - vect
    def __isub__(self, vect): return self - vect

    # dot product, scalar multiplication & division
    def __mul__(self, V): # V is either a scalar or a vector
        if type(V) in (int, float, complex):
            return Vector( *(x*V for x in self) )
        return sum(( x*y for x, y in zip(self, V) ))
    def __rmul__(self, V): return self * V
    def __imul__(self, V): return self * V
    def __truediv__(self, D):  return self * (1/D) 
    def __idiv__(self, D): return self/D
    def __power__(self, n): # for self**2 only
        if n == 2: return self * self

    # cross product
    def __xor__(self, vect):
        if   self.dim == vect.dim == 2: # fake cross product -> scalar
            return self[0]*vect[1] - self[1]*vect[0]
        elif self.dim == vect.dim == 3: # real cross product -> vector
            return Vector(
                self[1]*vect[2] - self[2]*vect[1],
                self[2]*vect[0] - self[0]*vect[2],
                self[0]*vect[1] - self[1]*vect[0]
                )

    # angle
    @classmethod
    def angle(self, vect1, vect2): # -> angle between the two vectors
        try:
            v = vect1^vect2
            if v == 0: v = 1
            return acos( vect1*vect2/(vect1.magnitude*vect2.magnitude) ) * abs(v)/v
        except:
            return 0
    
    def rotate(self, angle): # Vector2 -> Vector2
        return Vector(self.coo[0]*cos(angle) - self.coo[1]*sin(angle),
                      self.coo[0]*sin(angle) + self.coo[1]*cos(angle))
    
    # sum 
    @classmethod
    def sum(self, vectors):
        if len(vectors) > 1:
            return vectors[-1] + Vector.sum(vectors[:-1])
        return vectors[0]