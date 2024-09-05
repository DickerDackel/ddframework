import sampleapp.globals as G

from sampleapp.states.bannerstate import BannerState


class Pause(BannerState):
    def __init__(self, app):
        styles = (G.BANNER_STYLE.copy(border=10, bgcolor='black', margin=1,
                                      padding=(16, 32), border_color=G.COLOR.default,
                                      border_radius=16),
                  G.BANNER_STYLE.copy(color='black', border=1,
                                      bgcolor='black', margin=16, padding=(16, 32),
                                      border_color=G.COLOR.default, border_radius=10))

        super().__init__(app, 'Pause', styles=styles, pos=G.BANNER_POS)
