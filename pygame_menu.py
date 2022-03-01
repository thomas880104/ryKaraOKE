import pygame as pg
import pyperclip
from mytubespleeter import Downloading_music,myspleeterrun
from ryKaraOkeInPygame import *
from ryMic      import *
from ryPitch__  import *

def song_start():
    pg.quit()
    mic= RyMic(musicfile = r'output/tmp/KaraOKE.wav')
    mic.start()
            
    Spectrogram= RySpectrogram(mic)
    Spectrogram.start()


def main():
    black = (0,0,0)
    white = (255,255,255)
    pg.display.set_caption('test pygame screen')
    screen = pg.display.set_mode((800,800))
    font = pg.font.Font(None, 32)
    clock = pg.time.Clock()
    input_box = pg.Rect(100, 100, 140, 32)
    color_inactive = pg.Color(0,255,0)
    color_active = pg.Color(255, 0, 0)
    color = color_inactive
    active = False
    text = ''
    done = False
    t = font.render('Please paste the youtube url', True, black)
    text_rect = t.get_rect(x = 100, y = 80)
    button_clicked = False

    button = font.render('download', True, white ,black)
    button_rect = button.get_rect(x = 120, y = 200)

    finish_text = font.render('done', True, black)
    finish_text_rect = finish_text.get_rect(x = 120,y = 240)
    finish = False

    while not done:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                done = True
            if event.type == pg.MOUSEBUTTONDOWN:

                # If the user clicked on the input_box rect.
                if input_box.collidepoint(event.pos):

                    # Toggle the active variable.
                    active = True
                elif button_rect.collidepoint(event.pos):
                    Downloading_music(text)
                    myspleeterrun()
                    song_start()
                    finish = True
                else:
                    active = False
                    finish = False

                # Change the current color of the input box.
                color = color_active if active else color_inactive

            if event.type == pg.KEYDOWN:

                if active:
                    if event.key == pg.K_RETURN:
                        print(text)
                        text = ''

                    elif event.key == pg.K_ESCAPE:
                        done = True

                    elif event.key == pg.K_BACKSPACE:
                        text = text[:-1]

                    elif pg.key.get_mods() & pg.KMOD_CTRL and event.key == pg.K_v:
                        text = pyperclip.paste()

                    else:
                        text += event.unicode


        screen.fill((255,255,255))

        # Render the current text.
        txt_surface = font.render(text, True, color)

        # Resize the box if the text is too long.
        width = max(200, txt_surface.get_width()+10)
        input_box.w = width

        # Blit the text.
        screen.blit(txt_surface, (input_box.x+5, input_box.y+5))
        screen.blit(t, text_rect)
        screen.blit(button, button_rect)
        if finish == True:
            screen.blit(finish_text, finish_text_rect)

        # Blit the input_box rect.
        pg.draw.rect(screen, color, input_box, 2)

        pg.display.flip()
        clock.tick(30)


if __name__ == '__main__':
    pg.init()
    main()
    pg.quit()