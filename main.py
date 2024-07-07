from direct.showbase.ShowBase import ShowBase
from panda3d.core import LPoint3, CollisionNode, CollisionSphere, CollisionBox, CollisionTraverser, CollisionHandlerQueue, BitMask32, CardMaker
from panda3d.core import ClockObject
import random

class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        
        self.player = self.loader.loadModel("models/panda-model")
        self.player.reparentTo(self.render)
        self.player.setScale(0.005, 0.005, 0.005)
        self.player.setPos(LPoint3(0, 0, 0))

        
        cm = CardMaker('floor')
        cm.setFrame(-10, 10, -10, 10)  
        self.floor = self.render.attachNewNode(cm.generate())
        self.floor.setPos(0, 10, -0.5)  
        self.floor.setHpr(0, -90, 0)  

        
        self.camera_limits = {
            "left": -15,
            "right": 15,
            "top": 15,
            "bottom": -15,
            "near": -5,
            "far": 25
        }

        
        self.camera_angles = {"h": 0, "p": 0, "r": 0}

        
        self.accept("arrow_up", self.set_key, ["up", True])
        self.accept("arrow_up-up", self.set_key, ["up", False])
        self.accept("arrow_down", self.set_key, ["down", True])
        self.accept("arrow_down-up", self.set_key, ["down", False])
        self.accept("arrow_left", self.set_key, ["left", True])
        self.accept("arrow_left-up", self.set_key, ["left", False])
        self.accept("arrow_right", self.set_key, ["right", True])
        self.accept("arrow_right-up", self.set_key, ["right", False])
        self.accept("space", self.shoot)

        self.accept("a", self.set_key, ["rotate_left", True])
        self.accept("a-up", self.set_key, ["rotate_left", False])
        self.accept("d", self.set_key, ["rotate_right", True])
        self.accept("d-up", self.set_key, ["rotate_right", False])
        self.accept("w", self.set_key, ["rotate_up", True])
        self.accept("w-up", self.set_key, ["rotate_up", False])
        self.accept("s", self.set_key, ["rotate_down", True])
        self.accept("s-up", self.set_key, ["rotate_down", False])

        self.keys = {
            "up": False, "down": False, "left": False, "right": False,
            "rotate_left": False, "rotate_right": False, "rotate_up": False, "rotate_down": False
        }

        self.bullets = []
        self.enemies = []

        
        self.cTrav = CollisionTraverser()
        self.cHandler = CollisionHandlerQueue()

        
        self.player_coll_sphere = CollisionSphere(0, 0, 0, 1)
        self.player_coll_node = CollisionNode('player')
        self.player_coll_node.addSolid(self.player_coll_sphere)
        self.player_coll_node.setFromCollideMask(BitMask32.bit(0))
        self.player_coll_node.setIntoCollideMask(BitMask32.allOff())
        self.player_coll_np = self.player.attachNewNode(self.player_coll_node)
        self.cTrav.addCollider(self.player_coll_np, self.cHandler)

        
        self.create_enemies()

        
        self.taskMgr.add(self.update, "update")

    def set_key(self, key, value):
        self.keys[key] = value

    def move_player(self, dt):
        speed = 25 * dt
        if self.keys["up"]:
            self.player.setY(self.player, speed)
        if self.keys["down"] and self.player.getY() > 0:
            self.player.setY(self.player, -speed)
        if self.keys["left"]:
            self.player.setX(self.player, -speed)
        if self.keys["right"]:
            self.player.setX(self.player, speed)

    def rotate_camera(self, dt):
        rotate_speed = 50 * dt
        if self.keys["rotate_left"]:
            self.camera_angles["h"] += rotate_speed
        if self.keys["rotate_right"]:
            self.camera_angles["h"] -= rotate_speed
        if self.keys["rotate_up"]:
            self.camera_angles["p"] += rotate_speed
        if self.keys["rotate_down"]:
            self.camera_angles["p"] -= rotate_speed

        self.camera.setHpr(self.camera_angles["h"], self.camera_angles["p"], self.camera_angles["r"])

    def shoot(self):
        bullet = self.loader.loadModel("models/smiley")
        bullet.reparentTo(self.render)
        bullet.setScale(0.1, 0.1, 0.1)
        bullet.setPos(self.camera.getPos(self.render))
        bullet.setHpr(self.camera.getHpr(self.render))
        self.bullets.append(bullet)
        print(f"Bullet created at {bullet.getPos()}")

        
        bullet_coll_sphere = CollisionSphere(0, 0, 0, 0.1)
        bullet_coll_node = CollisionNode('bullet')
        bullet_coll_node.addSolid(bullet_coll_sphere)
        bullet_coll_node.setFromCollideMask(BitMask32.bit(1))
        bullet_coll_node.setIntoCollideMask(BitMask32.allOff())
        bullet_coll_np = bullet.attachNewNode(bullet_coll_node)
        self.cTrav.addCollider(bullet_coll_np, self.cHandler)

    def create_enemies(self):
        for i in range(5):
            enemy = self.loader.loadModel("models/panda-model")
            enemy.reparentTo(self.render)
            enemy.setScale(0.005, 0.005, 0.005)
            enemy.setPos(LPoint3(random.uniform(-5, 5), random.uniform(10, 20), 0))
            self.enemies.append(enemy)
            print(f"Enemy {i} created at {enemy.getPos()}")

            
            hitbox = CollisionBox(LPoint3(0, 0, 0), 1, 1, 1)
            hitbox_node = CollisionNode(f'hitbox-{i}')
            hitbox_node.addSolid(hitbox)
            hitbox_node.setFromCollideMask(BitMask32.allOff())
            hitbox_node.setIntoCollideMask(BitMask32.bit(1))
            hitbox_np = enemy.attachNewNode(hitbox_node)
            self.cTrav.addCollider(hitbox_np, self.cHandler)

    def update(self, task):
        dt = ClockObject.getGlobalClock().getDt()

        self.move_player(dt)
        self.rotate_camera(dt)
        self.limit_camera_position()

        
        for bullet in self.bullets:
            bullet.setY(bullet, 0.5)
            if bullet.getY() > 50:
                print("Bullet out of bounds, removing.")
                bullet.removeNode()
                self.bullets.remove(bullet)

        
        for enemy in self.enemies:
            enemy.setY(enemy, -0.05)
            if enemy.getY() < -10:
                enemy.setPos(LPoint3(random.uniform(-5, 5), random.uniform(10, 20), 0))

        self.cTrav.traverse(self.render)

        
        to_remove_bullets = []
        to_remove_enemies = []

        for entry in self.cHandler.entries:
            from_node = entry.getFromNode()
            into_node = entry.getIntoNode()
            from_obj = entry.getFromNodePath().getParent()
            into_obj = entry.getIntoNodePath().getParent()
            print(f"Collision detected: {from_node.getName()} hit {into_node.getName()}")
            if 'bullet' in from_node.getName() and 'hitbox' in into_node.getName():
                print("Bullet hit enemy hitbox, marking both for removal.")
                to_remove_bullets.append(from_obj)
                to_remove_enemies.append(into_obj.getParent())

       
        for bullet in to_remove_bullets:
            if bullet in self.bullets:
                print(f"Removing bullet at {bullet.getPos()}")
                bullet.removeNode()
                self.bullets.remove(bullet)

        for enemy in to_remove_enemies:
            if enemy in self.enemies:
                print(f"Removing enemy at {enemy.getPos()}")
                enemy.removeNode()
                self.enemies.remove(enemy)

        return task.cont

    def limit_camera_position(self):
        pos = self.camera.getPos()
        x = max(self.camera_limits["left"], min(self.camera_limits["right"], pos.getX()))
        y = max(self.camera_limits["near"], min(self.camera_limits["far"], pos.getY()))
        z = max(self.camera_limits["bottom"], min(self.camera_limits["top"], pos.getZ()))
        self.camera.setPos(x, y, z)

app = MyApp()
app.run()
