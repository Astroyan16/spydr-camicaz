camtop = get_env("CAMTOP");
if (!camtop) 
  error,"CAMTOP is not defined!";

// load necessary files 
//require,"pyk.i"; 
require,"util_fr.i"; 
require,camtop+"/yorick/yCamicaz.i";
require,camtop+"/yorick/spydr/spydr_fitsutils.i";
require,camtop+"/yorick/spydr/spydr_metadata.i";

cam_new             = yCamicaz_new;
cam_get_image       = yCamicaz_get_image;
cam_get_next_image  = yCamicaz_get_next_image;
cam_get_cube        = yCamicaz_get_cube;
cam_set_param       = yCamicaz_set_param;
cam_monitoring      = yCamicaz_get_monitoring;
cam_homing          = yCamicaz_set_home;
cam_chopping        = yCamicaz_set_chopping;
cam_is_open         = yCamicaz_is_open;

func cam_warn_if_unavailable(one=)
{
  extern cam_freerun;

  if (cam_is_open(cam_handle)) return;

  cam_stop_freerun;
  spydr_pyk_status_push,"Warning: no signal detected on the National Instruments card. Acquisition is unavailable.";
}

func cam_savebckg
{
  extern cam_bckg_buffer;

  if (dimsof(cam_buffer)(1) == 3) cam_bckg_buffer = cam_buffer;
  else cam_bckg_buffer = cam_buffer(,,,avg);
  spydr_pyk,cmd_cam+swrite(format="glade.get_widget('bckg_check').set_sensitive(%d)", 1);
}

func cam_sethome
{
  extern cam_applied_params;
  if (cam_recording) return;
  cam_applied_params=[];
  cam_homing,cam_handle;
}

func cam_monitor_unavailable(void)
{
  for (probe=1;probe<=4;probe++) {
    widget=swrite(format="glade.get_widget('probe%d')",probe);
    spydr_pyk,cmd_cam+widget+".set_text('N/A')";
    spydr_pyk,cmd_cam+widget+".modify_base(gtk.STATE_NORMAL, gtk.gdk.Color(50000, 50000, 50000))";
  }
}

func get_monitoring(one=){
  if (!cam_monitor) return;
  // Replace the single timer, including when Status is pressed manually.
  after,-,get_monitoring;
  // Freerun and Status callbacks run sequentially; protect recorded sequences.
  if (!gui_realized || cam_recording) {
    after,5,get_monitoring;
    return;
  }
  after,60,get_monitoring;
  if (catch(-1)) {
    cam_monitor_unavailable;
    return;
  }
  raw=[];
  if (cam_is_open(cam_handle)) raw=cam_monitoring(cam_handle);
  extern cam_last_probes,cam_last_probe_time;
  // Keep the last valid sample and its original age for FITS metadata.
  if (numberof(raw)==4) {
    if (allof(raw>0)) {
      cam_last_probes=raw;
      cam_last_probe_time=cam_epoch();
      update_probe_values,raw*1.5;
      return;
    }
  }
  cam_monitor_unavailable;
}
  
func start_monitoring(start){
  extern cam_monitor;
  after,-,get_monitoring;
  if(start) {
    cam_monitor = 1;
    get_monitoring;
  } else {
    cam_monitor = 0;
  }
}

func cam_start_auto_monitoring(void)
{
  extern cam_monitor;
  cam_monitor=1;
  after,-,get_monitoring;
  after,3,get_monitoring;
}

