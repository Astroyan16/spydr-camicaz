/*
 * camicaz.cpp
 *
 *  Created on: 11 juin 2012
 *      Author: sevin
 *
 * Code based on a NI example program:
 *    ContReadDigChan-ExtClk.c
 *
 */

#include "camicaz.h"
#include <algorithm>
#include <boost/property_tree/ptree.hpp>
#include <boost/property_tree/ini_parser.hpp>
#include <boost/date_time.hpp>
#include <boost/algorithm/string.hpp>

using namespace std;
using namespace boost;

#define DAQmxErrChk(functionCall) if( DAQmxFailed(error=(functionCall)) ) throw getLastError(__LINE__);

Camicaz::Camicaz(int nbDims, int *dims,
		 std::string portCam, int speedCam, int timeoutCam,
		 std::string portChopping, int speedChopping, int timeoutChopping,
		 int nbMonitoring,
		 std::string portList, std::string sampClkTiming) {

  this->size = 1;
  this->nbDims = nbDims;
  this->dims = new long int[nbDims];
  for (int index = 0; index < nbDims; index++) {
    stringstream buf;
    buf << "camera.dim" << index;
    string key(buf.str());
    this->dims[index] = dims[index];
    size *= dims[index];
  }

  /*********************************************/
  // USB Configure Code
  /*********************************************/
  this->portCam = portCam;
  this->speedCam = speedCam;
  this->timeoutCam = timeoutCam;

  this->portChopping = portChopping;
  this->speedChopping = speedChopping;
  this->timeoutChopping = timeoutChopping;

  this->nbMonitoring = nbMonitoring;

  this->portList = portList;
  this->sampClkTiming = sampClkTiming;

  initCam();
}

Camicaz::Camicaz(std::string configfile) {

  boost::property_tree::ptree pt;
  try {
    boost::property_tree::ini_parser::read_ini(configfile, pt);

    this->size = 1;
    this->nbDims = pt.get<int>("camera.nbDims");
    this->dims = new long int[nbDims];
    for (int index = 0; index < nbDims; index++) {
      stringstream buf;
      buf << "camera.dim" << index;
      string key(buf.str());
      this->dims[index] = pt.get<int>(key);
      size *= dims[index];
    }

    /*********************************************/
    // USB Configure Code
    /*********************************************/
    this->portCam = pt.get<std::string>("serial.cameraPort");
    this->speedCam = pt.get<int>("serial.cameraSpeed");
    this->timeoutCam = pt.get<int>("serial.cameraTimeOut");

    this->portChopping = pt.get<std::string>("serial.ChoppingPort");
    this->speedChopping = pt.get<int>("serial.ChoppingSpeed");
    this->timeoutChopping = pt.get<int>("serial.ChoppingTimeOut");

    this->nbMonitoring = pt.get<int>("serial.HKNumber");

    this->portList = pt.get<std::string>("NI.portList");
    this->sampClkTiming = pt.get<std::string>("NI.sampClkTiming");

    initCam();
  } catch (std::string& e) {
    cerr << "Error : " << e << endl;
    return;
  } catch (boost::property_tree::ini_parser_error& e) {
    cerr << "Error : " << e.what() << endl;
    return;
  } catch (boost::property_tree::ptree_bad_data& e) {
    cerr << "Error ptree_bad_data: " << e.what() << endl;
    return;
  } catch (boost::property_tree::ptree_bad_path& e) {
    cerr << "Error ptree_bad_path: " << e.what() << endl;
    return;
  } catch (boost::property_tree::ptree_error& e) {
    cerr << "Error ptree_error: " << e.what() << endl;
    return;
  } catch (...) {
    cerr << "error " << __FILE__ << "@" << __LINE__ << endl;
    return;
  }
}

