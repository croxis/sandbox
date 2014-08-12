"""SandBox engine! Much love to Maxis"""
# ## Python 3 look ahead imports ###
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from panda3d.core import loadPrcFileData

from direct.directnotify.DirectNotify import DirectNotify
from direct.showbase.ShowBase import ShowBase

from .networking import UDPNetworkSystem
from .systems import EntitySystem
from .errors import *
from .import appdirs

#from types import ClassType, TypeType

log = DirectNotify().newCategory("SandBox")
base = None

#TODO: Add locking mechanisms
#TODO: Add persistence mechanisms
#components = {} #{__Class__: []}
#entities = []
#components = [] #components[entityid]{componentType: component}
#removedAndAvailableEntities = []
entityCounter = 0
entities = {}
components = {}
systems = {}
counterReset = False
maxEntities = 65534


def init(log_level='info'):
    global base
    base = ShowBase()
    base.setSleep(0.001)
    if log_level == 'debug':
        log.setSeverity(2)
    if log_level == 'info':
        log.setSeverity(3)
    if log_level == 'warning':
        log.setSeverity(4)
    taskMgr.add(system_manager.update, "systemManager")


def getNextID():
    global entityCounter
    global counterReset
    entityCounter += 1
    if entityCounter > maxEntities:
        entityCounter = 0
        counterReset = True
    #if not counterReset:
    #print "Scanning for number", entityCounter, entities
    if entityCounter not in entities:
        return entityCounter
    else:
        for x in range(0, maxEntities):
            if x not in entities:
                entityCounter = x
                return x
                #return entityCounter
    '''else:
        print "Scanning for number", entityCounter, entities
        if entityCounter not in entities:
            return entityCounter
        else:
            for x in range(0, maxEntities):
                if x not in entities:
                    return x
            log.error("SandBox has reached the max number of entities. Increase entity limit.")'''


#def add_component(component):
#    if component.__class__ not in components.keys():
#        components[component.__class__] = []
#    components[component.__class__].append(component)


def add_component(entity, component):
    components[entity.id][component.__class__] = component
    log.debug("Added component: " + str(component) + " to " + str(entity.id))
    base.messenger.send("add_component", [entity, component])


def create_entity():
    """Returns next available entity"""
    entity = None
    """if removedAndAvailableEntities:
        log.debug("Entity Request: Using existing entity")
        entity = entities.pop()
    else:
        log.debug("Entity Request: Creating new entity")
        entity = Entity(len(entities))
        entities.append(entity)
        components.append({})
    log.debug("Number of entities: " + str(len(entities)))"""
    entity = Entity(getNextID())
    entities[entity.id] = entity
    components[entity.id] = {}
    log.debug("Entity Request: Creating new entity with id: " + str(entity.id))
    log.debug("Number of entities: " + str(len(entities)))
    return entity


def addEntity(entityId):
    """Manually adds an entity with a given id. Ideal for clients."""
    if entityId in entities:
        log.warning("Entity " + str(entityId) + " already exists!")
        log.warning("Entities: " + str(entities))
        return
    entity = Entity(entityId)
    entities[entity.id] = entity
    components[entity.id] = {}
    log.debug("Manually generated entity " + str(entityId))
    return entity


def removeEntity(entityId):
    #entities[entityId].reset()
    #components[entityId] = {}
    #removedAndAvailableEntities.append(entities[entityId])
    del entities[entityId]
    del components[entityId]


def get_entity(component):
    """
    Returns the entity of the component.

    :rtype : Entity
    :param component:
    """
    for entity_id in components:
        for component_class in components[entity_id]:
            if component is components[entity_id][component_class]:
                return entities[entity_id]
    raise NoEntity("No entity found for component: " + str(component))


def addSystem(system):
    add_system(system)


def add_system(system):
    system_manager.add_system(system)


def get_system(systemType):
    return system_manager.getSystem(systemType)


def getComponent(entity, componentType=None):
    if has_component(entity, componentType):
        return components[entity.id][componentType]
    else:
        raise NoComponent("No component type " + str(componentType)
                                 + " in entity " + str(entity.id))


def get_components(componentType):
    c = []
    for componentDict in components.values():
        if componentType in componentDict:
            c.append(componentDict[componentType])
    return c


def get_entities_by_component_type(component_type):
    """Returns a list of entities that have a component. This will be
    very expensive with large sets until the backend is moved to a
    real database.

    :rtype : list
    :param component_type: """
    entitiesList = []
    for entityID in components:
        if component_type in components[entityID]:
            entitiesList.append(entities[entityID])
    return entitiesList


def has_component(entity, component_type):
    return component_type in components[entity.id]


def send(message, params=[]):
    base.messenger.send(message, params)


class Entity(object):
    def __init__(self, uniqueId):
        self.id = uniqueId

    #    self.components = {}
    #def add_component(self,component):
    #    self.components[component.__class__] = component

    def removeComponent(self, componentClass):
        #del self.components[componentClass]
        pass

    def reset(self):
        #self.typeBits = self.systemBits = 0
        pass

    def add_component(self, component):
        #if not isinstance(component, Component): raise TypeError
        add_component(self, component)

    def get_component(self, component_type):
        return getComponent(self, component_type)

    def has_component(self, component_type):
        return has_component(self, component_type)


class Component(object):
    pass


class SystemManager(object):
    def __init__(self):
        pass
        #taskMgr.add(self.update, "systemManager")

    def add_system(self, system):
        if not isinstance(system, EntitySystem):
            raise TypeError
        log.debug("Adding system " + str(system))
        system.init()
        systems[system.__class__] = system

    def getSystem(self, systemType):
        #if not isinstance(systemType, EntitySystem):
        #    raise TypeError
        return systems[systemType]

    def update(self, task):
        #TODO: We may need to pass time delta values
        for system in systems.values():
            system.run()
        return task.cont


system_manager = SystemManager()


def run():
    log.info("Starting system")
    base.run()
