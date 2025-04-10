# Compiler and flags
CXX = g++
CXXFLAGS = -std=c++17 -Wall -O3
LDFLAGS = -pthread

# Target executables
TARGET = MetaClass

# Source files
SRC_STANDARD = MetaClass.cpp

# Object files
OBJ_STANDARD = $(SRC_STANDARD:.cpp=.o)

# Main target (builds all implementations)
all: $(TARGET) %.clean

# Specific implementation targets
standard: $(TARGET)

# Link the standard executable
$(TARGET): $(OBJ_STANDARD)
	$(CXX) $(CXXFLAGS) -o $@ $^ $(LDFLAGS)

# Compile source files
%.o: %.cpp
	$(CXX) $(CXXFLAGS) -c $< -o $@

# Remove .o files
%.clean:
	rm -f $(OBJ_STANDARD)

# Clean up
clean:
	rm -f $(OBJ_STANDARD) $(TARGET) results.csv

# Run with default parameters (example with standard implementation)
run: $(TARGET)
	./$(TARGET) -d db.txt -s meta.txt -k 10 -a 0.1 -t 20

# Install all implementations to /usr/local/bin
install: $(TARGET)
	cp $(TARGET) /usr/local/bin
	
.PHONY: all standard  clean run install