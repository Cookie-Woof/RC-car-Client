Explanition:

This repository includes 4 main files:

1. constants.py -
Easy Constants access to store it all in one place

2. mainscreen.py -
the main screen opens up as soon as you start the program letting
you choose your role for the game equiped with working buttons.

3.dashboard.py -
this file will be used by the engineer role. its equiped with real life
deta calculated with high end math and real stats that are getting sent
stright form the micro controller

4. Driver.py -
this file will be used by the role of the driver.
driver.py is the only program where we send pockets into
the server, and deta from the controller/keyboard to dashboard.py


(Explanition about the client will be in the Server README)

The actual program includes 2 diffrent options fro the our client to choose :

1. "Driver"
2. "Engineer"

For the Driver role, the program will recive deta from the controller/keyboard, it will chnages it to match the
Servo Max and Min angles that were set acordently to the RC car and send them stright to the Server part
of the program.
For the throttle it will do the same.

For the Engineering role, the program wont let the user drive even if they tried to plug a controller in or drive with the keyboard.
In this role the engineer will get spetific deta that they can use to track the car for exmpele: Speed(km/h), Angle, battery, Ping ect....
The program will not send any pockets but only recive deta that will be sent

===============================================================================================================================
The purpose of this project is to demonstrate successful communication between a server and an infinte amount of clients.
These are built in two different coding languages and run on two completely different types of computers,
communicating over wifi to apply results as real-world data and movement.

