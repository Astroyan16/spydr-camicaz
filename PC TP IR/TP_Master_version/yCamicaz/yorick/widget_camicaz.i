/*
  This collection of routines is part of the styc package
  
  Example of a yorick file associated to a widget

  Please include routines dedicated only to this widget
  Generic routines should be written in styc_utils.i file
*/

// Environment check
styctop = get_env("STYCTOP");
if (!styctop) //styctop = "~/workspace/GUI_Canary/styc";
  error,"STYCTOP is not defined!";

// load necessary files : yorick-python wrapper and styc_utils
require,"pyk.i"; //styctop+"/yorick/pyk.i";
require,styctop+"/yorick/styc_utils.i";
require,"util_fr.i"; //styctop+"/yorick/util_fr.i";
require,styctop+"/yorick/yCamicaz.i";

//pyk_debug=1;

//////////////////////////////////////////////////////////
//              **********************                 //
//////    THIS IS WHERE YOU DEFINE YOUR ROUTINES   ///////
//              **********************                 //
//////////////////////////////////////////////////////////

func camicaz_quit
{
  quit;
}

//////////////////////////////////////////////////////////
// A basic set of display functions
//////////////////////////////////////////////////////////
func camicaz_focus_in(void)
{
  extern camicaz_win_had_focus;

  cw=current_window();
  if (noneof(cw==camicaz_wins)) {
      if (cw>-1) camicaz_win_had_focus = cw;
  }
  //  write,format="camicaz focus in, old = %d\n",camicaz_win_had_focus;
}

func camicaz_focus_out(void)
{
  extern camicaz_win_had_focus;
  if (camicaz_win_had_focus>-1) {
    window,camicaz_win_had_focus;
    //    write,format="camicaz focus out, restored focus to %d\n",camicaz_win_had_focus;
  }
}

func camicaz_win_init(pid1,pid2,redisp=)
{
  extern camicaz_gui_realized;
  extern xid1,xid2;

  xid1=pid1; xid2=pid2;
  
  stylename = "gray.gp"; //styctop+"/gs/ncpa_styc.gs";
 
  window,camicaz_wins(1),dpi=camicaz_defaultdpi,width=0,height=0,   \
    xpos=-2,ypos=-2,parent=pid1; //,style=stylename;
  limits,square=1;
  palette,"gray.gp"; // need this if loadct is used!?

  if (!camicaz_gui_realized) {
    window,camicaz_wins(2),dpi=32,style="nobox.gs",parent=pid2,    \
      ypos=-27,xpos=-4;
    limits,square=1;
  }
  camicaz_set_lut,camicaz_lut;
  if (redisp) return;
}

func rad4zoom_incr(void) { camicaz_rad4zoom=min(rad4zoom+1,camicazs(imnum).dims(2)/2); }
func rad4zoom_decr(void) { camicaz_rad4zoom=max(rad4zoom-1,0); }


func camicaz_savebckg
{
  extern camicaz_bckg_buffer;

  if (dimsof(camicaz_buffer)(1) == 3) camicaz_bckg_buffer = camicaz_buffer;
  else camicaz_bckg_buffer = camicaz_buffer(,,,avg);
}

func get_monitoring(one=){
  if(!camicaz_monitor) return;

  //sesame_exec, camicaz_server, "GETMONIT"  
  after, 10, get_monitoring;
}
  
func start_monitoring(start){
  extern camicaz_monitor;
  if(start) {
    camicaz_monitor = 1;
    get_monitoring
  } else {
    camicaz_monitor = 0;
  }
}

func follow_update(void)
{
  extern camicaz_min, camicaz_max,camicaz_avg,camicaz_sum,camicaz_rms;
  
  tmp = camicaz_im(follow_pos(1)-5:follow_pos(1)+5,follow_pos(2)-5:follow_pos(2)+5);
  tmp=tmp(*);
  camicaz_min += 0.2*min(tmp);
  camicaz_max += 0.2*max(tmp);
  camicaz_avg += 0.2*avg(tmp);
  camicaz_sum += 0.2*sum(tmp);
  camicaz_rms += 0.2*tmp(rms);
  
  camicaz_min /= 1.2;
  camicaz_max /= 1.2;
  camicaz_avg /= 1.2;
  camicaz_sum /= 1.2;
  camicaz_rms /= 1.2;
  
  write,format="min : %.2f | max : %.2f | avg : %.2f | sum : %.2f | rms : %.2f\n",camicaz_min,
    camicaz_max,camicaz_avg,camicaz_sum,camicaz_rms;
}

