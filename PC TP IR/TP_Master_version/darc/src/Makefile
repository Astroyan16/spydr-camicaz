##darc, the Durham Adaptive optics Real-time Controller.
#Copyright (C) 2010 Alastair Basden.

#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU Affero General Public License as
#published by the Free Software Foundation, either version 3 of the
#License, or (at your option) any later version.

#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU Affero General Public License for more details.

#You should have received a copy of the GNU Affero General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.

all: libcamCamicaz.so

#Makefilelibs libraries

#libraries:
#	echo "Makefile.libs not yet made - rerun make"
#librariesInstall:
#	echo "Makefile.libs not yet made - rerun make"
#librariesInstalldev:
#	echo "Makefile.libs not yet made - rerun make"
include ../Makefile.config
-include ../Makefile.config.local
include Makefile.libs

OPTS= #-g

SINC=$(BASE)/include
install: librariesInstall
	cp libcamCamicaz.so $(LIB)

clean:
	rm *.o
	rm *.so

Makefilelibs:
	echo "Removing Makefile.libs"
	rm -f Makefile.libs.save
	mv Makefile.libs Makefile.libs.save

#Makes a makefile that can be used for library installation.
Makefile.libs:
	echo "Making Makefile.libs"
	echo libraries: `ls lib*.so` > Makefile.libs
	echo "	echo Made libraries" >> Makefile.libs
	echo librariesInstall: `ls lib*.so` >> Makefile.libs
	echo "	cp " `ls lib*.so` $(LIB) >> Makefile.libs
	echo librariesInstalldev: `ls lib*.so` >> Makefile.libs
	echo "	echo \"Please make softlinks manually of lib*.so into ../lib\"" >> Makefile.libs


libcamCamicaz.so: camCamicaz.c $(SINC)/darc.h $(SINC)/darcNames.h $(SINC)/arrayStruct.h  $(SINC)/buffer.h 
	gcc -D_GNU_SOURCE -DPLATFORM_UNIX -fPIC -I../include -I/home/camicaz/workspace/libcamicaz/include -O3 $(OPTS) -c -Wall -o camCamicaz.o camCamicaz.c
	gcc $(OPTS) -O3 -shared -Wl,-soname,libcamCamicaz.so.1 -o libcamCamicaz.so.1.0.1 camCamicaz.o -lc -L/home/camicaz/workspace/libcamicaz -lcamicaz -L/usr/local/natinst/nidaqmx/lib -lnidaqmx
	/sbin/ldconfig -n ./
	rm -f libcamCamicaz.so
	ln -s  libcamCamicaz.so.1 libcamCamicaz.so
