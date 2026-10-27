// Recording metadata and FITS serialization; no extra instrument transactions.
require,"fits.i";

func cam_epoch(void)
{
  clock=yCamicaz_clock();
  return clock(1)+clock(2)*1.e-9;
}

func cam_utc(seconds)
{
  // POSIX UTC calendar conversion, only at FITS save (no shell or time zone).
  // Gregorian civil date from day count, using 400-year eras (March origin).
  whole=floor(seconds);
  micros=0;
  if (1) {
    micros=long(floor((seconds-whole)*1.e6+0.5));
    if (micros==1000000) { whole+=1.; micros=0; }
  }
  days=long(floor(whole/86400.));
  daytime=long(whole-double(days)*86400.);
  z=days+719468;
  era=long(floor(z/146097.));
  doe=z-era*146097;
  yoe=long(floor((doe-long(floor(doe/1460.))+long(floor(doe/36524.))-
                 long(floor(doe/146096.)))/365.));
  year=yoe+era*400;
  doy=doe-(365*yoe+long(floor(yoe/4.))-long(floor(yoe/100.)));
  mp=long(floor((5*doy+2)/153.));
  day=doy-long(floor((153*mp+2)/5.))+1;
  month=mp+(mp<10?3:-9);
  if (month<=2) year+=1;
  hour=daytime/3600;
  minute=(daytime%3600)/60;
  second=daytime%60;
  prefix=swrite(format="%04d-%02d-%02dT%02d:%02d:%02d",year,month,day,hour,minute,second);
  if (1) return prefix+swrite(format=".%06dZ",micros);
  return prefix+"Z";
}

func cam_metadata_begin(kind,obj,count,mode,expo,lat,filt,observer,notes,payload,focal,version)
{
  extern cam_meta,cam_frame_log,cam_meta_end,cam_meta_reason;
  // Positional snapshot: never consult mutable GUI settings during save/retry.
  cam_meta=[kind,count,mode,expo,lat,filt,focal,cam_epoch()];
  extern cam_meta_object,cam_meta_observer,cam_meta_notes,cam_meta_payload,cam_meta_version;
  cam_meta_object=obj; cam_meta_observer=observer; cam_meta_notes=notes;
  cam_meta_payload=payload; cam_meta_version=version;
  cam_frame_log=[]; cam_meta_end=[]; cam_meta_reason="";
  extern cam_meta_clockres;
  cam_meta_clockres=yCamicaz_clock_resolution();
  extern cam_meta_probes,cam_meta_probe_time;
  cam_meta_probes=cam_last_probes;
  cam_meta_probe_time=cam_last_probe_time;
  extern cam_meta_config;
  cam_meta_config=[];
  if (camtop!=[] && cam_config!=[]) {
    config=open(camtop+"/"+cam_config,"r",1);
    if (config) {
      // rdline EOF is a nil string, not Yorick's void [] value.
      cam_meta_config=rdfile(config);
      close,config;
    }
  }
}