func update_probe_values(val)
{
  spydr_pyk,cmd_cam+swrite(format="glade.get_widget('probe1').set_text('%s')", swrite(format="%.1f",val(1)));
  if (val(1) < 85)
    spydr_pyk,cmd_cam+"glade.get_widget('probe1').modify_base(gtk.STATE_NORMAL, gtk.gdk.Color(0, 65535, 0))";
  else
    spydr_pyk,cmd_cam+"glade.get_widget('probe1').modify_base(gtk.STATE_NORMAL, gtk.gdk.Color(65535, 0, 0))";

  spydr_pyk,cmd_cam+swrite(format="glade.get_widget('probe2').set_text('%s')", swrite(format="%.1f",val(2)));
  if (val(2) < 85)
    spydr_pyk,cmd_cam+"glade.get_widget('probe2').modify_base(gtk.STATE_NORMAL, gtk.gdk.Color(0, 65535, 0))";
  else
    spydr_pyk,cmd_cam+"glade.get_widget('probe2').modify_base(gtk.STATE_NORMAL, gtk.gdk.Color(65535, 0, 0))";

  spydr_pyk,cmd_cam+swrite(format="glade.get_widget('probe3').set_text('%s')", swrite(format="%.1f",val(3)));
  if (val(3) < 150)
    spydr_pyk,cmd_cam+"glade.get_widget('probe3').modify_base(gtk.STATE_NORMAL, gtk.gdk.Color(0, 65535, 0))";
  else
    spydr_pyk,cmd_cam+"glade.get_widget('probe3').modify_base(gtk.STATE_NORMAL, gtk.gdk.Color(65535, 0, 0))";

  spydr_pyk,cmd_cam+swrite(format="glade.get_widget('probe4').set_text('%s')", swrite(format="%.1f",val(4)));
  if (val(4) < 110)
    spydr_pyk,cmd_cam+"glade.get_widget('probe4').modify_base(gtk.STATE_NORMAL, gtk.gdk.Color(0, 65535, 0))";
  else
    spydr_pyk,cmd_cam+"glade.get_widget('probe4').modify_base(gtk.STATE_NORMAL, gtk.gdk.Color(65535, 0, 0))";
}


func cam_stop_freerun(void)
{
  extern cam_freerun;
  cam_freerun = 0;
  after,-,freerun_loop;
}

func cam_set_freerun_chopping(enabled)
{
  extern cam_freechop;
  if (!cam_freerun) return;
  // Apply between frames, without restarting acquisition or resetting the phase.
  if (!enabled) cam_freechop = -1;
  else if (cam_freechop < 0) cam_freechop = 1;
}

func cam_start_freerun(run,chop){
  extern cam_freerun;
  extern cam_freechop;

  if (!run) {
    cam_stop_freerun;
    return;
  }
  if (cam_recording) {
    spydr_pyk_status_push,"Finish or save the current recording before starting freerun.";
    spydr_pyk,cmd_cam+"glade.get_widget('freerun').set_active(0)";
    return;
  }
  if (cam_freerun) return;
  after,-,freerun_loop;
  // A recorded cube may leave stale axis limits; live restarts keep user zoom.
  if (numberof(dimsof(cam_buffer))==5) {
    window,spydr_wins(1);
    unzoom;
    limits;
  }
  cam_freerun = 1;
  if (chop) cam_freechop = 1;
  else cam_freechop = -1;
  //spydr_pyk,cmd_cam+swrite(format="glade.get_widget('apply_param').set_sensitive(%d)", run);
  if(run) freerun_loop;
}

func freerun_loop(one=){
  extern cam_buffer;
  extern cam_freechop;

  if(!cam_freerun) return;
  // Cancel duplicates; schedule the next acquisition only after rendering.
  after,-,freerun_loop;
  if (catch(-1)) {
    cam_stop_freerun;
    spydr_pyk_status_push,"Freerun stopped: "+catch_message;
    spydr_pyk,cmd_cam+"glade.get_widget('freerun').set_active(0)";
    return;
  }
  if (!cam_is_open(cam_handle)) {
    error,"Camera unavailable";
  }
  cam_buffer = -cam_get_image(cam_handle);
  if (!cam_is_open(cam_handle)) error,"Camera acquisition failed";
  if (cam_freechop > -1) {
    cam_chopping,cam_handle,cam_freechop;
    cam_freechop += 1;
    cam_freechop = cam_freechop % 2;
  }
  if (numberof(cam_buffer_content)!=3) cam_load;
  cam_disp_select,cam_current_ndisp,cam_current_bckg,live=1;
  if (cam_freerun) after, 0.1, freerun_loop;
}
  
func snap_image(nb_images){
  extern cam_buffer,cam_name;
  if (cam_recording) return;
  if (catch(-1)) {
    cam_record_controls,0;
    spydr_pyk_status_push,"Snapshot failed: "+catch_message;
    return;
  }
  
  if(nb_images==1)
    cam_buffer = -cam_get_image(cam_handle);
  else
    cam_buffer = -cam_get_cube(cam_handle,nb_images);

  cam_name="last image";
  spydr_pyk,cmd_cam+"glade.get_widget('apply_param').set_sensitive(1)";
  spydr_pyk,cmd_cam+"glade.get_widget('freerun').set_sensitive(1)";
  spydr_pyk,cmd_cam+"glade.get_widget('acquire').set_sensitive(1)";
  //spydr_pyk,cmd_cam+"glade.get_widget('button_abort').set_sensitive(0)";

  cam_load;
}

