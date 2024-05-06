CC = g++
CFLAGS = -Wall -Wextra -Werror -pedantic -g

OBJDIR = objects
OBJS = $(addprefix $(OBJDIR)/, $(patsubst %.cpp, %.o, $(wildcard *.cpp)))

BINFOLDER = executable
BIN = $(BINFOLDER)/bager_parser

all : $(OBJDIR) $(BINFOLDER) $(BIN)

$(OBJDIR):
	mkdir $(OBJDIR)

$(BINFOLDER):
	mkdir $(BINFOLDER)

$(BIN) : $(OBJS)
	$(CC) $(OBJS) -o $(BIN) $(CFLAGS)

$(OBJDIR)/%.o : %.cpp
	$(CC) $(CFLAGS) -c $< -o $@

run:
	@./$(BIN)

clean:
	rm -rf $(wildcard *.o) objects

full_clean:
	rm -rf $(BIN) executable $(wildcard *.o) objects
