# TAI - Group-7
## Installation Instructions

## Dependencies

Ensure you have the following dependencies installed:

- GCC: `sudo apt-get install gcc`
- Make: `sudo apt-get install make`

To compile the program on a Linux machine, ensure you have the necessary dependencies installed. You can compile the programs using the following commands:

```sh
make
```

## Running the Programs

### fcm

To run the `fcm` program, use the following command:

```sh
./fcm input_text.txt -k 3 -a 0.01
```

### generator

To run the `generator` program, use the following command (having in count that you already run the fcm program):

```sh
./generator -p ABC -s 500
```