func apply_param(filter,expo,latency){
  extern cam_applied_params;
  if (cam_recording) return;
  cam_applied_params=[];
  if (catch(-1)) {
    cam_record_controls,0;
    spydr_pyk_status_push,"Apply failed: "+catch_message;
    return;
  }
  if (filter<0 || filter>3 || expo<0 || expo>6 || latency<0 || latency>3)
    error,"Select valid camera parameters";
  cam_set_param, cam_handle, expo, latency, filter;
  if (!cam_is_open(cam_handle)) error,"Camera unavailable";
  cam_applied_params=[filter,expo,latency];
  
  spydr_pyk,cmd_cam+"glade.get_widget('apply_param').set_sensitive(1)";
  spydr_pyk,cmd_cam+"glade.get_widget('acquire').set_sensitive(1)";
  //spydr_pyk,cmd_cam+"glade.get_widget('button_abort').set_sensitive(0)";

}

func cam_load(void)
{
  extern cam_buffer,cam_im,cam_dim;
  extern cam_buffer_content;

  cam_dim = dimsof(cam_buffer)(1);

  //spydr_pyk,swrite(format=cmd_cam+"glade.get_widget('combodisp').insert_text(%d,'%s')",0,"Start");
  spydr_pyk,cmd_cam+"glade.get_widget('combodisp').get_model().clear()";
  cam_buffer_content = [];
  spydr_pyk,swrite(format=cmd_cam+"glade.get_widget('combodisp').insert_text(%d,'%s')",0,"Start");
  grow,cam_buffer_content,"Start";
  spydr_pyk,swrite(format=cmd_cam+"glade.get_widget('combodisp').insert_text(%d,'%s')",0,"End");
  grow,cam_buffer_content,"End";
  spydr_pyk,swrite(format=cmd_cam+"glade.get_widget('combodisp').insert_text(%d,'%s')",0,"Diff");
  grow,cam_buffer_content,"Diff";

  cam_buffer_content = cam_buffer_content(::-1);

  spydr_pyk,swrite(format=cmd_cam+"glade.get_widget('combodisp').set_active(%d)",0);
}
  
func cam_disp_select(ndisp,bckg,live=)
{
  extern cam_im, cam_current_ndisp, cam_current_bckg;

  if (ndisp<0 || ndisp>=numberof(cam_buffer_content)) return;
  cam_current_ndisp=ndisp;
  cam_current_bckg=bckg;
  // UI changes update the selection; the single freerun loop does the draw.
  if (cam_freerun && !live) return;
  dispType = cam_buffer_content(ndisp+1);  

  if (bckg) {
    if (strmatch(dispType,"End")) tmpbckg = cam_bckg_buffer(,,2);
    if (strmatch(dispType,"Start")) tmpbckg = cam_bckg_buffer(,,1);
    if (strmatch(dispType,"Diff")) tmpbckg = cam_bckg_buffer(,,2)-cam_bckg_buffer(,,1);
  } else tmpbckg = cam_buffer(,,1)*0.;

  if (dimsof(cam_buffer)(1) == 3) {
    if (strmatch(dispType,"End")) spydr,cam_buffer(,,2)-tmpbckg,replace=live;
    if (strmatch(dispType,"Start")) spydr,cam_buffer(,,1)-tmpbckg,replace=live;
    if (strmatch(dispType,"Diff")) spydr,cam_buffer(,,2)-cam_buffer(,,1)-tmpbckg,replace=live;
  } else {
    if (strmatch(dispType,"End")) spydr,cam_buffer(,,2,)-tmpbckg(,,-:1:dimsof(cam_buffer)(5));
    if (strmatch(dispType,"Start")) spydr,cam_buffer(,,1,)-tmpbckg(,,-:1:dimsof(cam_buffer)(5));
    if (strmatch(dispType,"Diff")) spydr,cam_buffer(,,2,)-cam_buffer(,,1,)-tmpbckg(,,-:1:dimsof(cam_buffer)(5));
  }
  
  disp_zoom,once=1;
}
 
