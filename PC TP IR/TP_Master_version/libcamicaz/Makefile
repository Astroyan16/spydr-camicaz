LIB_NAME=libcamicaz.so

C_DIR=src
H_DIR=include
O_DIR=obj

RTC_DIR=/rtc/

C_OBJS=camicaz.o TimeoutSerial.o
OBJS := $(addprefix $(O_DIR)/,$(C_OBJS))

DEPLIBS= -L/usr/local/natinst/nidaqmx/lib -lnidaqmx -lboost_system -lstdc++ # 

CFLAGS= -Wall -fno-common -I$(H_DIR) -I/usr/local/natinst/nidaqmx/include # -DSIMU

ifneq ($(DEBUG),)
CFLAGS+= -g -DDEBUG
endif

# ------------------------------------- targets and rules for this package
# color for printf
#31=red, 32=green, 33=yellow,34=blue, 35=pink, 36=cyan, 37=white

all: $(LIB_NAME)

clean:
	@rm -f $(OBJS)

$(O_DIR)/%.o: $(C_DIR)/%.cpp
	@printf '\033[36m%s\033[31m%s\033[m\n' "Compiling     " $@
	@mkdir -p $(O_DIR)
	@$(CC) $(CFLAGS) $< -c -o $@

$(LIB_NAME): $(OBJS)
	@printf '\033[36m%s\033[31m%s\033[m\n' "Linking       " $(LIB_NAME)
	@$(CC) -shared $(DEPLIBS) -o $@ $^ 

darc : $(LIB_NAME) $(RTC_DIR)
	@cp include/camicaz.h $(RTC_DIR)/include
	@cp $(LIB_NAME) $(RTC_DIR)/lib