func get_follow(one=){
  if(!camicaz_follow) return;
  follow_update;
  after, 0.5, get_follow;
}
func start_follow(start){
  extern camicaz_follow;
  extern follow_pos;
  extern camicaz_min, camicaz_max,camicaz_avg,camicaz_sum,camicaz_rms;
  
  if(start) {
    write,"Click on source";
    follow_pos = long(mouse(1,0,"")(1:2));
    camicaz_follow = 1;
    write,"Region stats";
    tmp = camicaz_im(follow_pos(1)-5:follow_pos(1)+5,follow_pos(2)-5:follow_pos(2)+5);
    tmp=tmp(*);
    camicaz_min = min(tmp);
    camicaz_max = max(tmp);
    camicaz_avg = avg(tmp);
    camicaz_sum = sum(tmp);
    camicaz_rms = tmp(rms);
    get_follow;
  } else {
    camicaz_follow = 0;
  }
}

func camicaz_start_freerun(run){
  extern camicaz_freerun;
  camicaz_freerun = run;
  //window,camicaz_wins(1);
  //fma;
  //animate, 1;
  pyk,cmd_camicaz+swrite(format="glade.get_widget('apply_param').set_sensitive(%d)", run);
  if(run) freerun_loop;
}

func freerun_loop(one=){
  extern camicaz_buffer;
  if(!camicaz_freerun) return;
  camicaz_buffer = -yCamicaz_get_image(camicaz_handle);
  camicaz_disp_select,camicaz_current_ndisp,1;
  camicaz_disp_zoom;
  //camicaz_load;
  after, 0.1, freerun_loop;
}
  
func snap_image(nb_images){
  extern camicaz_buffer,camicaz_name;
  
  if(nb_images==1)
    camicaz_buffer = -yCamicaz_get_image(camicaz_handle);
  else
    camicaz_buffer = -yCamicaz_get_cube(camicaz_handle,nb_images);

  camicaz_name="last image";
  camicaz_load;
  pyk,cmd_camicaz+"glade.get_widget('apply_param').set_sensitive(1)";
  pyk,cmd_camicaz+"glade.get_widget('freerun').set_sensitive(1)";
  pyk,cmd_camicaz+"glade.get_widget('acquire').set_sensitive(1)";
  pyk,cmd_camicaz+"glade.get_widget('button_abort').set_sensitive(0)";

}

func apply_param(filter,expo,latency){
  //sesame_exec, camicaz_server, swrite(format="SET_FILT_f%d --silent", filter);
  //sesame_exec, camicaz_server, swrite(format="SET_EXPO_t%d --silent", expo);
  //sesame_exec, camicaz_server, swrite(format="SET_LATE_l%d --silent", latency);
  //camicaz_set_filter, camicaz_handle, filter;
  //camicaz_set_expo, camicaz_handle, expo;
  //camicaz_set_latency, camicaz_handle, latency;
  yCamicaz_set_param, camicaz_handle, expo, latency, filter;
  
  pyk,cmd_camicaz+"glade.get_widget('apply_param').set_sensitive(1)";
  pyk,cmd_camicaz+"glade.get_widget('acquire').set_sensitive(1)";
  pyk,cmd_camicaz+"glade.get_widget('button_abort').set_sensitive(0)";

}

func camicaz_openfile(name)
{
  extern camicaz_buffer,camicaz_name;
  
  camicaz_buffer = fits_read(name);
  camicaz_name = basename(name);
  camicaz_load;
}

