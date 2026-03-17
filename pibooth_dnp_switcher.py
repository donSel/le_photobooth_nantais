import pibooth
import pygame
from pibooth.utils import LOGGER
from pibooth.view.background import PrintBackground, Background
from pibooth.language import get_translated_text
from pibooth import fonts, pictures

ARROW_TOP = 'top'
ARROW_BOTTOM = 'bottom'
ARROW_HIDDEN = 'hidden'
ARROW_TOUCH = 'touchscreen'

MAX_PRINTS = 400

"""
To make this plugin work you should update the config file like this :
    [GENERAL]
    plugins = /home/pi/pibooth_dnp_switcher.py
Make also sure that you've previously created two printers in CPUS, one printing classic 6x4 (DNP_Standard), and the other one cut 6x2 strips (DNP_Strips).
"""

class QuotaReachedBackground(Background):

    def __init__(self, arrow_location=ARROW_BOTTOM, arrow_offset=0):
        Background.__init__(self, "print")
        self.arrow_location = arrow_location
        self.arrow_offset = arrow_offset
        self.right_arrow = None
        self.right_arrow_pos = None
        self.left_arrow = None
        self.left_arrow_pos = None

    def resize(self, screen):
        Background.resize(self, screen)
        if self._need_update and self.arrow_location != ARROW_HIDDEN:

            if self.arrow_location == ARROW_TOUCH:
                size = (self._rect.width // 4, self._rect.height // 4)
                # Right arrow
                self.right_arrow = pictures.get_pygame_image(
                    "printer_touch.png", size, hflip=False, vflip=False, color=self._text_color)
                x = int(self._rect.left + self._rect.width * 0.70
                        - self.right_arrow.get_rect().width // 2)
                y = int(self._rect.top + self._rect.height * 0.45)
            else:
                size = (self._rect.width * 0.3, self._rect.height * 0.3)

                vflip = True if self.arrow_location == ARROW_TOP else False

                # Right arrow
                self.right_arrow = pictures.get_pygame_image(
                    "arrow.png", size, hflip=True, vflip=vflip, color=self._text_color)

                x = int(self._rect.left + self._rect.width * 0.75
                        - self.right_arrow.get_rect().width // 2)
                if self.arrow_location == ARROW_TOP:
                    y = self._rect.top + 10
                else:
                    y = int(self._rect.top + 2 * self._rect.height // 3)

            self.right_arrow_pos = (x + self.arrow_offset, y)

            # Left arrow
            size = (self._rect.width * 0.1, self._rect.height * 0.1)

            if self.arrow_location == ARROW_TOUCH:
                self.left_arrow = pictures.get_pygame_image(
                    "hand.png", size, hflip=False, vflip=False, angle=70, color=self._text_color)
            else:
                vflip = True if self.arrow_location == ARROW_TOP else False
                angle = 70 if self.arrow_location == ARROW_TOP else -70
                self.left_arrow = pictures.get_pygame_image(
                    "arrow.png", size, hflip=False, vflip=vflip, angle=angle, color=self._text_color)

            x = int(self._rect.left + self._rect.width // 2
                    - self.left_arrow.get_rect().width // 2)

            if self.arrow_location == ARROW_TOP:
                y = self._rect.top + 10
            else:
                y = int(self._rect.bottom - self.left_arrow.get_rect().height * 1.1)

            self.left_arrow_pos = (x - self.arrow_offset, y)

    def resize_texts(self):
        """Update text surfaces.
        """
        if self.arrow_location == ARROW_HIDDEN:
            rect = pygame.Rect(self._rect.width / 2 + self._text_border, self._text_border,
                               self._rect.width / 2 - 2 * self._text_border,
                               self._rect.height - 2 * self._text_border)
            align = 'center'
        elif self.arrow_location == ARROW_BOTTOM:
            rect = pygame.Rect(self._rect.width / 2 + self._text_border, self._text_border,
                               self._rect.width / 2 - 2 * self._text_border,
                               self._rect.height * 0.6 - self._text_border)
            align = 'bottom-center'
        elif self.arrow_location == ARROW_TOUCH:
            rect = pygame.Rect(self._rect.width / 2 + self._text_border, self._text_border,
                               self._rect.width / 2 - 2 * self._text_border,
                               self._rect.height * 0.4 - self._text_border)
            align = 'bottom-center'
        else:
            rect = pygame.Rect(self._rect.width / 2 + self._text_border, self._rect.height * 0.4,
                               self._rect.width / 2 - 2 * self._text_border,
                               self._rect.height * 0.6 - self._text_border)
            align = 'top-center'
        Background.resize_texts(self, rect, align)

        text = 'Oh hell no'
        if text:
            rect = pygame.Rect(self._rect.width // 2, 0,
                               self._rect.width // 5 - 2 * self._text_border,
                               self._rect.height * 0.3 - 2 * self._text_border)
            if self.arrow_location == ARROW_TOP:
                rect.top = self._rect.height * 0.08
            else:
                rect.bottom = self._rect.height - self._rect.height * 0.08

            self._write_text(text, rect)

    def paint(self, screen):
        Background.paint(self, screen)
        if self.arrow_location != ARROW_HIDDEN:
            screen.blit(self.right_arrow, self.right_arrow_pos)
            screen.blit(self.left_arrow, self.left_arrow_pos)

            

@pibooth.hookimpl
def state_processing_enter(app):
    """
    This hook runs when the 'Processing' screen starts (after photos are taken).
    It checks how many photos were taken to choose the right DNP queue.
    """
    # Get the number of captures from the current session
    # num_photos = app.dirname  # In some versions, it's easier to check app.capture_nbr
    num_photos = app.capture_nbr
    # num_photos = len(app.captured_photos)
    
    if num_photos == 3:
        LOGGER.info("Format Bandelette détecté (3 captures) -> Utilisation de DNP_Strip")
        app.printer.name = "DNP_Strip"
        LOGGER.info(f"Impirmante {app.printer.name} sélectionnée")
    else:
        LOGGER.info("Format Classique détecté (1/2 captures) -> Utilisation de DNP_Standard")
        app.printer.name = "DNP_Standard"
        LOGGER.info(f"Impirmante {app.printer.name} sélectionnée")


@pibooth.hookimpl
def state_print_do(app):
    """
    If the MAX_PRINTS is reached, the impression is disabled
    """
    LOGGER.info(f"Nombre d'impressions {app.count.taken}")
    if app.count.taken >= MAX_PRINTS:
        LOGGER.warning(f"QUOTA ATTEINT ({MAX_PRINTS}). Désactivation de l'impression.")
        # We force Pibooth to think that printin is impossible
        # Or we can display an error message on the screen

        #app.printer.name = "PRINTER_DISABLED"
        win = app._window
        bg = win._current_background
        
        if bg:
            LOGGER.info("Afffichage du message de quota d'impression atteint")
            
            #bg_error = QuotaReachedBackground()
            #app._window._update_background(bg_error)
            
        #if app.previous_picture:
            #app._window._update_foreground(app.previous_picture, pos='left')
            

@pibooth.hookimpl
def state_wait_enter(app):
    """
    Executes when the choice menu is displayed.
    Reset to default when returning to the home screen
    """
    app.printer.name = "DNP_Standard"
    
