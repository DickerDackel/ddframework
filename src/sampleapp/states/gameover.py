import sampleapp.globals as G

from sampleapp.states.bannerstate import BannerState


class Gameover(BannerState):
    def __init__(self, app):
        styles = (G.BANNER_STYLE.copy(color=G.COLOR.secondary,
                                      font=G.FONT.huge,
                                      border_color=G.COLOR.default, border=10,
                                      margin=16, padding=(16, 32),
                                      bgcolor='black', border_radius=20), )
        super().__init__(app, 'Gameover', styles=styles, pos=G.SCREEN.center,
                         followup=None, lifetime=3)

    # Needed because Bannerstate fills black
    def draw(self):
        self.groups.text.draw()
