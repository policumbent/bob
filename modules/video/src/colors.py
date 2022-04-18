class _Colors:
    @property
    def white(self):
        return (255,255,255)

    @property
    def black(self):
        return (0,0,0)

    @property
    def red(self):
        return (255,0,0)
    @property
    def green(self):
        return (0,255,0)
    
    @property
    def blue(self):
        return (0,0,255)

# exported contant for color
Colors = _Colors()