from dictionary import print_play, play_sound
import pygame
import getch

#print_play("Select or say 1 if you want to move your own pieces. Select or say 2 if you want me to move your pieces for you. Select or say 3 if you want me to replay your last game. Select or say 4 if you want to replay the legendary game Kasparov versus Deep Blue.", lang)

pygame.mixer.init(27300)
pygame.mixer.music.load('sounds/user_robot_control_en.wav')
pygame.mixer.music.play()

c = getch.getch()
pygame.mixer.music.stop()
print(c)
while (True):
    pass