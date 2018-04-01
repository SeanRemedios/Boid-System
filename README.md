# Boid-System
Craig Reynold's Boid System <br>
<i>for CISC 325, Queen's University by Sean Remedios</i>

## Usage
To run the program, type the following into a terminal window:
```
python3 boids.py
```

## Features
1. Wind - The boids are pushed in the direction of the wind. The wind activates after 10 seconds. The wind direction can change be changed by modifying the vector at the top of the file with the other constants.
2. Bound Position - The boids' positions are bounded to the screen. If a boid gets near to the edge of the screen, it's velocity is changed slowly in the opposite direction so it can move back towards the screen. This is so the boids don't go fully off the screen. The force at which the boids move back towards the middle and the area where their velocity is changed can be changed at the top of the file with the other constants.
3. Perching - When a boid reaches the bottom edge of the screen, it perches on the bottom edge for a random amount of time (minimum 20 ticks, maximum 100 ticks). The min and max perch times can be changed in the Boid Class' constructor.
4. Speed Limiting - The speed of the boids is always increasing so their velocity is limited to a certain value. This value can be changed at the top of the file with the other constants.

## Sources
The following links were used as a reference when creating this program:
1. TwoDVector: http://hplgit.github.io/primer.html/doc/pub/class/._class-readable004.html
2. Boid Pseudocode: http://www.kfish.org/boids/pseudocode.html
