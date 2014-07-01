__author__ = 'croxis'
from direct.directnotify.DirectNotify import DirectNotify
from direct.showbase.DirectObject import DirectObject

log = DirectNotify().newCategory("SandBox")


class EntitySystem(DirectObject):
    def __init__(self, *types):
        self.entities = {}
        self.interested = set()
        self.enabled = True
        for t in types:
            if t:
                log.debug(str(self) + " interested in " + str(t))
                self.interested.add(t)
        self.accept("add_component", self.add_component)

    def add_component(self, entity, component):
        if component.__class__ in self.interested and entity not in self.entities:
            log.debug(str(self) + " recognizes component " + str(component) + " for entity " + str(entity.id))
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