func cam_write_fits(filename,data,background=)
{
  fh=[];
  if (catch(-1)) {
    message=catch_message;
    if (fh!=[]) fits_close,fh;
    error,message;
  }
  fh=fits_create(filename,bitpix=fits_bitpix_of(data),dimlist=dimsof(data),
                 extend=1,overwrite=0);
  fits_set,fh,"ORIGIN","Spydr / Camicaz";
  fits_set,fh,"INSTRUME","NICMOS";
  fits_set,fh,"BUNIT","count","Digitizer counts; no photometric calibration";
  fits_set,fh,"METAVER",2,"Spydr recording metadata schema";
  fits_set,fh,"READ1","Start","Axis 3 plane 1";
  fits_set,fh,"READ2","End","Axis 3 plane 2; display Diff = End - Start";
  fits_set,fh,"CTYPE1","PIXEL";
  fits_set,fh,"CTYPE2","PIXEL";
  fits_set,fh,"CTYPE3","READ";
  if (numberof(dimsof(data))==5) fits_set,fh,"CTYPE4","EXPOSURE";
  fits_set,fh,"XPIXSZ",40.,"Native pixel pitch [um]";
  fits_set,fh,"YPIXSZ",40.,"Native pixel pitch [um]";
  fits_set,fh,"BGSUB",'F',"Recorded arrays are not background subtracted";
  fits_set,fh,"HISTORY","Camera arrays are quadrant-reconstructed and sign-inverted by Camicaz/Spydr. Start and End are retained; Diff is not stored.";
  if (numberof(cam_meta)==8) {
    types=["Calibration","Science","Test"];
    filters=["dark","J","H","K"];
    exposures=[0.075,0.090,0.110,0.173,0.277,0.485,1.110];
    latencies=[0.003,0.010,0.032,0.130];
    fits_set,fh,"OBSTYPE",types(long(cam_meta(1))+1);
    fits_set,fh,"OBJECT",cam_meta_object,"ASCII summary; full text in metadata payload";
    fits_set,fh,"OBSERVER",cam_meta_observer,"ASCII summary; full text in metadata payload";
    fits_set,fh,"COMMENT","User notes: "+cam_meta_notes;
    fits_set,fh,"FILTER",filters(long(cam_meta(6))+1);
    fits_set,fh,"EXPTIME",exposures(long(cam_meta(4))+1),"Nominal integration time [s]";
    fits_set,fh,"LATENCY",latencies(long(cam_meta(5))+1),"Nominal selected latency [s]";
    fits_set,fh,"EXPIDX",long(cam_meta(4)),"Applied exposure setting index";
    fits_set,fh,"LATIDX",long(cam_meta(5)),"Applied latency setting index";
    fits_set,fh,"NSAVED",cam_seqind,"Number of valid exposures in this file";
    fits_set,fh,"NREQUEST",cam_nimseq,"Requested total exposures";
    fits_set,fh,"NCYCLE",long(cam_meta(2)),"Requested cycles, or exposures if no chopping";
    fits_set,fh,"PARTIAL",(cam_seqind<cam_nimseq?'T':'F');
    fits_set,fh,"TIMESYS","UTC";
    fits_set,fh,"MJD-OBS",40587.+cam_meta(8)/86400.,"Host UTC before primer; not detector trigger";
    fits_set,fh,"DATE-OBS",cam_utc(cam_meta(8));
    if (numberof(cam_meta_end)) {
      fits_set,fh,"MJD-END",40587.+cam_meta_end/86400.,"Host UTC at stop, before save/retries";
      fits_set,fh,"DATE-END",cam_utc(cam_meta_end);
    }
    fits_set,fh,"DATE",cam_utc(cam_epoch()),"UTC file creation time";
    fits_set,fh,"TIMEPREC",max(cam_meta_clockres(1),1.e-6),"UTC date string resolution [s]; not accuracy";
    fits_set,fh,"UTCRES",cam_meta_clockres(1),"CLOCK_REALTIME nominal resolution [s]";
    fits_set,fh,"MONORES",cam_meta_clockres(2),"CLOCK_MONOTONIC nominal resolution [s]";
    fits_set,fh,"TIMESRC","clock_gettime","Host clocks; no hardware trigger timestamp";
    fits_set,fh,"STOPWHY",cam_meta_reason;
    fits_set,fh,"HISTORY","Recording termination: "+cam_meta_reason;
    fits_set,fh,"SOFTVER",cam_meta_version;
    fits_set,fh,"CHOPPING",(cam_meta(3)>=0?'T':'F');
    pattern="NONE";
    if (numberof(cam_seqpattern)) {
      pattern="";
      for (i=1;i<=numberof(cam_seqpattern);i++)
        pattern+=(cam_seqpattern(i)?"B":"A");
    }
    fits_set,fh,"CHOPPAT",pattern,"Repeated pattern; A=DTR off, B=DTR on";
    fits_set,fh,"CHOPWAIT",0.5,"Settling delay before each chopped exposure [s]";
    fits_set,fh,"CHOPMAP","A=0,B=1","Logical DTR; physical sky positions unverified";
    fits_set,fh,"FOCVALID",(cam_meta(7)>0?'T':'F');
    if (cam_meta(7)>0) {
      fits_set,fh,"FOCALLEN",cam_meta(7),"Effective focal length at detector [mm]";
      fits_set,fh,"PIXSCALE",(180.*3600./pi)*0.040/cam_meta(7),"Native scale [arcsec/pixel]; no celestial WCS";
    }
    valid=numberof(cam_meta_probes)==4;
    fits_set,fh,"HKVALID",(valid?'T':'F'),"Cached positive probe readout available";
    if (valid) {
      fits_set,fh,"HKMJD",40587.+cam_meta_probe_time/86400.,"UTC at last monitoring return; may be stale";
      fits_set,fh,"HKAGE",cam_meta(8)-cam_meta_probe_time,"Age at recording start [s]";
      fits_set,fh,"HKFACTOR",1.5,"Legacy conversion: displayed K = raw * factor";
      for (i=1;i<=4;i++) {
        fits_set,fh,swrite(format="HKRAW%d",i),cam_meta_probes(i),"Raw serial monitoring value";
        fits_set,fh,swrite(format="TEMP%d",i),cam_meta_probes(i)*1.5,"Displayed [K]; calibration/location unverified";
      }
    }
    if (strlen(cam_meta_payload)) {
      fits_set,fh,"METAFMT","JSON-UTF8-BASE64","Join META0001..METAnnnn then decode";
      chunks=long(ceil(strlen(cam_meta_payload)/60.));
      fits_set,fh,"METACNT",chunks;
      for (i=1;i<=chunks;i++)
        fits_set,fh,swrite(format="META%04d",i),strpart(cam_meta_payload,1+60*(i-1):min(60*i,strlen(cam_meta_payload)));
    }
    if (numberof(cam_meta_config)) {
      fits_set,fh,"COMMENT","Camera configuration snapshot (camicaz.ini):";
      for (i=1;i<=numberof(cam_meta_config);i++) fits_set,fh,"COMMENT",cam_meta_config(i);
    }
  }
  fits_write_header,fh;
  fits_write_array,fh,data;
  if (!background && numberof(cam_frame_log)) {
    fits_new_image,fh,cam_frame_log;
    fits_set,fh,"PCOUNT",0;
    fits_set,fh,"GCOUNT",1;
    fits_set,fh,"EXTNAME","FRAMELOG";
    fits_set,fh,"COL1","MJD-REQUEST","Host UTC before blocking camera read";
    fits_set,fh,"COL2","MJD-RETURN","Host UTC after successful camera read";
    fits_set,fh,"COL3","DTR","0=A, 1=B, -1=uncontrolled (no chopping)";
    fits_set,fh,"COL4","UTCREQ_S","Unix UTC whole seconds before read";
    fits_set,fh,"COL5","UTCREQ_N","UTC nanoseconds within COL4 second";
    fits_set,fh,"COL6","UTCRET_S","Unix UTC whole seconds after read";
    fits_set,fh,"COL7","UTCRET_N","UTC nanoseconds within COL6 second";
    fits_set,fh,"COL8","MONOREQ_S","Monotonic whole seconds before read";
    fits_set,fh,"COL9","MONOREQ_N","Monotonic nanoseconds within COL8 second";
    fits_set,fh,"COL10","MONORET_S","Monotonic whole seconds after read";
    fits_set,fh,"COL11","MONORET_N","Monotonic nanoseconds within COL10 second";
    fits_set,fh,"COL12","READ_DT","Monotonic elapsed read duration [s]";
    fits_set,fh,"UTCRES",cam_meta_clockres(1);
    fits_set,fh,"MONORES",cam_meta_clockres(2);
    fits_set,fh,"COMMENT","Image array [12,NSAVED]. First three columns retain schema 1 meanings. MJD doubles are rounded; separate seconds/nanoseconds preserve native readings. Monotonic times are relative to host boot. These are not detector trigger timestamps.";
    fits_write_header,fh;
    fits_write_array,fh,cam_frame_log;
  }
  fits_close,fh;
}

cam_meta=[];
cam_frame_log=[];
cam_last_probes=[];
cam_last_probe_time=[];
cam_meta_config=[];
cam_meta_clockres=[];