void Camicaz::initCam() {

  this->error = 0;
  this->taskHandle = 0;
  this->camOpen = false;
  this->camAcquire = false;
  this->camGetImage = false;
  this->newFrame = false;
  this->portUsed = false;
  this->lastFrame = 0L;
  this->serialFdChopping = 0;
  this->freq = 0.0;
  this->lastErrorMessage = "Camera backend not initialized";
  this->expo=0;
  this->latency=0;
  this->filter=0;
  this->waitFrame=50000;
  this->serialCam = 0L;

  try {
    /*********************************************/
    // USB Configure Code
    /*********************************************/
    if(portCam.compare("/dev/null")!=0) {
      this->serialCam = new TimeoutSerial(portCam,speedCam);
      this->serialCam->setTimeout(posix_time::seconds(timeoutCam));
    } else this->serialCam = 0L;

    if(portChopping.compare("/dev/null")!=0) {
      this->serialFdChopping = open(portChopping.c_str(), O_RDWR);
    } else this->serialFdChopping = 0;

    /*********************************************/
    // DAQmx Configure Code
    /*********************************************/
    DAQmxErrChk(DAQmxCreateTask("",&taskHandle));

    DAQmxErrChk(DAQmxCreateDIChan(taskHandle,this->portList.c_str(),"",DAQmx_Val_ChanForAllLines));
    DAQmxErrChk(DAQmxCfgSampClkTiming(taskHandle,this->sampClkTiming.c_str(),1000.0,DAQmx_Val_Rising,DAQmx_Val_FiniteSamps,size));
    DAQmxErrChk(DAQmxCfgInputBuffer(taskHandle, size));

    pthread_t grab_loop;
    pthread_create(&grab_loop, NULL, Camicaz::start_cam, (void*) this);
    usleep(100000);
    this->lastErrorMessage = "Camera ready";

  } catch (std::string& e) {
    cerr << "Error : " << e << endl;
    this->lastErrorMessage = e;
    unsetupCam(false);
    return;
  } catch (boost::system::system_error& e) {
    cerr << "Error: can't open " << this->portCam
	 << ", " << e.what() << endl;
    this->lastErrorMessage = e.what();
    unsetupCam(false);
    return;
  } catch (...) {
    cerr << "error " << __FILE__ << "@" << __LINE__ << endl;
    this->lastErrorMessage = "Unknown camera initialization error";
    unsetupCam(false);
    return;
  }
}

void* Camicaz::start_cam(void* camera_arg) {
  Camicaz *camera = (Camicaz*) camera_arg;
  camera->grab();
  return (void*) 0L;
}

void Camicaz::grab() {
  this->lastFrame = new uInt32[size];
  this->camOpen = true;
  unsigned char index = 0;
  int32 sampsRead;
  boost::posix_time::ptime start =
    boost::posix_time::microsec_clock::universal_time();
  while (this->camOpen) {
    try {
      while(this->camGetImage) usleep(50000);

      this->camAcquire = true;
      /*********************************************/
      // DAQmx Start Code
      /*********************************************/
      DAQmxErrChk(DAQmxStartTask(taskHandle));

      /*********************************************/
      //Acquisition trigger
      /*********************************************/
      if (serialCam != 0L) {
        sendCmd(serialCam, "g0g1", false);
      } else
        break;

      /*********************************************/
      // DAQmx Read Code
      /*********************************************/
      DAQmxErrChk(DAQmxReadDigitalU32(taskHandle,size,2.0,DAQmx_Val_GroupByChannel,this->lastFrame,size,&sampsRead,NULL));

      //bool32 isLate=false;
      //DAQmxWaitForNextSampleClock(taskHandle,2.0, &isLate);
      DAQmxErrChk(DAQmxStopTask(taskHandle));
      this->newFrame = true;
      this->camAcquire = false;
      usleep(waitFrame);
      index++;

      if (index % 10 == 0) {
        boost::posix_time::time_duration duration =
	  boost::posix_time::microsec_clock::universal_time() - start;
        freq = 10. / duration.total_microseconds() * 1e6;
        //cerr << "freq " << freq << " time " << duration.total_microseconds()/1e6 << endl;
        start = boost::posix_time::microsec_clock::universal_time();
        index = 0;
      }
    } catch (std::string& e) {
      cerr << "Error : " << e << endl;
      this->lastErrorMessage = e;
      unsetupCam(false);
    } catch (boost::system::system_error& e) {
      cerr << "Error : " << e.what() << endl;
      this->lastErrorMessage = e.what();
      unsetupCam(false);
    } catch (...) {
      cerr << "error " << __FILE__ << "@" << __LINE__ << endl;
      this->lastErrorMessage = "Unknown acquisition error";
      unsetupCam(false);
    }
  }
  delete[] this->lastFrame;
  this->lastFrame = 0L;
}

string Camicaz::getLastError(int line) {
  if (DAQmxFailed (error)) {
    char errBuff[2048];
    DAQmxGetExtendedErrorInfo(errBuff, 2048);
    stringstream buff;
    buff << string(errBuff) << " at line " << line;
    return buff.str();
  }
  return string("Success!");
}

