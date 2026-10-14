# these values filled in by    yorick -batch make.i
Y_MAKEDIR=/home/etudiants/yorick.git/relocate
Y_EXE=/home/etudiants/yorick.git/relocate/bin/yorick
Y_EXE_PKGS=

Y_EXE_HOME=/home/etudiants/yorick.git/relocate
Y_EXE_SITE=/home/etudiants/yorick.git/relocate
Y_HOME_PKG=

# ----------------------------------------------------- optimization flags

# options for make command line, e.g.-   make COPT=-g TGT=exe
COPT=$(COPT_DEFAULT)
TGT=$(DEFAULT_TGT)
# ------------------------------------------------ macros for this package

I_DIR=yorick
O_DIR=obj

LIB_CAMICAZ_DIR ?= /home/etudiants/Packages/tp_master/tags/TP_Master_version/libcamicaz

PKG_NAME = yCamicaz
PKG_I=$(I_DIR)/yCamicaz.i

C_OBJS= yCamicaz.o
OBJS := $(addprefix $(O_DIR)/,$(C_OBJS))


# change to give the executable a name other than yorick
#PKG_EXENAME=yorick

# PKG_DEPLIBS=-Lsomedir -lsomelib   for dependencies of this package
PKG_DEPLIBS = -L/usr/local/natinst/nidaqmx/lib -lnidaqmx 
PKG_DEPLIBS+= -L$(LIB_CAMICAZ_DIR) -lcamicaz
PKG_DEPLIBS+= -L-lboost_system -lstdc++ # 

# set compiler (or rarely loader) flags specific to this package
#PKG_CFLAGS= -Wall -g -O3 -DUNIX -DADD_ -DGPUSHMEM=130 -fPIC -Xlinker -zmuldefs -fno-common -I$(H_DIR) -I/usr/local/cuda/include 
PKG_CFLAGS= -Wall -fno-common -I$(LIB_CAMICAZ_DIR)/include -I/usr/local/natinst/nidaqmx/include # -DSIMU

ifneq ($(DEBUG),)
PKG_CFLAGS+= -g -DDEBUG
endif

#-I/usr/local/cula/include
PKG_LDFLAGS=

# list of additional package names you want in PKG_EXENAME
# (typically Y_EXE_PKGS should be first here)
EXTRA_PKGS=$(Y_EXE_PKGS)

# list of additional files for clean
PKG_CLEAN=

# autoload file for this package, if any
PKG_I_START=
# non-pkg.i include files for this package, if any
PKG_I_EXTRA= 

# -------------------------------- standard targets and rules (in Makepkg)

#--compiler-options -fpermissive 

# set macros Makepkg uses in target and dependency names
# DLL_TARGETS, LIB_TARGETS, EXE_TARGETS
# are any additional targets (defined below) prerequisite to
# the plugin library, archive library, and executable, respectively
PKG_I_DEPS=$(PKG_I)
Y_DISTMAKE=distmake

include $(Y_MAKEDIR)/Make.cfg
include $(Y_MAKEDIR)/Makepkg
include $(Y_MAKEDIR)/Make$(TGT)

# override macros Makepkg sets for rules and other macros
# Y_HOME and Y_SITE in Make.cfg may not be correct (e.g.- relocatable)
Y_HOME=$(Y_EXE_HOME)
Y_SITE=$(Y_EXE_SITE)

# reduce chance of yorick-1.5 corrupting this Makefile
MAKE_TEMPLATE = protect-against-1.5

# ------------------------------------- targets and rules for this package
# color for printf
#31=red, 32=green, 33=yellow,34=blue, 35=pink, 36=cyan, 37=white

# codger emits C; CC=g++ must not give its builtin references C++ linkage.
ywrap.o: ywrap.c $(H_YWRAP)
	$(CC) -x c $(CFLAGS) $(PKG_CFLAGS) -c $< -o $@

$(O_DIR)/%.o: %.cpp
	@printf '\033[36m%s\033[31m%s\033[m\n' "Compiling     " $@
	@mkdir -p $(O_DIR)
	$(CC) $(CFLAGS) $(PKG_CFLAGS) $< -c -o $@

$(PKG_NAME): $(OBJS)
	@printf '\033[36m%s\033[31m%s\033[m\n' "Linking       " $(PKG_NAME)
	$(CC) $(PKG_CPPFLAGS) $(PKG_DEPLIBS) -o $@ $^ 
