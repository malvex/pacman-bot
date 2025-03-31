# Pacman Bot

Simple bot that plays [pacman game](https://dos.zone/pac-man-nov-11-1982/) automatically by recognizing objects on screen.

## Goals

* MVP (Minimal Viable Product)
* No googling
* No LLM/AI
* No walls vision (for additional challenge to discover the maze)

## Features

* Each ghost tracked separately
* Automatic control of Pacman with a basic logic
* Auto-discovery of the map by trial-and-error and by watching paths of ghosts
* Map is stored in 2D grid using Numpy array for better performance
* Visual Map preview of what the bot sees, including what paths were explored
* Pathfinding (Simple Breadth-first search algorithm)
* Memory to remember locations even if we can't temporarily detect the object

## How it works?

* Python script uses Roboflow Inference Pipeline to recognize objects on screen.
* The screen is captured using OBS Virtual Camera (on linux you need v4l2loopback module to enable it).
* Python library [keyboard](https://pypi.org/project/keyboard/) is used to press the keyboard buttons.
* The script analyses the location of all objects on the map and makes decision based on several factors (read below).
* Walls are not visually recognized, instead we assume everything is a wall and we "reveal" the paths by watching pacman and ghosts locations as they walk.
* If the pacman stops moving, we trigger unstuck function that sends pacman to secondary direction based on the current target.
* Pacman stuck detection is done by checking the distance between pacman from current frame and pacman from previous frame.

## Next Steps and Future Improvements

* [ ] Fix tons of bugs (especially in pathfinding)
* [ ] Use OCR for current score
* [ ] Memory TTL (expiration)
* [ ] Optimize performance (cpu cycles, memory allocation)
* [ ] More complex bot behavior based on predicting future ghost location based on their current direction and speed
* [ ] Implementing actual pathfinding algorithm
* [ ] Easier setup - currently it requires OBS Virtual Camera + firefox to run the game

## Notes

* Some walls are only 2px wide, which requires fine grid resolution - initially I planned to implement small 2D grid based on the size of pacman, but the grid needs to be much thinner. Fortunately, numpy arrays are quite fast.

## Bot Decision making

1. (tbd)

## Detected classes

* pacman
* ghosts (green, yello, red, orange - each tracked separately)
* vulnerable-ghost (ghost we can eat after power-up)
* berry
* power pill (buff)

## How to Run this

```sh
# if you have go-task installed
task build
task run

# if you don't have go-task installed
poetry install
poetry run python3 src/main.py
```

## Linter

```sh
task lint
```
