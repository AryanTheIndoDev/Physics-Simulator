import io
import pygame as pg

settings_svg = """<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="#C8C8C8" class="bi bi-wrench" viewBox="0 0 16 16" shape-rendering="crispEdges">
  <path d="M.102 2.223A3.004 3.004 0 0 0 3.78 5.897l6.341 6.252A3.003 3.003 0 0 0 13 16a3 3 0 1 0-.851-5.878L5.897 3.781A3.004 3.004 0 0 0 2.223.1l2.141 2.142L4 4l-1.757.364zm13.37 9.019.528.026.287.445.445.287.026.529L15 13l-.242.471-.026.529-.445.287-.287.445-.529.026L13 15l-.471-.242-.529-.026-.287-.445-.445-.287-.026-.529L11 13l.242-.471.026-.529.445-.287.287-.445.529-.026L13 11z"/>
</svg>"""

class Svgs:
    settings_encoded = io.BytesIO(settings_svg.encode("utf-8"))

    def load(self):
        self.settings_surf = pg.image.load_sized_svg(self.settings_encoded, (24, 24)).convert_alpha()


svgs = Svgs()

