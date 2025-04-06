# Compiler and flags
CXX = g++
CXXFLAGS = -std=c++17 -Wall -O3
LDFLAGS = -pthread

# Target executables
TARGET = MetaClass
TARGET_SIMPLE = MetaClass_C
TARGET_NSMOOTH = MetaClass_NSmooth

# Source files
SRC_STANDARD = MetaClass.cpp
SRC_SIMPLE = MetaClass_C.cpp
SRC_NSMOOTH = MetaClass_NSmooth.cpp

# Object files
OBJ_STANDARD = $(SRC_STANDARD:.cpp=.o)
OBJ_SIMPLE = $(SRC_SIMPLE:.cpp=.o)
OBJ_NSMOOTH = $(SRC_NSMOOTH:.cpp=.o)

# Main target (builds all implementations)
all: $(TARGET) $(TARGET_SIMPLE) $(TARGET_NSMOOTH) %.clean

# Specific implementation targets
standard: $(TARGET)
simple: $(TARGET_SIMPLE)
nsmooth: $(TARGET_NSMOOTH)

# Link the standard executable
$(TARGET): $(OBJ_STANDARD)
	$(CXX) $(CXXFLAGS) -o $@ $^ $(LDFLAGS)

# Link the simple executable
$(TARGET_SIMPLE): $(OBJ_SIMPLE)
	$(CXX) $(CXXFLAGS) -o $@ $^

# Link the nsmooth executable
$(TARGET_NSMOOTH): $(OBJ_NSMOOTH)
	$(CXX) $(CXXFLAGS) -o $@ $^ $(LDFLAGS)

# Compile source files
%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c $< -o $@

# Remove .o files
%.clean:
	rm -f $(OBJ_STANDARD) $(OBJ_SIMPLE) $(OBJ_NSMOOTH)

# Clean up
clean:
	rm -f $(OBJ_STANDARD) $(OBJ_SIMPLE) $(OBJ_NSMOOTH) $(TARGET) $(TARGET_SIMPLE) $(TARGET_NSMOOTH) results.csv

# Run with default parameters (example with standard implementation)
run: $(TARGET)
	./$(TARGET) -d db.txt -s meta.txt -k 10 -a 0.1 -t 20

# Run simple implementation
run-simple: $(TARGET_SIMPLE)
	./$(TARGET_SIMPLE) -d db.txt -s meta.txt -k 10 -t 20

# Run nsmooth implementation
run-nsmooth: $(TARGET_NSMOOTH)
	./$(TARGET_NSMOOTH) -d db.txt -s meta.txt -k 10 -a 0.1 -t 20

# Install all implementations to /usr/local/bin
install: $(TARGET) $(TARGET_SIMPLE) $(TARGET_NSMOOTH)
	cp $(TARGET) /usr/local/bin
	cp $(TARGET_SIMPLE) /usr/local/bin
	cp $(TARGET_NSMOOTH) /usr/local/bin

.PHONY: all standard simple nsmooth clean run run-simple run-nsmooth install