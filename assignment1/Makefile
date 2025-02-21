# Compiler
CXX = g++

# Compiler flags
CXXFLAGS = -std=c++11 -Wall

# Target executable
TARGET = fcm

# Source files
SRCS = fcm.cpp

# Object files
OBJS = $(SRCS:.cpp=.o)

# Default target
all: $(TARGET) clean_objs

# Link the target executable
$(TARGET): $(OBJS)
	$(CXX) $(CXXFLAGS) -o $(TARGET) $(OBJS)

# Compile source files into object files
%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c $< -o $@

# Clean up build files
clean:
	rm -f $(TARGET) $(OBJS)

clean_objs:
	rm -f $(OBJS)

# Run the program
run: $(TARGET)
	./$(TARGET) input.txt -k 3 -a 0.5

.PHONY: all clean run clean_objs