func camicaz_load(void)
{
  extern camicaz_buffer,camicaz_im,camicaz_dim;
  extern camicaz_buffer_content;

  camicaz_dim = dimsof(camicaz_buffer)(1);

  /* remplacer par xxx.get_model().clear()
  for (cc=1;cc<=100;cc++)
    pyk,swrite(format=cmd_camicaz+"glade.get_widget('winselect_camicaz').remove_text(%d)",0);
  */
  
  pyk,cmd_camicaz+"glade.get_widget('winselect_camicaz').get_model().clear()";
  camicaz_buffer_content = [];
  if (camicaz_bckg_buffer != []) {
    pyk,swrite(format=cmd_camicaz+"glade.get_widget('winselect_camicaz').insert_text(%d,'%s')",0,"Start-bckg");
    grow,camicaz_buffer_content,"Start-bckg";
    pyk,swrite(format=cmd_camicaz+"glade.get_widget('winselect_camicaz').insert_text(%d,'%s')",0,"End-bckg");
    grow,camicaz_buffer_content,"End-bckg";
    pyk,swrite(format=cmd_camicaz+"glade.get_widget('winselect_camicaz').insert_text(%d,'%s')",0,"Diff-bckg");
    grow,camicaz_buffer_content,"Diff-bckg";
  }
  pyk,swrite(format=cmd_camicaz+"glade.get_widget('winselect_camicaz').insert_text(%d,'%s')",0,"Start");
  grow,camicaz_buffer_content,"Start";
  pyk,swrite(format=cmd_camicaz+"glade.get_widget('winselect_camicaz').insert_text(%d,'%s')",0,"End");
  grow,camicaz_buffer_content,"End";
  pyk,swrite(format=cmd_camicaz+"glade.get_widget('winselect_camicaz').insert_text(%d,'%s')",0,"Diff");
  grow,camicaz_buffer_content,"Diff";

  camicaz_buffer_content = camicaz_buffer_content(::-1);

  /* remplacer par xxx.get_model().clear()
  for (cc=1;cc<=100;cc++)
    pyk,swrite(format=cmd_camicaz+"glade.get_widget('winselect_camicaz1').remove_text(%d)",0);
  */
  pyk,cmd_camicaz+"glade.get_widget('winselect_camicaz1').get_model().clear()";

  if (camicaz_dim == 4) {
    for (cc=dimsof(camicaz_buffer)(5);cc>=1;cc--) 
      pyk,swrite(format=cmd_camicaz+"glade.get_widget('winselect_camicaz1').insert_text(%d,'%s')",0,swrite(format="# %d",cc));
    pyk,swrite(format=cmd_camicaz+"glade.get_widget('winselect_camicaz1').insert_text(%d,'%s')",0,"Avg");
    pyk,swrite(format=cmd_camicaz+"glade.get_widget('winselect_camicaz1').set_active(%d)",0);
  }

  pyk,swrite(format=cmd_camicaz+"glade.get_widget('winselect_camicaz').set_active(%d)",0);  
}
  
func camicaz_disp_select(ndisp,ndisp_im)
{
  extern camicaz_im, camicaz_current_ndisp;

  camicaz_current_ndisp=ndisp;
  dispType = camicaz_buffer_content(ndisp+1);  

  if (strmatch(dispType,"bckg")) {
    if (strmatch(dispType,"End")) tmpbckg = camicaz_bckg_buffer(,,2);
    if (strmatch(dispType,"Start")) tmpbckg = camicaz_bckg_buffer(,,1);
    if (strmatch(dispType,"Diff")) tmpbckg = camicaz_bckg_buffer(,,2)-camicaz_bckg_buffer(,,1);
  } else tmpbckg = 0.;

  if (dimsof(camicaz_buffer)(1) == 3) {
    if (strmatch(dispType,"End")) camicaz_im = camicaz_buffer(,,2)-tmpbckg;
    if (strmatch(dispType,"Start")) camicaz_im = camicaz_buffer(,,1)-tmpbckg;
    if (strmatch(dispType,"Diff")) camicaz_im = camicaz_buffer(,,2)-camicaz_buffer(,,1)-tmpbckg;
  } else {
    if (ndisp_im == 0) {
      if (strmatch(dispType,"End")) camicaz_im = camicaz_buffer(,,2,avg)-tmpbckg;
      if (strmatch(dispType,"Start")) camicaz_im = camicaz_buffer(,,1,avg)-tmpbckg;
      if (strmatch(dispType,"Diff")) camicaz_im = camicaz_buffer(,,2,avg)-camicaz_buffer(,,1,avg)-tmpbckg;
    } else {
      if (strmatch(dispType,"End")) camicaz_im = camicaz_buffer(,,2,ndisp_im)-tmpbckg;
      if (strmatch(dispType,"Start")) camicaz_im = camicaz_buffer(,,1,ndisp_im)-tmpbckg;
      if (strmatch(dispType,"Diff")) camicaz_im = camicaz_buffer(,,2,ndisp_im)-camicaz_buffer(,,1,ndisp_im)-tmpbckg;
    }
  }
  camicaz_disp_cpc;
  camicaz_disp;
}
 