func create_cam_filename(&filename,ntype,obj,nim,filter,texp,lat)
{
  if (ntype == 0) type = "Cal";
  if (ntype == 1) type = "Sci";
  if (ntype == 2) type = "Test";

  if ((obj == "") || (obj == [])) obj = "unknown";
  
  tmp = strtok(timestamp()," ",5);
  file_date = tmp(2)+tmp(3)+"-"+tmp(5)+"-"+strtok(tmp(4),":",3)(1)+strtok(tmp(4),":",3)(2)+strtok(tmp(4),":",3)(3);

  if (filter == 0) file_filt = "dark";
  if (filter == 1) file_filt = "J";
  if (filter == 2) file_filt = "H";
  if (filter == 3) file_filt = "K";
  
  if (texp == 0) file_exp = "75ms";
  if (texp == 1) file_exp = "90ms";
  if (texp == 2) file_exp = "110ms";
  if (texp == 3) file_exp = "173ms";
  if (texp == 4) file_exp = "277ms";
  if (texp == 5) file_exp = "485ms";
  if (texp == 6) file_exp = "1110ms";
  
  if (lat == 0) file_lat = "3ms";
  if (lat == 1) file_lat = "10ms";
  if (lat == 2) file_lat = "32ms";
  if (lat == 3) file_lat = "130ms";
  
  filename = type+"-"+obj+"-"+file_date+"-"+file_filt+"-"+file_exp;
 
  //spydr_pyk,swrite(format=cmd_cam+"save_cam_data('%s')",filename);
}

func cam_chop_pattern(seqid)
{
  // Logical A=0 (DTR off), B=1 (DTR on), as in the original ABAB mode.
  if (seqid == -1) return [];
  if (seqid == 0) return [0,1];
  if (seqid == 1) return [0,1,1,0];
  if (seqid == 2) return [0,0,1,1];
  if (seqid == 3) return [0,0,0,0,0,1,1,1,1,1];
  if (seqid == 4) return [0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1];
  if (seqid == 5) return [0,1,1,0,1,0,0,1,1,0,0,1,0,1,1,0];
  error,"Unknown chopping sequence";
}

func cam_record_controls(busy)
{
  spydr_pyk,cmd_cam+swrite(format="glade.get_widget('record').set_sensitive(%d)",!busy);
  spydr_pyk,cmd_cam+swrite(format="glade.get_widget('apply_param').set_sensitive(%d)",!busy);
  spydr_pyk,cmd_cam+swrite(format="glade.get_widget('freerun').set_sensitive(%d)",!busy);
  spydr_pyk,cmd_cam+swrite(format="glade.get_widget('acquire').set_sensitive(%d)",!busy);
  spydr_pyk,cmd_cam+swrite(format="glade.get_widget('button_stop').set_sensitive(%d)",busy);
}

func cam_unique_filename(base)
{
  candidate=base+".fits";
  index=0;
  while ((existing=open(candidate,"r",1))) {
    close,existing;
    index++;
    candidate=base+swrite(format="-%03d.fits",index);
  }
  return candidate;
}

func cam_finish_record(reason)
{
  extern cam_recording,stop_record,cam_filename,cam_record_partial;
  extern cam_meta_end,cam_meta_reason;
  if (!cam_recording) return;
  after,-,add_image;
  stop_record=1;
  if (catch(-1)) {
    // Keep the cube and acquisition lock until Stop retries a successful save.
    spydr_pyk,swrite(format="record_progress_state(4,%d,%d)",cam_seqind,cam_nimseq);
    spydr_pyk_status_push,"Save failed: "+catch_message+". Data retained; fix the disk/path and press Stop to retry.";
    return;
  }
  if (cam_seqind>0) {
    if (cam_meta_end==[]) {
      cam_meta_end=cam_epoch();
      cam_meta_reason=reason;
    }
    if (cam_seqind<cam_nimseq && !cam_record_partial) {
      cam_filename+="-partial";
      cam_record_partial=1;
    }
    spydr_pyk,swrite(format="record_progress_state(1,%d,%d)",cam_seqind,cam_nimseq);
    camdata_save,0;
  }
  cam_recording=0;
  cam_record_controls,0;
  requested=0;
  if (cam_seqind>0) {
    requested=cam_nimseq;
    state=3;
    if (cam_seqind==cam_nimseq && cam_meta_reason=="Recording complete.") state=2;
  } else {
    state=(reason=="Recording stopped; acquired exposures saved."?6:5);
  }
  spydr_pyk,swrite(format="record_progress_state(%d,%d,%d)",state,cam_seqind,requested);
  spydr_pyk_status_push,reason;
  if (cam_seqind>0) cam_load;
}

