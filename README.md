Sandbox
=======

An entity component system for panda3d + additional bloat!

Sandbox tucks away some of the initial panda3d setup boiler code.

# Installation

Sandbox can be installed via pip:

```
pip2 install git+https://github.com/croxis/sandbox.git
```

# Quick Start

To begin using sandbox, import it and initialize with your desired log level.

```python
import sandbox

if __name__ == '__main__':
    # Configure any panda prc settings here
    sandbox.init(log_level='info')
    # Initiate sandbox and panda3d's game loop.
    sandbox.run()
```


# Use

sandbox.init() must be called before any entity, components, or systems can be added.

## Entity

Sandbox implements an entity-component-system similar to what is described on [t-machines](http://t-machine.org/index.php/2007/09/03/entity-systems-are-the-future-of-mmog-development-part-1/).

To create a new entity:
```python
import sandbox
sandbox.init()

entity = sandbox.create_entity()
```

## Component

Components are a specific aspect of an entity to define what it is. Generally components only contain variables and no functions themselves.


```python
import sandbox
from panda3d.core import NodePath

class PhysicsComponent:
    x = 0
    y = 0
    z = 0
    
class GraphicsComponent:
    node_path = None

if __name__ == '__main__':
    # Configure any panda prc settings here
    sandbox.init(log_level='info')
    
    entity = sandbox.create_entity()
    component = PhysicsComponent()
    entity.add_component(component)
    component = GraphicsComponent()
    component.node_path = NodePath()
    # Initiate sandbox and panda3d's game loop.
    sandbox.run()
```

## System

Systems manipulate components. Systems run in a panda3d task that operates every frame.
A system must inherit from sandbox.EntitySystem

Custom setup is done by overriding sandbox.EntitySystem.init(), NOT ```__init__```.

There are several functions that are called by sandbox on an EntitySystem.

EntitySystem.init(): called when the system is added to the system manager
EntitySystem.begin(): called once each frame before any entities are processed
EntitySystem.process(entity): called for each entity being processed. If not overridden an error is thrown.
EntitySystem.end(): called once each frame after all entities have been processed

An entity is passed to the process function, not the component. This allows a system to watch for multiple component, but requires for the component(s) to be manually obtained.

The component classes the system is interested in listening for are passed in the constructor.

```python
import sandbox
from panda3d.core import NodePath

class PhysicsComponent:
    x = 0
    y = 0
    z = 0
    
class GraphicsComponent:
    node_path = None

class PhysicsSystem(sandbox.EntitySystem):
    def init(self):
        # Set up bullet world or other physics systems here
        pass
    
    def process(self, entity):
        physics_component = entity.get_component(PhysicsComponent)
        physics_component.x += 1

class GraphicsSystem(sandbox.EntitySystem):
    def process(self, entity):
        graphics_component = entity.get_component(GraphicsComponent)
        physics_component = entity.get_component(PhysicsComponent)
        graphics_component.node_path.set_pos(physics_component.x, physics_component.y, physics_component.z)


if __name__ == '__main__':
    # Configure any panda prc settings here
    sandbox.init(log_level='info')
    
    entity = sandbox.create_entity()
    component = PhysicsComponent()
    entity.add_component(component)
    component = GraphicsComponent()
    component.node_path = NodePath()
    
    # Set up systems and register them with the system manager
    physics_system = PhysicsSystem(PhysicsComponent)
    sandbox.add_system(physics_system)
    
    graphics_system = GraphicsSystem(graphicsComponent)
    sandbox.add_system(graphics_component)
    
    # Initiate sandbox and panda3d's game loop.
    sandbox.run()
```