func create_camicaz_filename(ntype,nim,nframes,filter,texp)
{
  if (ntype == -1) type = "NoName";
  else type = camicaz_buffer_content(ntype+1);
  if (!strmatch(type,"Diff")) {
    if (!strmatch(type,"bckg")) type = "All";
    else type = "All-bckg";
  }
  
  tmp = strtok(timestamp()," ",5);
  file_date = "-"+tmp(2)+tmp(3)+"-"+tmp(5)+"-"+strtok(tmp(4),":",3)(1)+strtok(tmp(4),":",3)(2);

  if (filter == 0) file_filt = "-dark-";
  if (filter == 1) file_filt = "-J-";
  if (filter == 2) file_filt = "-H-";
  if (filter == 3) file_filt = "-K-";
  
  if (texp == 0) file_filt = "-3ms-";
  if (texp == 1) file_filt = "-42ms-";
  if (texp == 2) file_filt = "-108ms-";
  if (texp == 3) file_filt = "-212ms-";
  
  if (nim == 0) file_suff = swrite(format="-avg%dframes.fits",nframes);
  else file_suff = ".fits";

  filename = type+file_date+file_suff;
 
  pyk,swrite(format=cmd_camicaz+"save_camicaz_data('%s')",filename);
}


func camicazdata_save(filename,ntype,nim,nframes)
{

  if (!strmatch(filename,".fits")) filename += ".fits";
  
  if (strmatch(filename,"Diff")) {
    if (strmatch(filename,"bckg")) {
      tmpbckg = camicaz_bckg_buffer(,,2)-camicaz_bckg_buffer(,,1)
      if (nim == -1) tmp = camicaz_buffer(,,2)-camicaz_buffer(,,1)-tmpbckg;
      if (nim == 0) tmp = camicaz_buffer(,,2,avg)-camicaz_buffer(,,1,avg)-tmpbckg;
      if (nim > 0) tmp = camicaz_buffer(,,2,)-camicaz_buffer(,,1,)-tmpbckg;
    } else {
      if (nim == -1) tmp = camicaz_buffer(,,2)-camicaz_buffer(,,1);
      if (nim == 0) tmp = camicaz_buffer(,,2,avg)-camicaz_buffer(,,1,avg);
      if (nim > 0) tmp = camicaz_buffer(,,2,)-camicaz_buffer(,,1,);
    }
  } else {
    if (strmatch(filename,"bckg")) {
      if (nim == -1) tmp = camicaz_buffer-camicaz_bckg_buffer;
      if (nim == 0) tmp = camicaz_buffer(,,,avg)-camicaz_bckg_buffer;
      if (nim > 0) {
        tmp = camicaz_buffer;
        for (cc=1;cc<=dimsof(tmp)(5);cc) tmp(,,,cc) -= camicaz_bckg_buffer;
      }
    } else tmp = camicaz_buffer;
  }
  
   fits_write,filename,tmp,overwrite=1;
}

func camicaz_send2spydr(ntype,nim)
{

  type = camicaz_buffer_content(ntype+1);
  
  if (strmatch(type,"Diff")) {
    if (strmatch(type,"bckg")) {
      tmpbckg = camicaz_bckg_buffer(,,2)-camicaz_bckg_buffer(,,1)+65635;
      if (nim == -1) tmp = camicaz_buffer(,,2)-camicaz_buffer(,,1)-tmpbckg+65635;
      if (nim == 0) tmp = camicaz_buffer(,,2,avg)-camicaz_buffer(,,1,avg)-tmpbckg+65635;
      if (nim > 0) tmp = camicaz_buffer(,,2,)-camicaz_buffer(,,1,)-tmpbckg+65635;
    } else {
      if (nim == -1) tmp = camicaz_buffer(,,2)-camicaz_buffer(,,1)+65635;
      if (nim == 0) tmp = camicaz_buffer(,,2,avg)-camicaz_buffer(,,1,avg)+65635;
      if (nim > 0) tmp = camicaz_buffer(,,2,)-camicaz_buffer(,,1,)+65635;
    }
  } 
  if (strmatch(type,"Start")) {
    if (strmatch(type,"bckg")) {
      if (nim == -1) tmp = camicaz_buffer(,,1)-camicaz_bckg_buffer(,,1);
      if (nim == 0) tmp = camicaz_buffer(,,1,avg)-camicaz_bckg_buffer(,,1);
      if (nim > 0) {
        tmp = camicaz_buffer(,,,1);
        for (cc=1;cc<=dimsof(tmp)(5);cc) tmp(,,,cc) -= camicaz_bckg_buffer(,,1);
      }
    } else {
      if (nim == -1) tmp = camicaz_buffer(,,1);
      if (nim == 0) tmp = camicaz_buffer(,,1,avg);
      if (nim > 0) tmp = camicaz_buffer(,,1,);
    }
  }
  if (strmatch(type,"End")) {
    if (strmatch(type,"bckg")) {
      if (nim == -1) tmp = camicaz_buffer(,,2)-camicaz_bckg_buffer(,,2);
      if (nim == 0) tmp = camicaz_buffer(,,2,avg)-camicaz_bckg_buffer(,,2);
      if (nim > 0) {
        tmp = camicaz_buffer(,,2,);
        for (cc=1;cc<=dimsof(tmp)(5);cc) tmp(,,,cc) -= camicaz_bckg_buffer(,,2);
      }
    } else {
      if (nim == -1) tmp = camicaz_buffer(,,2);
      if (nim == 0) tmp = camicaz_buffer(,,2,avg);
      if (nim > 0) tmp = camicaz_buffer(,,2,);
    }
  }
  
  spydr,tmp;
}

