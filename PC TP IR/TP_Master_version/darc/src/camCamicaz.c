/*
darc, the Durham Adaptive optics Real-time Controller.
Copyright (C) 2010 Alastair Basden.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/
/**
   The code here is used to create a shared object library, which can then be swapped around depending on which cameras you have in use, ie you simple rename the camera file you want to camera.so (or better, change the soft link), and restart the coremain.

The library is written for a specific camera configuration - ie in multiple camera situations, the library is written to handle multiple cameras, not a single camera many times.
*/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "rtccamera.h"
#include <time.h>
#include <unistd.h>
#include <string.h>
#include <pthread.h>
#define __LINUX__ 1
#include "buffer.h"
#include "camicaz.h"
#include "darc.h"

typedef enum{
  CAMICAZEXPOSURE,
  CAMICAZFILTER,
  CAMICAZGETHK,
  CAMICAZHOMEFILTERW,
  CAMICAZLATENCY,
  CAMICAZMOVEFILTERW,
  CAMICAZSAVEFILTERW,
  CAMICAZUPDATEHK,
  //Add more before this line.
  CAMNBUFFERVARIABLES//equal to number of entries in the enum
}CAMBUFFERVARIABLEINDX;

#define camMakeNames() bufferMakeNames(CAMNBUFFERVARIABLES,"camicazExposure","camicazFilter","camicazHK","camicazHomeFW","camicazLatency","camicazMoveFW","camicazSaveFW","camicazUpdHK")

typedef struct{
  int frameno;
  int *imgdata;
  int npxls;
  unsigned int *userFrameNo;
  int ncam;
  int captureStarted;
  int camOpen;
  void *hCam;
  float frameRate;
  int expTime;
  int latency;
  int filter;
  circBuf *rtcErrorBuf;
  unsigned char *lastImgMem;
  int nFrames;
  int *HK;
  int nHK;
  char *paramNames;
  int index[CAMNBUFFERVARIABLES];
  void *values[CAMNBUFFERVARIABLES];
  char dtype[CAMNBUFFERVARIABLES];
  int nbytes[CAMNBUFFERVARIABLES];
}CamStruct;

void camdoFree(CamStruct *camstr){
  void *hCam=camstr->hCam;
  if(camstr!=NULL){
    if(camstr->paramNames!=NULL)
      free(camstr->paramNames);
    if(camstr->HK!=NULL)
      free(camstr->HK);
    free(camstr);
    camicaz_delete(&hCam);
  }
}

