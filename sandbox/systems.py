# ## Python 3 look ahead imports ###
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from direct.directnotify.DirectNotify import DirectNotify
from direct.showbase.DirectObject import DirectObject

__author__ = 'croxis'
log = DirectNotify().newCategory("SandBox-Systems")


class EntitySystem(object, DirectObject):
    def __init__(self, *types):
        super(EntitySystem, self).__init__()
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
        """Called once each frame before any components are manipulated."""
        pass

    def process(self, entity):
        """This is overridden."""
        log.error(str(self) + " has no process function.")
        raise NotImplementedError

    def end(self):
        """Called ocne each frame after all entities have been processed."""
        pass