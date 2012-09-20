import os
from PIL import Image

def compose_images(background, foreground):
    background.paste(foreground, None, foreground)
    return background

class Head():
    def __init__(self, head_type, color):
        self.head_type = head_type
        self.color = color

class Outfit():
    def __init__(self,outfit_type, torso_color, leg_color):
        self.outfit_type = outfit_type
        self.torso_color = torso_color
        self.leg_color = leg_color

class Character():

    all_actions = ['Walk']
    all_orientations = ['Back','Front','Left','Right']

    def __init__(self,race,gender,head,outfit):
        self.race = race
        self.gender = gender
        self.head = head
        self.outfit = outfit

    def subimage(self, action, orientation, part, frame):
        
        # check to make sure user is requesting a valid part
        assert action in self.all_actions
        assert orientation in self.all_orientations 
        if orientation in ['Back','Front']:
            orientation_dependent_parts = ['LArm','RArm']
        elif orientation in ['Left','Right']:
            orientation_dependent_parts = ['BArm','FArm']
        assert part in ['Head','Legs','Torso'] + orientation_dependent_parts

        # this can be expanded to include weapons, etc
        if part == 'Head':
            return Image.open(os.path.join('CharacterAssets', self.race, self.gender, "Heads",self.head.head_type, action, orientation, str(self.head.color) + '-' + str(frame) +'.png'))
        elif part == 'Legs':
            return Image.open(os.path.join('CharacterAssets', self.race, self.gender, "Outfits",self.outfit.outfit_type, action, orientation, 'Legs', str(self.outfit.leg_color) + '-' + str(frame) +'.png'))
        elif part == 'Torso':
            return Image.open(os.path.join('CharacterAssets', self.race, self.gender, "Outfits",self.outfit.outfit_type, action, orientation, 'Torso', str(self.outfit.torso_color) + '-' + str(frame) +'.png'))
        elif part in ['LArm','RArm', 'BArm','FArm']:
            return Image.open(os.path.join('CharacterAssets', self.race, self.gender, "Outfits",self.outfit.outfit_type, action, orientation, part, '1-' + str(frame) +'.png'))

    def composite_image(self, action, orientation, frame):
        construction_orders = {'Front': ['LArm', 'RArm', 'Torso', 'Legs', 'Head'],
            'Back': ['LArm','RArm', 'Torso', 'Legs', 'Head'],
            'Left': ['BArm','Torso','Legs','FArm','Head'],
            'Right': ['BArm','Torso','Legs','FArm','Head'],
        }

        images = [self.subimage(action, orientation, part, frame) for part in construction_orders[orientation]]
        return reduce(compose_images, images)

    def save_all_images(self):
        all_frames = {}
        
        for action in self.all_actions:
            for orientation in self.all_orientations:
                for frame in xrange(100):
                    try:
                        i = self.composite_image(action, orientation, frame + 1)
                        i.save('Character_%s_%s-%s.png' % (action, orientation, frame+1))
                    except IOError as e:
                        print e
                        break

if __name__ == '__main__':
    h = Head('Heads1',1)
    o = Outfit('Clothes1', 3, 4)
    ch = Character('Isanian','Female',h,o)
    ch.save_all_images()
