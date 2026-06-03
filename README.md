Explanation:

This repository includes 4 main files:

1. constants.py -
Easy constant access to store it all in one place

2. mainscreen.py -
The main screen opens up as soon as you start the program, letting
you choose your role for the game. Which are equipped with working buttons.

3.dashboard.py -
This file will be used by the engineer role. It's equipped with real life
data calculated with high end physics and real stats that are getting sent
Straight from the microcontroller.


4. Driver.py -
This file will be used by the role of the driver.
driver.py is the only program where we send pockets into
The server, and data from the controller/keyboard to dashboard.py

(Explanation about the client will be in the Server README)

The actual program includes 2 different options for our clients to choose from :
1. "Driver"
2. "Engineer"

For the Driver role, the program will receive data from the controller/keyboard, and it change it to match the Servo Max and Min angles that were set acordently to the RC car
and send them straight to the Server part of the program.
For the throttle it will do the same.

For the Engineering role, the program won't let the user drive even if they try to plug a controller in or drive with the keyboard.
In this role the engineer will get specialized data that they can use to track the car for example: Speed (km/h), Angle, battery, Ping ect....
The program will not send any pockets but only receive data that will be sent

===============================================================================================================================

The purpose of this project is to demonstrate successful communication between a server and an infinite amount of clients.
These are built in two different coding languages and run on two completely different types of computers.
Communicating over wifi to apply results as real-world data and movement.