func cam_check_record_params(request_id,filt,expo,latency)
{
  status=1;
  if (cam_recording) status=2;
  else if (filt<0 || filt>3 || expo<0 || expo>6 || latency<0 || latency>3) status=3;
  else if (numberof(cam_applied_params)==3) {
    hardware_filters=[0,2,3,1];
    if (allof(cam_applied_params==[hardware_filters(filt+1),expo,latency])) status=0;
  }
  spydr_pyk,swrite(format="record_parameters_checked(%d,%d)",request_id,status);
}

// The historical funcdef wire parser accepts positional tokens only.
func cam_record_request(typed,objectd,nb_images,fold,seqid,exp,lat,filt,
                        observer,notes,metadata,focal,version,apply_first)
{
  // A prefix also avoids the old mini-parser's empty quoted-string bug.
  objectd=strpart(objectd,[1,strlen(objectd)]);
  observer=strpart(observer,[1,strlen(observer)]);
  notes=strpart(notes,[1,strlen(notes)]);
  metadata=strpart(metadata,[1,strlen(metadata)]);
  version=strpart(version,[1,strlen(version)]);
  record_image,typed,objectd,nb_images,fold,seqid,exp,lat,filt,
    observer=observer,notes=notes,metadata=metadata,focal=focal,
    version=version,apply_first=apply_first;
}

func record_image(typed,objectd,nb_images,fold,seqid,exp,lat,filt,observer=,notes=,metadata=,focal=,version=,apply_first=)
{
  extern cam_applied_params;
  extern cam_filename;
  extern cam_buffer;
  extern cam_freerun;
  extern cam_seqid,cam_seqind,cam_nimseq;
  extern cam_seqpattern;
  extern stop_record;
  extern cam_recording,cam_record_partial;
  
  if (cam_recording) {
    spydr_pyk_status_push,"A recording is still acquiring or waiting to be saved.";
    return;
  }
  cam_recording=1;
  cam_seqind=0;
  cam_record_partial=0;
  extern cam_meta,cam_meta_end,cam_meta_reason;
  cam_meta=[]; cam_meta_end=[]; cam_meta_reason="";
  cam_record_controls,1;
  applying=0;
  if (catch(-1)) {
    cam_finish_record,"Record stopped: "+catch_message;
    if (applying) spydr_pyk,"record_apply_failed()";
    return;
  }
  spydr_pyk,"record_progress_state(0,0,0)";
  pattern = cam_chop_pattern(seqid);
  if (nb_images < 1 || nb_images != long(nb_images))
    error,"Sequence count must be a positive integer";
  if (filt<0 || filt>3 || exp<0 || exp>6 || lat<0 || lat>3)
    error,"Select valid camera parameters";
  hardware_filters=[0,2,3,1];
  if (apply_first) {
    applying=1;
    cam_stop_freerun;
    cam_applied_params=[];
    spydr_pyk_status_push,"Applying camera settings; waiting for camera acknowledgement...";
    // Native setParam waits for each serial reply, including the filter command.
    cam_set_param,cam_handle,exp,lat,hardware_filters(filt+1);
    if (!cam_is_open(cam_handle)) error,"Camera unavailable after Apply";
    cam_applied_params=[hardware_filters(filt+1),exp,lat];
    applying=0;
  }
  if (numberof(cam_applied_params)!=3)
    error,"Apply camera parameters before starting Record";
  if (!allof(cam_applied_params==[hardware_filters(filt+1),exp,lat]))
    error,"Camera parameters changed; click Apply before starting Record";
  after,-,add_image;
  cam_stop_freerun;
  if (!cam_is_open(cam_handle)) error,"Camera unavailable";

  cam_metadata_begin,typed,objectd,nb_images,seqid,exp,lat,filt,
    (is_void(observer)?"":observer),(is_void(notes)?"":notes),
    (is_void(metadata)?"":metadata),(is_void(focal)?0.:focal),
    (is_void(version)?"unknown":version);

  create_cam_filename,filename,typed,objectd,nb_images,filt,exp,lat;
  cam_filename = fold+"/"+filename;
  
  cam_buffer = -cam_get_image(cam_handle)(,,,-:1:1);
  if (!cam_is_open(cam_handle)) error,"Camera acquisition failed";

  cam_seqid = seqid;
  // Snapshot the mode for this recording; later GUI changes affect the next one.
  cam_seqpattern = pattern;
  cam_nimseq = nb_images * max(1,numberof(pattern));

  cam_seqind = stop_record = 0;
  
  add_image;
}

