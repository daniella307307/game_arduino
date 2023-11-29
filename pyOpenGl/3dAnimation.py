from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import serial
import json

ser = serial.Serial('COM20', 9600)  # Replace 'COM3' with your Arduino port

rotation_angle = 0.0

def draw_cube():
    glBegin(GL_QUADS)
    glVertex3f(-0.5, -0.5, -0.5)
    glVertex3f(0.5, -0.5, -0.5)
    glVertex3f(0.5, 0.5, -0.5)
    glVertex3f(-0.5, 0.5, -0.5)

    glVertex3f(-0.5, -0.5, 0.5)
    glVertex3f(0.5, -0.5, 0.5)
    glVertex3f(0.5, 0.5, 0.5)
    glVertex3f(-0.5, 0.5, 0.5)

    glVertex3f(-0.5, -0.5, -0.5)
    glVertex3f(0.5, -0.5, -0.5)
    glVertex3f(0.5, -0.5, 0.5)
    glVertex3f(-0.5, -0.5, 0.5)

    glVertex3f(-0.5, 0.5, -0.5)
    glVertex3f(0.5, 0.5, -0.5)
    glVertex3f(0.5, 0.5, 0.5)
    glVertex3f(-0.5, 0.5, 0.5)

    glVertex3f(-0.5, -0.5, -0.5)
    glVertex3f(-0.5, 0.5, -0.5)
    glVertex3f(-0.5, 0.5, 0.5)
    glVertex3f(-0.5, -0.5, 0.5)

    glVertex3f(0.5, -0.5, -0.5)
    glVertex3f(0.5, 0.5, -0.5)
    glVertex3f(0.5, 0.5, 0.5)
    glVertex3f(0.5, -0.5, 0.5)
    glEnd()

def display():
    global rotation_angle

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    try:
        data = ser.readline().decode().strip()
        if data:
            joystick_data = json.loads(data)
            joyX1, joyY1, joyX2, joyY2 = (
                joystick_data.get("joyX1", 0),
                joystick_data.get("joyY1", 0),
                joystick_data.get("joyX2", 0),
                joystick_data.get("joyY2", 0),
            )

            # Adjust your game logic here based on joystick input
            glTranslatef(joyX1 / 1024 - 0.5, joyY1 / 1024 - 0.5, -(joyX2 / 1024 - 0.5))
            rotation_angle += 1.0
            glRotatef(rotation_angle, 1, 1, 1)

    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")

    draw_cube()
    glutSwapBuffers()

glutInit()
glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
glutCreateWindow(b"Joystick Control Tutorial")
glutReshapeWindow(800, 600)
glutDisplayFunc(display)
glEnable(GL_DEPTH_TEST)
glutIdleFunc(display)
glutMainLoop()