func camicaz_exportpng(name)
{
  extern camicaz_savedir;

  window,camicaz_wins(1);
  
  if (strpart(name,-3:0)!=".png") name+=".png";
  
  png,name;
  write,format="Image exported to %s\n",name;
  camicaz_pyk_status_push,swrite(format="Image exported to %s",name);
}

func camicaz_save(void)
{
  extern camicaz_savedir;
  name = camicaz_savedir+"/"+escapechar2save(camicazs(imnum).saveasname);
  if (strpart(name,-4:0) != ".fits") name+=".fits";
  //  fits_write,name,*camicazs(imnum).pim,overwrite=1;
  fits_write,name,camicaz_im,overwrite=1;
  write,format="Image saved in %s\n",name;
  camicaz_pyk_status_push,swrite(format="Image saved in %s",name);
}

func camicaz_saveas(name)
{
  extern camicaz_savedir;

  if (strpart(name,-4:0) != ".fits") name+=".fits";
  
  fits_write,name,camicaz_im,overwrite=1;
  write,format="Image saved in %s\n",name;
  camicaz_pyk_status_push,swrite(format="Image saved in %s",name);
}

func escapechar2save(s)
{
  s=streplace(s,strfind(".fits",s,n=20),"");
  s=streplace(s,strfind("/",s,n=20),":");
  s=streplace(s,strfind(" ",s,n=20),"_");
  return s;
}

func toggle_animate(state)
{
  plsys,1;
  if (state==0) fma;
  if (state!=[]) animate,state; else animate;
}


//==============================
// ZOOM, cursor and misc graphic
//==============================

prevxy = [0,0];

func get_cursor(wid)
/* DOCUMENT get_cursor(wid)
   returns [xpos,ypos]
   where xpos,ypos is the cursor x and y coordinates
   Returns [] if not in correct window;
   SEE ALSO:
 */
{
  if (wid==[]) wid=camicaz_wins(1);
  cur = current_mouse(wid);
  if (cur==[]) return;
  cur(1:2) = cur(1:2)+1; //ceil
  cur = long(cur);
  return cur;
}
  

camicaz_stop_zoom=0;
camicaz_zoom_started=0;

func camicaz_start_zoom(void)
{
  extern camicaz_stop_zoom,camicaz_zoom_started;
  if (camicaz_zoom_started) return; // already running.
  camicaz_zoom_started=1;
  camicaz_disp_zoom;
}
  