func add_image
{
  extern cam_buffer;
  extern cam_seqind;

  if (!cam_recording) return;
  after,-,add_image;
  if (catch(-1)) {
    cam_finish_record,"Record stopped: "+catch_message;
    return;
  }
  if (stop_record) {
    cam_finish_record,"Recording stopped; acquired exposures saved.";
    return;
  }
  if (!cam_is_open(cam_handle)) error,"Camera unavailable";
  if (numberof(cam_seqpattern)) {
    phase = cam_seqind % numberof(cam_seqpattern) + 1;
    position = cam_seqpattern(phase);
    // Always impose the first position, even after a freerun ending on B.
    if (cam_seqind == 0) cam_chopping,cam_handle,position;
    else {
      previous = (cam_seqind-1) % numberof(cam_seqpattern) + 1;
      if (position != cam_seqpattern(previous)) cam_chopping,cam_handle,position;
    }
    // Keep the existing settling delay before requesting the next exposure.
    pause,500;
  }
  requested=yCamicaz_clock();
  frame=-cam_get_next_image(cam_handle);
  returned=yCamicaz_clock();
  if (!cam_is_open(cam_handle)) error,"Camera acquisition failed";
  extern cam_frame_log;
  state=-1;
  if (numberof(cam_seqpattern)) state=cam_seqpattern(phase);
  entry=array(0.,12,1);
  elapsed=(returned(3)-requested(3))+(returned(4)-requested(4))*1.e-9;
  entry(1:3,1)=[40587.+(requested(1)+requested(2)*1.e-9)/86400.,
                40587.+(returned(1)+returned(2)*1.e-9)/86400.,state];
  entry(4:5,1)=requested(1:2);
  entry(6:7,1)=returned(1:2);
  entry(8:9,1)=requested(3:4);
  entry(10:11,1)=returned(3:4);
  entry(12,1)=elapsed;
  grow,cam_buffer,frame;
  grow,cam_frame_log,entry;

  cam_seqind += 1;

  spydr_pyk,swrite(format=cmd_cam+"glade.get_widget('obs_progress').set_fraction(%f)",float(cam_seqind)/cam_nimseq);
  msg = swrite(format="acquiring image %d on %d",cam_seqind,cam_nimseq);
  spydr_pyk,swrite(format=cmd_cam+"glade.get_widget('obs_progress').set_text('%s')",msg);
  
  if (cam_nimseq > cam_seqind) after,0.1,add_image;
  else cam_finish_record,"Recording complete.";
}

func camdata_save(bckg)
{
  extern cam_buffer;
  extern cam_filename;
  
  if (cam_seqind > 1) data = cam_buffer(,,,2:);
  else data = cam_buffer(,,,2);
  filename=cam_unique_filename(cam_filename);

  if (bckg) {
    filename_bckg = cam_unique_filename(cam_filename + "-" + bckg);
  }
  
  cam_write_fits,filename,data;
  if (bckg) cam_write_fits,filename_bckg,cam_bckg_buffer,background=1;
  cam_filename=filename;
  cam_buffer=data;
}

func abort_record
{
  extern stop_record;
  if (!cam_recording) return;
  stop_record = 1;
  cam_finish_record,"Recording stopped; acquired exposures saved.";
}

func yo_cam_homing
{
  extern cam_applied_params;
  if (cam_recording) return;
  cam_applied_params=[];
  spydr_pyk,swrite(format=cmd_cam+"glade.get_widget('record').set_sensitive(%d)",0);
  spydr_pyk,swrite(format=cmd_cam+"glade.get_widget('apply_param').set_sensitive(%d)",0);
  spydr_pyk,swrite(format=cmd_cam+"glade.get_widget('freerun').set_sensitive(%d)",0);
  spydr_pyk,swrite(format=cmd_cam+"glade.get_widget('acquire').set_sensitive(%d)",0);
  cam_homing,cam_handle;
  spydr_pyk,swrite(format=cmd_cam+"glade.get_widget('record').set_sensitive(%d)",1);
  spydr_pyk,swrite(format=cmd_cam+"glade.get_widget('apply_param').set_sensitive(%d)",1);
  spydr_pyk,swrite(format=cmd_cam+"glade.get_widget('freerun').set_sensitive(%d)",1);
  spydr_pyk,swrite(format=cmd_cam+"glade.get_widget('acquire').set_sensitive(%d)",1);
}
  
/*
AB
ABBA 1xx45xx89xx1213xx16
AABB 

 */
