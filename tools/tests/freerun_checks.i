// Loaded after functions extracted verbatim from the production sources.
func check(ok, message) { if (!ok) error,message; }
func checkpoint(label) {
  write,label;
  ack=open(get_env("SPYDR_TEST_ACK"));
  rdline,ack;
  close,ack;
}
func spydr_get_available_windows(void) {}
func gui_update(void) {}
func disp_zoom(once=) {}
func plot_histo(void) {}
func spydr_pltitle(title) {}
func spydr_xytitles(x,y) {}
func spydr_pyk(message) { extern gui_message; gui_message=message; }
func spydr_pyk_status_push(message) { extern status; status=message; write,message; }
func get_subim(x1,x2,y1,y2) { return spydr_im; }
func disp_cpc(e,allim,all=) {
  extern cmin,cmax;
  cmin=0; cmax=255;
}
func colorbar(adjust=,levs=) {
  extern probe_render;
  if (fail_render) error,"injected render failure";
  // Force the partial drawing to its target before sampling the visible window.
  if (probe_render) {
    probe_render=0;
    redraw;
    checkpoint,"PROBE_PENDING";
  }
}

// Keep real after() available for the timer cancellation regression.
real_after=after;
func test_after(delay,callback,arg) {
  extern pending,max_pending;
  if (structof(delay)==[]) pending=0;
  else { pending++; max_pending=max(max_pending,pending); }
}
after=test_after;
func cam_is_open(handle) { return camera_open; }
func cam_get_image(handle) {
  extern acquisitions,camera_open;
  acquisitions++;
  if (fail_acquire) error,"injected acquisition failure";
  if (fail_after_read) camera_open=0;
  return -array(acquisitions%200,256,256,2);
}
func cam_chopping(handle,state) { extern chop_states; grow,chop_states,state; }

spydr_wins=[0,1,2];
spydr_defaultdpi=spydr_dpi=80;
spydr_wavelength=1.; spydr_pixsize=1.;
spydr_showlower=spydr_showplugins=0;
spydr_plot_in_arcsec=0; spydr_itt=1;
python_exec=path2glade="unused";
_spydr_pyk_proc=1; gui_realized=0;
spydr_append=0; spydr_nim=0; imnum=[];
spydr_disp=disp_tv;
cam_freerun=0; cam_current_ndisp=0; cam_current_bckg=0;
cam_recording=0;
cam_buffer_content=[];
cam_handle=0; cmd_cam="";
camera_open=1; fail_acquire=fail_after_read=fail_render=probe_render=0;
acquisitions=pending=max_pending=0;
chop_states=[];
window,0,width=400,height=400,style="nobox.gs",wait=1;
palette,"gray.gp";
limits,0,256,0,256;

// An unsaved recording must not be overwritten by a fresh live acquisition.
cam_recording=1;
cam_start_freerun,1,0;
check,!cam_freerun && acquisitions==0 && pending==0,"freerun overwrote unsaved recording";
cam_recording=0;

// Append must remain functional for ordinary images, but never for live images.
spydr,array(20,256,256);
spydr,array(30,256,256),append=1;
check,spydr_nim==2,"ordinary append regressed";
spydr_append=1;
cam_start_freerun,1,0;
check,allof(cam_buffer_content==["Diff","End","Start"]),"first start missed camera selection";
check,spydr_nim==1 && numberof(spydrs)==1,"live appended images";
check,pending==1,"missing next frame";
before=acquisitions;
cam_start_freerun,1,0;
check,acquisitions==before && pending==1,"duplicate start acquired/queued";
cam_stop_freerun;
check,pending==0 && !cam_freerun,"stop left a pending callback";
freerun_loop;
check,acquisitions==before,"stopped callback acquired";

// Changing chopping during live acquisition must not restart or queue frames.
cam_start_freerun,1,0;
before=acquisitions;
cam_set_freerun_chopping,1;
check,acquisitions==before && pending==1 && numberof(chop_states)==0,
  "enabling chopping acquired, queued or moved hardware immediately";
freerun_loop;
check,numberof(chop_states)==1 && chop_states(1)==1,
  "live enable did not chop on the next frame";
cam_set_freerun_chopping,1;
freerun_loop;
check,numberof(chop_states)==2 && chop_states(2)==0,
  "repeated enable reset chopping phase";
before=acquisitions;
cam_set_freerun_chopping,0;
check,acquisitions==before && pending==1,"disabling chopping restarted acquisition";
freerun_loop;
check,numberof(chop_states)==2 && cam_freechop==-1,
  "live disable did not stop chopping";
cam_set_freerun_chopping,1;
freerun_loop;
check,numberof(chop_states)==3 && chop_states(3)==1,
  "live re-enable did not resume chopping";