func camicaz_disp_zoom(once=)
{
  extern camicaz_stop_zoom,camicaz_zoom_started;
  extern camicaz_prevz,camicaz_prevxy;

  if (camicaz_im == []) {
    camicaz_zoom_started=0;
    return;
  }

  if (camicaz_stop_zoom) {
    camicaz_stop_zoom=0;
    return;
  }

  dimx = dimsof(camicaz_im)(2);
  dimy = dimsof(camicaz_im)(3);

  cur = get_cursor();
  if (cur==[]) { // not in correct window
    if (!once) after,0.05,camicaz_disp_zoom;
    return;
  }
if (allof(camicaz_prevxy==cur(1:2)) && (camicaz_prevz==camicaz_rad4zoom)) {  // same positon as before
    if (!once) after,0.05,camicaz_disp_zoom;
    return;
  }

  sys = cur(3);
  if (sys!=0) {
    i = clip(cur(1),1,dimx);
    j = clip(cur(2),1,dimy);
    pyk,swrite(format="y_camicaz_set_xyz('%d','%d','%4.5g')",\
               i,j,float(camicaz_im(i,j)));

    local_rad=min([5,camicaz_rad4zoom]);
    x1 = clip(i-local_rad,1,dimx);
    x2 = clip(i+local_rad,1,dimx);
    y1 = clip(j-local_rad,1,dimy);
    y2 = clip(j+local_rad,1,dimy);
    pyk,swrite(format="y_camicaz_text_parm_update('localmax','%4.5g')",\
               float(max(camicaz_im(x1:x2,y1:y2))));
    sim=camicaz_im(x1:x2,y1:y2);
    wm = where2(sim==max(sim))(,1)-local_rad-1;

    if ((i-local_rad)<1) wm(1) += (1-i+local_rad);
    if ((j-local_rad)<1) wm(2) += (1-j+local_rad);

    // FIXME: blue cursor is not at correct position when pointing lower than smaller indice

    x1 = i-camicaz_rad4zoom;
    x2 = i+camicaz_rad4zoom;
    y1 = j-camicaz_rad4zoom;
    y2 = j+camicaz_rad4zoom;
    
    if (x1<1) { x1=1; x2=2*camicaz_rad4zoom+1; }
    else if (x2>dimx) { x2=dimx; x1=x2-2*camicaz_rad4zoom; }      

    if (y1<1) { y1=1; y2=2*camicaz_rad4zoom+1; }
    else if (y2>dimy) { y2=dimy; y1=y2-2*camicaz_rad4zoom; }      

    window,camicaz_wins(2);
    fma;
    pli,camicaz_im(x1:x2,y1:y2),2*camicaz_rad4zoom+1,2*camicaz_rad4zoom+1;
    //    limits,0,2*rad4zoom+1,0,2*rad4zoom+1;
    limits;
    // plot local maxima location
    plp,j-y1+wm(2)+0.5,i-x1+wm(1)+0.5,symbol=2,color="blue",width=1;
    // plot cursor location
    plp,j-y1+0.5,i-x1+0.5,symbol=2,color="red",width=3;

    window,camicaz_wins(1);
  }
  camicaz_prevxy = cur(1:2);
  camicaz_prevz = camicaz_rad4zoom;
  if (!once) after,0.05,camicaz_disp_zoom;
}


func escapechar(s)
{
  s=streplace(s,strfind("_",s,n=20),"!_");
  s=streplace(s,strfind("^",s,n=20),"!^");
  return s;
}

func camicaz_redisp(void)
{
  camicaz_disp;
}

func camicaz_dispgui_update
{
  //pyk,swrite(format="y_camicaz_set_lut(%d)",camicaz_lut);
  pyk,swrite(format=cmd_camicaz+"camicaz_set_itt(%d)",clip(long(camicaz_itt-1),0,4));

}

func camicaz_set_lut(_lut)
// change the LookUp Table and Intensity Transfer Table
{
  require,"idl-colors.i";
  extern rlut,glut,blut;
  local r,g,b;
  extern camicaz_invertlut,camicaz_lut,camicaz_itt,camicaz_ncolors,camicaz_log_itt_dex;

  //  if ((!lut)||(lut==camicaz_lut)) return; // nothing to do.

  window,camicaz_wins(1);
  if (_lut!=[]) camicaz_lut = _lut;
  
  if (_lut!=[]) {  // then read and set new lut
    if (_lut==0) palette,"earth.gp";
    else loadct,_lut;
    palette,query=1,rlut,glut,blut;  // store
  }

  // invert?
  if (camicaz_invertlut) {
    r=rlut(::-1); g=glut(::-1); b=blut(::-1);
  } else {
    r=rlut; g=glut; b=blut;
  }

  // itt:
  if (camicaz_itt<=1) { // linear
    ind = span(0.,1.,camicaz_ncolors);
  } else if (camicaz_itt==2) { // sqrt
    ind = sqrt(span(0.,1.,camicaz_ncolors));
  } else if (camicaz_itt==3) { // square
    ind = (span(0.,1.,camicaz_ncolors))^2.;
  } else if (camicaz_itt==4) { // log
    ind = log10(span(10.^(-camicaz_log_itt_dex),1.,camicaz_ncolors)); // 8 dex
    ind -= min(ind);
    ind /= max(ind);
  } else if (camicaz_itt>=5) { // histeq
    ind = span(0.,1.,camicaz_ncolors);
  }
  ind = long(round(ind*(camicaz_ncolors-1)+1));
  r = r(ind); g = g(ind); b = b(ind);

  // and finally, load the palette:
  window,camicaz_wins(1);
  palette,r,g,b;

  camicaz_disp;
}

