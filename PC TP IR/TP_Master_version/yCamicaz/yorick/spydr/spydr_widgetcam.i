camtop = get_env("CAMTOP");
if (!camtop) 
  error,"CAMTOP is not defined!";

// load necessary files 
//require,"pyk.i"; 
require,"util_fr.i"; 
require,camtop+"/yorick/yCamicaz.i";
require,camtop+"/yorick/spydr/spydr_fitsutils.i";

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
  cam_homing,cam_handle;
}

func get_monitoring(one=){
  if(!cam_monitor) return;
  update_probe_values,cam_monitoring(cam_handle)*1.5;
  //after, 1, get_monitoring;
}
  
func start_monitoring(start){
  extern cam_monitor;
  if(start) {
    cam_monitor = 1;
    get_monitoring;
    cam_monitor = 0;
  } else {
    cam_monitor = 0;
  }
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
  cam_set_param, cam_handle, expo, latency, filter;
  
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
  file_date = tmp(2)+tmp(3)+"-"+tmp(5)+"-"+strtok(tmp(4),":",3)(1)+strtok(tmp(4),":",3)(2);

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
  error,"Unknown chopping sequence";
}

func record_image(typed,objectd,nb_images,fold,seqid,exp,lat,filt)
{
  extern cam_filename;
  extern cam_buffer;
  extern cam_freerun;
  extern cam_seqid,cam_seqind,cam_nimseq;
  extern cam_seqpattern;
  extern stop_record;
  
  pattern = cam_chop_pattern(seqid);
  if (nb_images < 1 || nb_images != long(nb_images))
    error,"Sequence count must be a positive integer";
  cam_stop_freerun;

  create_cam_filename,filename,typed,objectd,nb_images,filt,exp,lat;
  cam_filename = fold+"/"+filename;
  
  cam_buffer = -cam_get_image(cam_handle)(,,,-:1:1);

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

  if (stop_record) {
    camdata_save;
    return;
  }
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
  grow,cam_buffer,-cam_get_next_image(cam_handle);

  cam_seqind += 1;

  spydr_pyk,swrite(format=cmd_cam+"glade.get_widget('obs_progress').set_fraction(%f)",float(cam_seqind)/cam_nimseq);
  msg = swrite(format="acquiring image %d on %d",cam_seqind,cam_nimseq);
  spydr_pyk,swrite(format=cmd_cam+"glade.get_widget('obs_progress').set_text('%s')",msg);
  
  if (cam_nimseq > cam_seqind) after,0.1,add_image;
  else camdata_save,0;
}

func camdata_save(bckg)
{
  extern cam_buffer;
  extern cam_filename;
  
  if (cam_seqind > 1) cam_buffer = cam_buffer(,,,2:);
  else cam_buffer = cam_buffer(,,,2);

  if (bckg) {
    filename_bckg = cam_filename + "-" + bckg;
    if (!strmatch(filename_bckg,".fits")) filename_bckg += ".fits";
  }
  
  if (!strmatch(cam_filename,".fits")) cam_filename += ".fits";
  
  fits_write,cam_filename,cam_buffer,overwrite=1;
  if (bckg) fits_write,filename_bckg,cam_bckg_buffer,overwrite=1;
  
  spydr_pyk,swrite(format=cmd_cam+"glade.get_widget('record').set_sensitive(%d)",1);
  spydr_pyk,swrite(format=cmd_cam+"glade.get_widget('apply_param').set_sensitive(%d)",1);
  spydr_pyk,swrite(format=cmd_cam+"glade.get_widget('freerun').set_sensitive(%d)",1);
  spydr_pyk,swrite(format=cmd_cam+"glade.get_widget('acquire').set_sensitive(%d)",1);

  cam_load;
}

func abort_record
{
  extern stop_record;
  stop_record = 1;
  spydr_pyk,swrite(format=cmd_cam+"glade.get_widget('record').set_sensitive(%d)",1);
  spydr_pyk,swrite(format=cmd_cam+"glade.get_widget('apply_param').set_sensitive(%d)",1);
  spydr_pyk,swrite(format=cmd_cam+"glade.get_widget('freerun').set_sensitive(%d)",1);
  spydr_pyk,swrite(format=cmd_cam+"glade.get_widget('acquire').set_sensitive(%d)",1);
  //spydr_pyk,swrite(format=cmd_cam+"glade.get_widget('record').set_sensitive(%d)",1);  
}

func yo_cam_homing
{
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
