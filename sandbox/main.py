"""I think we are going to go python module here!"""

"""Key ideas:
Units contain their own simulation logic (see rules slides)
Units combine to get aggregate behavior"""

"""Resources
Units + Maps + Globals + Zones (rules in each one)
Paths + Agents"""

"""Objective: What You See Is What You Sim"""


"""Components"""




class Path(object):
    """Points connected by Segments make up Paths which make up PathSets
    full 3d spline"""

class Agent(object):
    """Has own resource bins, does not run rules
    Controlled by transport handlers, agents given to handler when agent emited from unit
    Handler resposible for delivering agent to destination unit"""
    """Created by unit rules, given destination.
    Can have Sinks which advertise the possible destinations.
    Creation rules can set simple destination instructions"""
    def __init__(self):
        self.bins = {}
    
class TransportHandler(object):
    """Path oriented be it people or resource"""
    """Path based routing: virtual distance field using D*-lite based and wavefront updates
    Calculate cost to nearest sink at vertices
    Steer to vertex with elast cost
    no per-agent routing info
    
    Distance modified by sink strength and modifiers such as congestion and speed limit"""
    pass
  

class Resource(object):
    """Basic currency of the game"""
    def __init__(self, name, icon):
        self.name = name
        self.icon = icon
        
class Bin(object):
    """Bins hold :class:`Resource`
    Args: 
        resource: :class:`Resource`
        capacity: numerical capacity"""
    def __init__(self, resource, capacity):
        self.resource = resource
        self.capacity = capacity
        self.amount = 0
        

class Unit(object):
    """A unit represents things. Contains a collection of bins. Should also be aware of spatial existance"""
    """Assume can be moved at will and controlled by a physics simulation"""
    def __init__(self):
        self.bins = {}
        self.spatialStuff = None
        self.rules = ""
    def addBin(self, binName, binType):
        self.bins[binName] = binType
    def getBin(self, binName):
        return self.bins[binName]

class Map(object):
    """Resource in the environment. Uniform grid, each cell a resource bin.
    Units interact with maps via footprint.
    Multiple maps can overlap (forrest map, water map, etc"""
    def __init__(self):
        self.rules = ""
    
class Globals(object):
    """A global set of resource bins such as player money"""
    def __init__(self):
        self.bins = {}
    def addBin(self, binName, binType):
        self.bins[binName] = binType
    def getBin(self, binName):
        return self.bins[binName]
        

class Box(object):
    """Play area and other properties, unit types, map types, global bins
    rule scripts
    
    bin and cell values
    unit locations"""
    def __init__(self):
        self.entities = {}
        self.systems = {}
        


    