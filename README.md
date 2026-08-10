# Ball Studios

A 2D physics simulator built from scratch in **Python** using **pygame-ce**.

![Showcase](showcase/showcase-gif.gif)

Ball Studios is a project focused on implementing and experimenting with physics systems such as gravity, collisions, friction, bouncing, and object interactions.


## Getting Started

### Download

#### Windows

[**Download Ball Studios**](https://github.com/AryanTheIndoDev/Physics-Simulator/releases/latest)

Download the latest release and run "Ball-Studios-Windows.exe"

#### macOS

macOS builds are currently not available.

### Manual Installation

#### Requirements

* Python 3.x
* pygame-ce 2.5.x

#### Installation

Clone the repository:

```bash
git clone https://github.com/AryanTheIndoDev/Physics-Simulator.git
cd Physics-Simulator
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

Run the simulator:

```bash
python main.py
```


## Features

* Multiple physics objects
* Gravity
* Object collisions
* Collision response
* Friction
* Bouncing and restitution
* Velocity and momentum visualization
* Interactive controls
* Configurable physics parameters

## Controls

| Input                 | Action                                  |
| --------------------- | --------------------------------------- |
| `Left Mouse Button`   | Grab objects                            |
| `Middle Mouse Button` | Change gravity to mouse                 |
| `Right Mouse Button`  | Interact with the simulation            |
| `Mouse Scroll`        | Switch interaction mode                 |
| `Arrow Keys`          | Change gravity direction                |
| `f`                   | Toggle Free Body Diagram mode           |
| `Esc`                 | Quit                                    |

> Controls may change as the project develops.

## How It Works

Ball Studios implements its physics systems directly rather than relying on a dedicated physics engine.

The simulator handles things such as:

* Position and velocity updates
* Acceleration due to gravity
* Collision detection
* Collision resolution
* Friction
* Bouncing
* Momentum-based interactions

The project is primarily an exploration of how these systems can be implemented and combined into a working physics simulation.

## Showcase

[▶ Watch the Full Showcase Video on YouTube](https://www.youtube.com/watch?v=rrPOUG59lfo)

## Future Plans

The project is currently in a usable state, but there is plenty of room for experimentation and improvement.

Possible future additions include:

* Improved friction and rolling physics
* Additional object types
* Better visualization of physical quantities
* Performance improvements
* Additional simulation tools

## Built With

* **Python**
* **pygame-ce**

## Author

**Aryan**

GitHub: [AryanTheIndoDev](https://github.com/AryanTheIndoDev)

---

*Ball Studios is a personal project built to learn, experiment, and have fun with physics and programming.*