func camicaz_disp(void)
// pli display, main window
{
  extern camicaz_nim,camicaz_wins,camicaz_data;
  extern camicaz_im,camicaz_imd,camicaz_imdnum,camicaz_cmin,camicaz_cmax,camicaz_name;

  if (camicaz_im == []) return;

  window,camicaz_wins(1);
  fma;

  if (camicaz_itt==5) {
    if (nallof(camicaz_imdnum==[1,camicaz_itt])) \
      camicaz_imd = styc_histeq_scale(camicaz_im);
  } else camicaz_imd = bytscl(camicaz_im,cmin=camicaz_cmin,cmax=camicaz_cmax);
  camicaz_imdnum = [1,camicaz_itt];
  
  pli,camicaz_imd;
  axtit = "pixels";
  
  styc_pltitle,camicaz_name+swrite(format=" %dx%d",dimsof(camicaz_im)(2),dimsof(camicaz_im)(3));
  styc_xytitles,axtit,axtit;
  colorbar,adjust=-0.024,levs=10;
  //refresh zoom now
  camicaz_disp_zoom,once=1;
}


func camicaz_disp_cpc(e,all=)
{
  extern camicaz_cmin,camicaz_cmax;

  if (camicaz_im == []) return;

  if (all) eq_nocopy,subim,camicaz_im(-4:,:5);
  else {
    subim=camicaz_get_subim(x1,x2,y1,y2);
    if (x2 == dimsof(camicaz_im)(2)) x2 = -4;
    if (y1 == 1) y1 = 5;
  }
  
  if (subim==[]) subim = camicaz_im(:-4,5:); // init, not defined
  
  if (e==0) {
    cmin = min(subim);
    cmax = max(subim);
  } else {
    tmp = minmax(camicaz_cpc(subim,0.1,0.999));
    cmin = tmp(1);
    cmax = tmp(2);
  }
  
  camicaz_cmin = cmin;
  camicaz_cmax = cmax;
  
  pyk,swrite(format=cmd_camicaz+"camicaz_set_cmincmax(%f,%f,%f)",float(cmin),float(cmax),float(cmax-cmin)/100.);
}

func camicaz_cpc(im,fmin,fmax)
/* DOCUMENT func cpc(im,fmin,fmax)
   return clipped image at
   from cmin=fraction fmin of pixel intensity
   to   cmax=fraction fmax of pixel intensity
   0 <= fmin < fmax <= 1
   example: pli,cpc(im)
   SEE ALSO:
 */
{
  s = sedgesort(im(*));
  n = numberof(im);
  if (fmin==[]) fmin = 0.10;
  if (fmax==[]) fmax = 0.995;
  if ((fmin<0)||(fmax<0)) error,"fmin and fmax should be > 0";
  if ((fmin>1)||(fmax>1)) error,"fmin and fmax should be < 1";
  if (fmin>fmax) error,"fmin should be < fmax";
  x1=s(long(round(n*fmin)));
  x2=s(long(round(n*fmax)));
  return clip(im,x1,x2);
}

func camicaz_set_cmin(pycmin)
{
  extern camicaz_cmin,camicaz_cmax;
  //  write,format="pycmin=%f, cmin=%f\n",pycmin,cmin;
  // because the precision was cut by the yorick -> python -> yoric
  // transfer, we have to allow for some slack
  if ((camicaz_cmax-camicaz_cmin)!=0) if ((abs(pycmin-camicaz_cmin)/(camicaz_cmax-camicaz_cmin))<1e-3) return;
  if (pycmin>camicaz_cmax) {
    write,"cmin > cmax, ignoring";
    return;
  }
  camicaz_cmin = pycmin;
  camicaz_disp;
}

func camicaz_set_cmax(pycmax)
{
  extern camicaz_cmax,camicaz_cmin;
  //  write,format="pycmax=%f, cmax=%f\n",pycmax,cmax;
  // because the precision was cut by the yorick -> python -> yoric
  // transfer, we have to allow for some slack
  if ((camicaz_cmax-camicaz_cmin)!=0) if ((abs(pycmax-camicaz_cmax)/(camicaz_cmax-camicaz_cmin))<1e-3) return;
  if (pycmax<camicaz_cmin) {
    write,"cmax < cmin, ignoring";
    return;
  }
  camicaz_cmax = pycmax;
  camicaz_disp;
}

func camicaz_get_subim(&x1,&x2,&y1,&y2)
{
  extern camicaz_im;
  
  if (camicaz_nim<1) return;
  curw = current_window();
  window,camicaz_wins(1);
  lim=limits();
  dims = dimsof(camicaz_im);
  x1=long(floor(clip(lim(1),1,dims(2))));
  x2=long(ceil(clip(lim(2),1,dims(2))));
  y1=long(floor(clip(lim(3),1,dims(3))));
  y2=long(ceil(clip(lim(4),1,dims(3))));
  if ( (x1==x2) || (y1==y2) ) {
    //    camicaz_pyk_status_push,"WARNING: (get_subim) Nothing to show";
    //    write,"WARNING: (get_subim) Nothing to show";
    return;
  }
  window,curw;
  return camicaz_im(x1:x2,y1:y2)
}

