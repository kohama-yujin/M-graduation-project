class TextureCount():
    def __init__(self):
        self.nTextures = 0

    def generateTextureID(self, ID):
        self.nTextures = self.nTextures + 1
        if ID < self.nTextures:
            return self.nTextures
        else:
            return ID