void Camicaz::unsetupCam(bool releaseDims) {
  this->camOpen = false;
  this->camAcquire = false;
  this->camGetImage = false;
  this->newFrame = false;
  this->portUsed = false;

  usleep(100000);
  if (releaseDims && dims != 0L) {
    delete[] dims;
    dims = 0L;
  }

  /*********************************************/
  // USB Stop Code
  /*********************************************/
  if (serialCam != 0L) {
    if (serialCam->isOpen()) {
      serialCam->close();
    }
    delete serialCam;
    serialCam = 0L;
  }

  if (serialFdChopping != 0) {
    close(serialFdChopping);
    serialFdChopping = 0;
  }

  if (taskHandle != 0) {
    /*********************************************/
    // DAQmx Stop Code
    /*********************************************/
    DAQmxClearTask(taskHandle);
    taskHandle = 0;
    error = 0;
  }
}

Camicaz::~Camicaz() {
  unsetupCam();
  if (DAQmxFailed (error))
    cerr << getLastError(__LINE__) << endl;
  ;
}

long int *Camicaz::getDims() {
  return this->dims;
}

long int Camicaz::getNbDims() {
  return this->nbDims;
}

const long int Camicaz::getSize() {
  return this->size;
}

int32 Camicaz::getNextImage(long int *data) {
  while (this->camAcquire) {
    if (!this->camOpen)
      return -1;
    usleep(25000);
  }
  this->newFrame=false;
  return getLastImage(data);
}

int32 Camicaz::getLastImage(long int *data) {
  try {
    if (!this->camOpen) {
      fill(data, data + this->size, 0L);
      return -1;
    }
    while (this->camAcquire || !this->newFrame) {
      if (!this->camOpen) {
        fill(data, data + this->size, 0L);
        return -1;
      }
      usleep(25000);
    }
    this->camGetImage = true;
    uInt32 doubleBuffer[this->size];
    copy(this->lastFrame, this->lastFrame + this->size, doubleBuffer);
    //memcpy(doubleBuffer, this->lastFrame, this->size*sizeof(uInt32));
    this->newFrame = false;
    this->camGetImage = false;
    long index = 0;
    long origins[4] = { dims[0] / 2 - 1, (dims[1] + 1) * dims[0] / 2 , dims[1] * dims[0] / 2, 0};
    uInt32 *ptrData = doubleBuffer;
    for (long indexn = 0; indexn < dims[2]; indexn++) {
      for (long indexx = 0; indexx < dims[0] / 2; indexx++) {
        for (long indexy = 0; indexy < dims[1] / 2; indexy++) {
          index = indexn * dims[0] * dims[1] + indexx * dims[1] + indexy;
          for (int i = 0; i < 4; i++)
            data[index + origins[i]] = *(ptrData++);
        }
      }
    }
  } catch (...) {
    cerr << "error " << __FILE__ << "@" << __LINE__ << endl;
    return -1;
  }
  return error;
}

int Camicaz::sendCmd(TimeoutSerial *serialPort, std::string cmd, long int value, bool endline) {
  stringstream buf;
  buf << cmd << value;
  string msg(buf.str());
  return sendCmd(serialPort, msg, endline);
}

int Camicaz::sendCmd(TimeoutSerial *serialPort, std::string msg, bool endline) {
  std::string result;
  return sendCmd(serialPort, &result, msg, endline);
}

int Camicaz::sendCmd(TimeoutSerial *serialPort, std::string *result, std::string msg, bool endline) {
  try {
    if (serialPort != 0L) {
      if(endline) msg.append("\n");
      while(portUsed) usleep(100000);
      portUsed = true;
      serialPort->flush();
      //cerr << "write " << msg << endl;
      serialPort->writeString(msg);
      //cerr << "reading " << endl;
      *result = serialPort->readStringUntil(string(">"));
      //cerr << "read " << *result << endl;
      portUsed = false;
   } else
      return -1;
  } catch (timeout_exception& e) {
    cerr << "Error : " << e.what() << endl;
    portUsed = false;
    return -2;
  } catch (boost::system::system_error& e) {
    cerr << "Error : " << e.what() << endl;
    portUsed = false;
    return -3;
  } catch (...) {
    cerr << "error " << __FILE__ << "@" << __LINE__ << endl;
    portUsed = false;
    return -4;
  }
  return 0;
}

int Camicaz::setExpo(int expo) {
  int result = sendCmd(this->serialCam, "t",expo, false);
  if (result < 0) return result;
  this->expo = expo;
  return expo;
}

int Camicaz::setLatency(int latency) {
  int result = sendCmd(this->serialCam, "l",latency, false);
  if (result < 0) return result;
  this->latency = latency;
  return latency;
}