int camNewParam(void *camHandle,paramBuf *pbuf,unsigned int frameno,arrayStruct *arr){
  CamStruct *camstr=(CamStruct*)camHandle;
  int i,nfound;
  nfound=bufferGetIndex(pbuf,CAMNBUFFERVARIABLES,camstr->paramNames,camstr->index,camstr->values,camstr->dtype,camstr->nbytes);

  i=CAMICAZEXPOSURE;
  if(camstr->index[i]>=0){//has been found...
    if(camstr->dtype[i]=='i' && camstr->nbytes[i]==sizeof(int)){
      if(camstr->expTime!=*((int*)camstr->values[i])) {
	camstr->expTime=*((int*)camstr->values[i]);
	camicaz_setExpo(camstr->hCam, camstr->expTime);
	printf("camicazExposure set to t%d\n", camstr->expTime);
      }
    }else{
      printf("camicazExposure should be int\n");
    }
  }

  i=CAMICAZLATENCY;
  if(camstr->index[i]>=0){//has been found...
    if(camstr->dtype[i]=='i' && camstr->nbytes[i]==sizeof(int)){
      if(camstr->latency!=*((int*)camstr->values[i])){
	camstr->latency=*((int*)camstr->values[i]);
	camicaz_setLatency(camstr->hCam, camstr->latency);
	printf("camicazLatency set to l%d\n", camstr->latency);
      }
    }else{
      printf("camicazLatency should be int\n");
    }
  }

  i=CAMICAZFILTER;
  if(camstr->index[i]>=0){//has been found...
    if(camstr->dtype[i]=='i' && camstr->nbytes[i]==sizeof(int)){
      if(camstr->filter!=*((int*)camstr->values[i])){
	camstr->filter=*((int*)camstr->values[i]);
	camicaz_setFilter(camstr->hCam, camstr->filter);
	printf("camicazFilter set to l%d\n", camstr->filter);
      }
    }else{
      printf("camicazFilter should be int\n");
    }
  }

  i=CAMICAZHOMEFILTERW;
  if(camstr->index[i]>=0){//has been found...
    if(camstr->dtype[i]=='i' && camstr->nbytes[i]==sizeof(int) && *((int*)camstr->values[i])==1){
      camicaz_setHome(camstr->hCam);
      *((int*)camstr->values[i])=0;
      printf("Filter wheel set to home position");
    }
  }

  i=CAMICAZMOVEFILTERW;
  if(camstr->index[i]>=0){//has been found...
    if(camstr->dtype[i]=='i' && camstr->nbytes[i]==sizeof(int)){
      int nbSteps=*((int*)camstr->values[i]);
      if(nbSteps!=0){
	camicaz_moveMotor(camstr->hCam, nbSteps);
	*((int*)camstr->values[i])=0;
	printf("Camicaz filter wheel move to %d steps\n", nbSteps);
      }
    }else{
      printf("camicazMoveFW should be int\n");
    }
  }

  i=CAMICAZSAVEFILTERW;
  if(camstr->index[i]>=0){//has been found...
    if(camstr->dtype[i]=='i' && camstr->nbytes[i]==sizeof(int)){
      if(*((int*)camstr->values[i])>=0){
	camstr->filter=*((int*)camstr->values[i]);
	*((int*)camstr->values[CAMICAZFILTER])=camstr->filter;
	*((int*)camstr->values[i]) = -1;
	camicaz_saveFilter(camstr->hCam, camstr->filter);
	printf("Camicaz filter wheel position saved to f%d\n", camstr->filter);
      }
    }else{
      printf("camicazSaveFW should be int\n");
    }
  }

  i=CAMICAZUPDATEHK;
  if(camstr->index[i]>=0){//has been found...
    if(camstr->dtype[i]=='i' && camstr->nbytes[i]==sizeof(int) && *((int*)camstr->values[i])==1){
      camicaz_getMonitoring(camstr->hCam,camstr->HK,camstr->nHK);
      memcpy(camstr->values[CAMICAZGETHK], camstr->HK,camstr->nHK*sizeof(int));
      *((int*)camstr->values[i])=0;
      printf("Camicaz HK updated\n");
    }
  }

  return 0;
}


/**
   Open a camera of type name.  Args are passed in a int array of size n, which can be cast if necessary.  Any state data is returned in camHandle, which should be NULL if an error arises.
   pxlbuf is the array that should hold the data. The library is free to use the user provided version, or use its own version as necessary (ie a pointer to physical memory or whatever).  It is of size npxls*sizeof(short).
   ncam is number of cameras, which is the length of arrays pxlx and pxly, which contain the dimensions for each camera.
   Name is used if a library can support more than one camera.

   This library opens a FITS file (assumes 2880 header size), and uses this for the data.
   args here contains filename
*/

