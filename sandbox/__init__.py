"""SandBox engine! Much love to Maxis"""
from pandac.PandaModules import loadPrcFileData
loadPrcFileData("", "notify-level-SandBox debug")

from direct.directnotify.DirectNotify import DirectNotify
from direct.showbase.DirectObject import DirectObject
from direct.showbase.ShowBase import ShowBase

from main import *

#from types import ClassType, TypeType

log = DirectNotify().newCategory("SandBox")
base = ShowBase()

#TODO: Add locking mechanisms
#TODO: Add persistance mechanisms
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

def getNextID():
    global entityCounter
    entityCounter += 1
    if entityCounter > maxEntities:
        entityCounter = 0
        counterReset = True
    if not counterReset:
        return entityCounter
    else:
        if entityCounter not in entities.keys():
            return entityCounter
        else:
            for x in range(0, maxEntities):
                if x not in entities.keys():
                    return x
            log.error("SandBox has reached the max number of entities. Increase entity limit.")



#def addComponent(component):
#    if component.__class__ not in components.keys():
#        components[component.__class__] = []
#    components[component.__class__].append(component)


def addComponent(entity, component):
    components[entity.id][component.__class__] = component
    log.debug("Added component: " + str(component))
    messenger.send("addComponent", [entity, component])


def createEntity():
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
    log.debug("Entity Request: Creating new entity")
    entity = Entity(getNextID())
    entities[entity.id] = entity
    components[entity.id] = {}
    log.debug("Number of entities: " + str(len(entities)))
    return entity


def addEntity(entityId):
    """Manually adds an entity with a given id. Ideal for clients."""
    if entityId in entities.keys():
        log.warning("Entity " + str(entityId) + " already exists!")
        return
    entity = Entity(entityId)
    entities[entity.id] = entity
    components[entity.id] = {}
    return entity


def removeEntity(entityId):
    #entities[entityId].reset()
    #components[entityId] = {}
    #removedAndAvailableEntities.append(entities[entityId])
    del entities[entityId]
    del components[entityId]


def addSystem(system):
    systemManager.addSystem(system)


def getSystem(systemType):
    return systemManager.getSystem(systemType)


def getComponent(entity, componentType=None):
    if hasComponent(entity, componentType):
        return components[entity.id][componentType]


def getComponents(componentType):
    c = []
    for componentDict in components.values():
        if componentType in componentDict:
            c.append(componentDict[componentType])
    return c

def hasComponent(entity, componentType):
    return componentType in components[entity.id]


class Entity(object):
    def __init__(self, uniqueId):
        self.id = uniqueId
    #    self.components = {}
    #def addComponent(self,component):
    #    self.components[component.__class__] = component

    def removeComponent(self, componentClass):
        #del self.components[componentClass]
        pass

    def reset(self):
        #self.typeBits = self.systemBits = 0
        pass

    def addComponent(self, component):
        #if not isinstance(component, Component): raise TypeError
        addComponent(self, component)

    def getComponent(self, componentType):
        return getComponent(self, componentType)

    def hasComponent(self, componentType):
        return hasComponent(self, componentType)


class Component(object):
    pass


class EntitySystem(DirectObject):
    def __init__(self, *types):
        self.entities = {}
        self.interested = set()
        self.enabled = True
        for t in types:
            log.debug(str(self) + " interested in " + str(t))
            self.interested.add(t)
        self.accept("addComponent", self.addComponent)

    def addComponent(self, entity, component):
        if component.__class__ in self.interested and entity not in self.entities:
            log.debug("Adding component " + str(component) + " to entity " + str(entity))
            self.entities[entity.id] = entity

    def run(self):
        if self.enabled:
            self.begin()
            #self.processEntities(self.entities)
            for e in self.entities.values():
                self.process(e)
            self.end()

    def init(self):
        """This function is overridden for initialization instead of __init__."""

    def begin(self):
        pass

    def process(self, entity):
        """This is overridden"""
        log.error(str(self) + " has no process function.")
        raise NotImplementedError

    def end(self):
        pass


class SystemManager(object):
    def __init__(self):
        taskMgr.add(self.update, "systemManager")

    def addSystem(self, system):
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

systemManager = SystemManager()


def run():
    log.info("Starting server")
    base.run()