int Camicaz::setChopping(int chopping){
  if (serialFdChopping == 0) {
    cerr << "Serial Chopping closed\n";
    return -1;
  }

  int status;
  
  if (ioctl(serialFdChopping, TIOCMGET, &status) == -1) {
    perror("get DTR state");
    return -1;
  }
 
  if (chopping==1) {
    status |= TIOCM_DTR;
  } else {
    status &= ~TIOCM_DTR;
  }

  while (this->camAcquire) {
    if (!this->camOpen) return -1;
    usleep(25000);
  }

  if (ioctl(serialFdChopping, TIOCMSET, &status) == -1) {
    perror("set DTR state");
    return -1;
  }
  this->chopping = chopping;
  return chopping;
}

int Camicaz::getMonitoring(int *monitoring, int size) {
  if (!this->camOpen) {
    fill(monitoring, monitoring + size, 0);
    return -1;
  }
  string monitor;
  int res=sendCmd(serialCam, &monitor, "u", true);
  if (res != 0 || monitor.length() < 4) {
    fill(monitoring, monitoring + size, 0);
    return res;
  }
  std::vector<std::string> HK;
  monitor=monitor.substr(3, monitor.length()-4);
  split(HK,monitor, is_any_of(" "));
  int HKsize = HK.size();
  if(size>HKsize) {
    cerr << "I receive only " << HKsize << "HKs" << endl;
    size = HKsize;
  }
  for(int i=0;i<size;i++){
    //cerr << i << " " << HK[i] << endl;
    std::stringstream ss;
    ss << std::hex << HK[i];
    ss >> monitoring[i];
  }

  return res;
}

int Camicaz::setHome() {
  return sendCmd(serialCam, "h", true);
}

int Camicaz::setFilter(int filter) {
  int result = sendCmd(this->serialCam, "f",filter, true);
  if (result < 0) return result;
  this->filter = filter;
  return filter;
}

int Camicaz::setParam(int expo, int latency, int filter) {
  int result = setExpo(expo);
  if (result < 0) return result;
  result = setLatency(latency);
  if (result < 0) return result;
  result = setFilter(filter);
  if (result < 0) return result;
  return 0;
}

int Camicaz::moveMotor(long int nbSteps) {
  return sendCmd(serialCam, "n", nbSteps, true);
}

int Camicaz::saveFilter(int filter) {
  return sendCmd(serialCam, "s", filter, true);
}

void camicaz_new(void** hCam, int nbDims, int* dims, 
		 char* portCam, int speedCam, int timeoutCam, 
		 char* portChopping, int speedChopping, int timeoutChopping,
		 int nbMonitoring, 
		 char* portList, char* sampClkTiming) {
  Camicaz *cam = new Camicaz(nbDims, dims, 
			     portCam, speedCam, timeoutCam, 
			     portChopping, speedChopping, timeoutChopping,
			     nbMonitoring, portList, sampClkTiming);
  *hCam = (void*)cam;
}

void camicaz_delete(void** hCam) {
  Camicaz *cam = (Camicaz *)(*hCam);
  delete cam;
  *hCam = 0L;
}

void camicaz_getNextImage(void* hCam, long int * data) {
  Camicaz *cam = (Camicaz *)hCam;
  cam->getNextImage(data);
}

void camicaz_getLastImage(void* hCam, long int * data) {
  Camicaz *cam = (Camicaz *)hCam;
  cam->getLastImage(data);
}

void camicaz_setExpo(void* hCam, int expo) {
  Camicaz *cam = (Camicaz *)hCam;
  cam->setExpo(expo);
}

void camicaz_setLatency(void* hCam, int latency) {
  Camicaz *cam = (Camicaz *)hCam;
  cam->setLatency(latency);
}

void camicaz_getMonitoring(void* hCam, int* monitoring, int size) {
  Camicaz *cam = (Camicaz *)hCam;
  cam->getMonitoring(monitoring, size);
}

int camicaz_getMonitoringSize(void* hCam) {
  Camicaz *cam = (Camicaz *)hCam;
  return cam->getMonitoringSize();
}

void camicaz_setHome(void* hCam) {
  Camicaz *cam = (Camicaz *)hCam;
  cam->setHome();
}

void camicaz_setFilter(void* hCam, int filter) {
  Camicaz *cam = (Camicaz *)hCam;
  cam->setFilter(filter);
}

void camicaz_saveFilter(void* hCam, int filter) {
  Camicaz *cam = (Camicaz *)hCam;
  cam->saveFilter(filter);
}

void camicaz_moveMotor(void* hCam, long int nbSteps) {
  Camicaz *cam = (Camicaz *)hCam;
  cam->moveMotor(nbSteps);
}

int camicaz_isOpen(void* hCam) {
  Camicaz *cam = (Camicaz *)hCam;
  return cam->isOpen() ? 1 : 0;
}