int camOpen(char *name,int n,int *args,paramBuf *pbuf,circBuf *rtcErrorBuf,char *prefix,arrayStruct *arr,void **camHandle,int nthreads,unsigned int thisiter,unsigned int **frameno,int *framenoSize,int npxls,int ncam,int *pxlx,int* pxly){
  CamStruct *camstr;
  int i;
  int *tmps;
  //INT cerr;
  //char *errtxt;
  //unsigned short *pxlbuf=arr->pxlbufs;
  printf("Initialising camera %s\n",name);
  if((*camHandle=malloc(sizeof(CamStruct)))==NULL){
    printf("Couldn't malloc camera handle\n");
    return 1;
  }
  memset(*camHandle,0,sizeof(CamStruct));
  camstr=(CamStruct*)*camHandle;
  camstr->paramNames=camMakeNames();
  camstr->rtcErrorBuf=rtcErrorBuf;

  if(arr->pxlbuftype!='i' || arr->pxlbufsSize!=sizeof(int)*npxls){
    //need to resize the pxlbufs...
    arr->pxlbufsSize=sizeof(int)*npxls;
    arr->pxlbuftype='i';
    arr->pxlbufelsize=sizeof(int);
    tmps=(int*)realloc(arr->pxlbufs,arr->pxlbufsSize);
    if(tmps==NULL){
      if(arr->pxlbufs!=NULL)
    	  free(arr->pxlbufs);
      printf("pxlbuf malloc error in camfile.\n");
      arr->pxlbufsSize=0;
      free(*camHandle);
      *camHandle=NULL;
      return 1;
    }
    arr->pxlbufs=tmps;
    memset(arr->pxlbufs,0,arr->pxlbufsSize);
  }
  if(ncam!=1){
    printf("Sorry - only 1 camera currently allowed\n");
    free(*camHandle);
    *camHandle=NULL;
    return 1;
  }
  camstr->imgdata=arr->pxlbufs;
  if(*framenoSize<ncam){
    if(*frameno!=NULL)free(*frameno);
    *frameno=malloc(sizeof(int)*ncam);
    if(*frameno==NULL){
      *framenoSize=0;
      printf("Unable to malloc camframeno\n");
    }else{
      *framenoSize=ncam;
    }
  }
  camstr->userFrameNo=*frameno;
  camstr->npxls=npxls;//*pxlx * *pxly;
  camstr->ncam=ncam;
  camstr->frameno=-1;
  for(i=0; i<ncam; i++){
    camstr->userFrameNo[i]=-1;
  }

  camstr->hCam=0L;
  int dims[3]={256,256,2};
  //fprintf(stderr, "avant 0x%8.8X", (int)camstr->hCam);
  camicaz_new(&(camstr->hCam), 3, dims,
	  		"/dev/ttyS0", 9600, 2,
	  		"/dev/ttyS1", 9600, 10,
	  		4,
	  		"Dev1/port2,Dev1/port3", "/Dev1/PFI3");
  //fprintf(stderr, "après 0x%8.8X", (int)camstr->hCam);
  camstr->camOpen=1;

  camstr->nHK = camicaz_getMonitoringSize(camstr->hCam);
  camstr->HK = (int *)malloc( camstr->nHK * sizeof(int) );
  memset(camstr->HK,0,camstr->nHK * sizeof(int));

  if(camNewParam(*camHandle,pbuf,thisiter,arr)!=0){
    printf("Error in camOpen->newParam...\n");
    camdoFree(camstr);
    *camHandle=NULL;
    return 1;
  }


  return 0;
}


/**
   Close a camera of type name.  Args are passed in the int array of size n, and state data is in camHandle, which should be freed and set to NULL before returning.
*/
int camClose(void **camHandle){
  CamStruct *camstr=(CamStruct*)*camHandle;
  printf("Closing camera\n");
  if(*camHandle==NULL)
    return 1;
  camdoFree(camstr);
  *camHandle=NULL;
  printf("Camera closed\n");
  return 0;
}


/**
   Called when we're starting processing the next frame.
*/
int camNewFrameSync(void *camHandle,unsigned int thisiter,double starttime){
  //printf("camNewFrame\n");
  CamStruct *camstr;
  //INT pitch;
  camstr=(CamStruct*)camHandle;
  if(camHandle==NULL){// || camstr->streaming==0){
    printf("called camNewFrame with camHandle==NULL\n");
    return 1;
  }
  memset(camstr->imgdata,0,sizeof(int)*camstr->npxls);

  camicaz_getLastImage(camstr->hCam, camstr->imgdata);

  camstr->frameno++;
  int i;
  for(i=0; i<camstr->ncam; i++){
    camstr->userFrameNo[i]++;//=camstr->frameno;
  }
  return 0;
}