func camicaz_unzoom
{
  window,camicaz_wins(1);
  unzoom;
  limits;
}


func camicaz_setcuts
{
  extern camicaz_name;
  if (!strmatch(camicaz_name,"Slopes")) camicaz_disp_cpc;
  camicaz_disp;
}

func camicaz_set_server(server)
{
  extern camicaz_server;

  camicaz_server=server;
  //sesame_exec, camicaz_server, "OK_READY";
}

func bash_exec_cb(msg)
{
  extern camicaz_monitor;
  
  status= strtok(msg, "\n");
  while(status(1)) {
    pyk,swrite(format=cmd_camicaz+"pyk_status_push(0,'%s')",status(1));
    status = strtok(status(2), "\n");
  }
  if (strmatch(msg, "READY")) {
    pyk,cmd_camicaz+"glade.get_widget('cam_status').set_markup(\"<span foreground='green' background='white'> CONNECTED </span>\")";
    analyzeMsg, msg;
  } else if (strmatch(msg, "ERROR")) {
    pyk,cmd_camicaz+"glade.get_widget('cam_status').set_markup(\"<span foreground='red' background='white'> NOT CONNECTED </span>\")";
    write,msg;
  }
}

func analyzeMsg(msg)
{
  // parsing msg
  if(strmatch(msg,"tension")){
    tension = strtok(msg, "\n");
    i=0; j=0;
    tab=array(long, 4);
    while(tension(1)) {
      sread, tension(1), format="tension %d : %d", i, j;
      tab(i+1)=j;
      tension = strtok(tension(2), "\n");
    }
    //tab;     
    if (anyof(tab*1.25 > camicaz_tempthresh)) {
      pyk,cmd_camicaz+"glade.get_widget('temp_status').set_markup(\"<span foreground='red' background='white'> "+swrite(format="%.1f / %.1f",tab(3)*1.25,tab(4)*1.25)+" </span>\")";
    } else {
      pyk,cmd_camicaz+"glade.get_widget('temp_status').set_markup(\"<span foreground='green' background='white'> "+swrite(format="%.1f / %.1f",tab(3)*1.25,tab(4)*1.25)+" </span>\")";
    }
  }
}

if (!bash_exec) bash_exec = spawn("/bin/bash",bash_exec_cb);

func sesame_exec(server, msg){
  bash_exec, "SESAME_facteur "+server+" "+msg+"\n";
}
//////////////////////////////////////////////////////////
//              **********************                 //
////////         END OF ROUTINES DEFINITION      ////////
//              **********************                 //
//////////////////////////////////////////////////////////

// start standalone version if called from shell  
arg_camicaz = get_argv();
cmd_camicaz = "camicaz.";

if (1 || anyof(arg_camicaz == "widget_camicaz.i")) {
  cmd_camicaz = "";
  python_camicaz_exec = styctop+"/widgets/widget_camicaz.py";
  pyk_camicaz_cmd=[python_camicaz_exec];
  if (!_pyk_proc) _pyk_proc = spawn(pyk_camicaz_cmd, _pyk_callback);
  write,"widget_camicaz  ready";
  write,"standalone version";
}

camicaz_wins = [36,35];
camicaz_defaultdpi = 75;    // change size of spydr graphic area
camicaz_itt        = 1;     // default ITT [1=lin,2=sqrt,3=square,4=log]
camicaz_ncolors    = 200;
camicaz_lut        = 0;     // default LUT index [0-41]
camicaz_xytitles_adjust = [0.012,0.019]; // X and Y notch axis titles in main area
camicaz_invertlut  = 0;
pldefault,opaque=1,marks=1;
camicaz_nim = 0;
camicaz_log_itt_dex = 3;
camicaz_gui_realized = 0;
camicaz_name = "";
camicaz_slope_autoscale = 0;
camicaz_rad4zoom         = 16;    // default zoom window radius (pixels)

camicaz_freerun = 0;
camicaz_current_ndisp = 0;
camicaz_monitor=0;
camicaz_tempthresh = 150.;

camicaz_server="145.238.175.94";
if(1) {
  camicaz_server="camicaz.ini";
  camicaz_handle=yCamicaz_new(styctop+"/"+camicaz_server);
 }
pyk, cmd_camicaz+"glade.get_widget('camicaz_server').set_text('"+camicaz_server+"')";

//snap_image, 1;
//pyk_debug=1;
