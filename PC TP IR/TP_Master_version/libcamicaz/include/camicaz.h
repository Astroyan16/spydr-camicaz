/*
 * camicaz.h
 *
 *  Created on: 11 juin 2012
 *      Author: sevin
 *
 * Code based on a NI example program:
 *    ContReadDigChan-ExtClk.c
 *
 */

#ifndef CAMICAZ_H_
#define CAMICAZ_H_

#ifdef __cplusplus
#include <iostream>
#include <string>
#include <NIDAQmx.h>
#include "TimeoutSerial.h"

class Camicaz {
 private:
  int32 error;
  TaskHandle taskHandle;
  std::string portCam;
  int speedCam;
  int timeoutCam;
  TimeoutSerial *serialCam;
  std::string portChopping;
  int speedChopping;
  int timeoutChopping;
  int serialFdChopping;
  int numberOfHK;
  long int *dims;
  long int nbDims;
  long int size;
  bool camOpen;
  bool camAcquire;
  bool camGetImage;
  bool newFrame;
  bool portUsed;
  uInt32 *lastFrame;
  double freq;
  std::string lastErrorMessage;
  int expo;
  int latency;
  int chopping;
  int filter;
  int nbMonitoring;
  long waitFrame;

  std::string portList;
  std::string sampClkTiming;

  void initCam();
  void unsetupCam(bool releaseDims=true);
  static void *start_cam(void *camera_arg);
  void grab();
  int sendCmd(TimeoutSerial *serialCam, std::string cmd, long int value, bool endline);
  int sendCmd(TimeoutSerial *serialCam, std::string *result, std::string cmd, bool endline);
  int sendCmd(TimeoutSerial *serialCam, std::string cmd, bool endline);

 public:
  Camicaz(std::string configfile);
  Camicaz(int nbDims, int *dims,
	  std::string portCam, int speedCam, int timeoutCam,
	  std::string portChopping, int speedChopping, int timeoutChopping,
	  int nbMonitoring,
	  std::string portList=0L, std::string sampClkTiming=0L);
  virtual ~Camicaz();
  bool isOpen() {
    return camOpen;
  }
  double getFreq() {
    return freq;
  }
  int setWaitFrame(long wait) { this->waitFrame=wait; return 0;}

  long int getNbDims();
  long int *getDims();
  const long int getSize();
  int32 getNextImage(long *data);
  int32 getLastImage(long *data);
  std::string getLastError(int line);
  std::string getStatusMessage() { return lastErrorMessage; }

  int setParam(int expo, int latency, int filter);
  int setExpo(int expo);
  int setLatency(int latency);
  int setChopping(int chopping);

  int getMonitoring(int *monitoring, int size);
  int getMonitoringSize() {return this->nbMonitoring;}
  int setHome();
  int setFilter(int filter);
  int saveFilter(int filter);
  int moveMotor(long int nbSteps);

};

extern "C" {
#endif

  void camicaz_new(void **hCam, int nbDims, int *dims,
		   char *portCam, int speedCam, int timeoutCam,
		   char *portChopping, int speedChopping, int timeoutChopping,
		   int nbMonitoring,
		   char *portList, char *sampClkTiming);
  void camicaz_delete(void **hCam);

  void camicaz_getNextImage(void *hCam, long int *data);
  void camicaz_getLastImage(void *hCam, long int *data);

  void camicaz_setExpo(void *hCam, int expo);
  void camicaz_setLatency(void *hCam, int latency);

  void camicaz_getMonitoring(void *hCam, int *monitoring, int size);
  int  camicaz_getMonitoringSize(void *hCam);
  void camicaz_setHome(void *hCam);
  void camicaz_setFilter(void *hCam, int filter);
  void camicaz_saveFilter(void *hCam, int filter);
  void camicaz_moveMotor(void *hCam, long int nbSteps);
  int  camicaz_isOpen(void *hCam);

#ifdef __cplusplus
}
#endif


#endif /* CAMICAZ_H_ */