cam_stop_freerun;
before=cam_freechop;
cam_set_freerun_chopping,0;
check,cam_freechop==before && pending==0,"stopped toggle affected acquisition";
cam_start_freerun,1,0;
check,cam_freechop==-1 && numberof(chop_states)==3,"restart ignored disabled checkbox";
cam_stop_freerun;
cam_start_freerun,1,1;
check,numberof(chop_states)==4 && chop_states(4)==1,"restart ignored enabled checkbox";
cam_stop_freerun;
check,max_pending==1,"chopping changes duplicated callbacks";
write,"PASS live chopping enable/disable without restart";

// Start/End/Diff and background subtraction, without asynchronous GUI replies.
cam_freerun=1;
cam_buffer=array(10,256,256,2); cam_buffer(,,2)=40;
cam_bckg_buffer=array(2,256,256,2); cam_bckg_buffer(,,2)=7;
for (j=0;j<3;j++) {
  expected=[25,33,8];
  cam_disp_select,j,1,live=1;
  check,allof(spydr_im==expected(j+1)),"wrong background/plane";
}
before=spydr_im;
cam_disp_select,1,0;
check,allof(spydr_im==before) && cam_current_ndisp==1,"UI drew outside loop";
cam_disp_select,-1,0;
check,cam_current_ndisp==1,"empty combo corrupted selection";
cam_stop_freerun;

// A completed 200-cycle ABBA sequence leaves an 800-exposure camera cube.
// Model the stale vertical crop reported when returning from cube browsing.
window,spydr_wins(1);
limits,0,256,0,256,square=1;
full_frame_limits=limits();
cam_buffer=array(char(10),256,256,2,4*200);
limits,0,256,64,192,square=1;
cam_start_freerun,1,0;
window,spydr_wins(1);
check,max(abs(limits()(1:4)-full_frame_limits(1:4)))<1.e-6,
  "cube-to-freerun retained the sequence vertical crop";
cam_stop_freerun;

// Ordinary live restarts must still preserve a deliberate user zoom.
limits,40,140,50,150,square=1;
user_zoom=limits();
cam_start_freerun,1,0;
window,spydr_wins(1);
check,allof(limits()==user_zoom),"ordinary freerun restart lost user zoom";
cam_stop_freerun;
write,"PASS ABBA cube-to-live framing and ordinary restart zoom";

// A partial draw must leave the previous visible frame unchanged.
spydr_append=0;
cam_current_ndisp=2; cam_current_bckg=0;
cam_freerun=1;
spydr,array(30,256,256),replace=1;
checkpoint,"PROBE_BASE";
probe_render=1;
spydr,array(210,256,256),replace=1;
probe_render=0;
checkpoint,"PROBE_DONE";
cam_stop_freerun;
redraw;
checkpoint,"PROBE_REDRAW";

// Failure paths must stop scheduling and release the temporary pixmap.
fail_acquire=1; cam_start_freerun,1,0;
check,!cam_freerun && pending==0,"acquisition failure did not stop";
fail_acquire=0; fail_after_read=1; cam_start_freerun,1,0;
check,!cam_freerun && pending==0,"closed camera did not stop";
fail_after_read=0; camera_open=1;
fail_render=1; cam_start_freerun,1,0;
check,!cam_freerun && pending==0,"render failure did not stop";
fail_render=0;
cam_start_freerun,1,1;
check,cam_freerun && pending==1,"restart after failure failed";
cam_stop_freerun;

// Exercise actual after() cancellation, not only the scheduler test double.
after=real_after;
real_after,60,freerun_loop;
real_after,60,freerun_loop;
cam_stop_freerun;
after=test_after;

// Long run with real Gist rendering and the real Spydr image-stack replacement.
xid1=0;
window,0;
limits,40,140,50,150,square=1;
saved_limits=limits();
palette,query=1,saved_r,saved_g,saved_b;
for (j=1;j<=100;j++) {
  spydr_resize_main,80+20*(j%3),-2,-2;
  check,gui_message=="camera_resize_done(1)","resize failed";
  check,allof(limits()==saved_limits),"resize lost zoom limits";
  palette,query=1,r,g,b;
  check,allof(r==saved_r) && allof(g==saved_g) && allof(b==saved_b),"resize lost palette";
}
write,"PASS 100 graph recreations with preserved zoom and palette";
spydr_append=1;
cam_start_freerun,1,0;
for (j=1;j<=3000;j++) {
  freerun_loop;
  check,spydr_nim==1 && numberof(spydrs)==1,"image stack grew";
  check,numberof(cam_buffer)==256*256*2,"camera cube grew";
  check,pending==1 && max_pending==1,"callback queue grew";
  if (j%500==0) {
    checkpoint,swrite(format="MEMORY %d",j);
  }
}
cam_stop_freerun;
for (j=1;j<=100;j++) { cam_start_freerun,1,0; cam_stop_freerun; }
check,pending==0,"restart cycles left callbacks";
write,"PASS freerun: rendering, image replacement, selections, errors, restarts";
quit;
