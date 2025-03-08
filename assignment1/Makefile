# Compiler
CXX = g++

# Compiler flags
CXXFLAGS = -std=c++17 -Wall

# Target executable
TARGET = fcm
GEN_TARGET = generator
TESTS_TARGET = runTests

# Source files
SRCS = fcm.cpp
GEN_SRCS = generator.cpp
TESTS_SRCS = runTests.cpp

# Object files
OBJS = $(SRCS:.cpp=.o)
GEN_OBJS = $(GEN_SRCS:.cpp=.o)
TESTS_OBJS = $(TESTS_SRCS:.cpp=.o)

# Default target
all: $(TARGET) $(GEN_TARGET) $(TESTS_TARGET) clean_objs

# Link the target executable
$(TARGET): $(OBJS)
	$(CXX) $(CXXFLAGS) -o $(TARGET) $(OBJS)

$(GEN_TARGET): $(GEN_OBJS)
	$(CXX) $(CXXFLAGS) -o $(GEN_TARGET) $(GEN_OBJS)

$(TESTS_TARGET): $(TESTS_OBJS)
	$(CXX) $(CXXFLAGS) -o $(TESTS_TARGET) $(TESTS_OBJS)

# Compile source files into object files
%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c $< -o $@

# Clean up build files
clean:
	rm -f $(TARGET) $(GEN_TARGET) $(TESTS_TARGET) $(OBJS)

clean_objs:
	rm -f $(OBJS) $(GEN_OBJS) $(TESTS_OBJS)

# Run the program
run: $(TARGET)
	./$(TARGET) input.txt -k 3 -a 0.5

.PHONY: all clean run clean_objs