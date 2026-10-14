camtop = get_env("CAMTOP");
if (!camtop)
  error,"CAMTOP is not defined!";

plug_dir, _(camtop,camtop+"/yorick","./","../",plug_dir());
plug_in,"yCamicaz";

extern yCamicaz_new
/* DOCUMENT 
     cam = yCamicaz_new("camicaz.ini");
   SEE ALSO:
 */

extern yCamicaz_get_image
/* DOCUMENT 
     img = yCamicaz_get_image(cam);
   SEE ALSO:
 */

extern yCamicaz_get_next_image
/* DOCUMENT 
     img = yCamicaz_get_next_image(cam);
   SEE ALSO:
 */

extern yCamicaz_get_cube
/* DOCUMENT 
     cube = yCamicaz_get_cube(cam, nbFrames);
   SEE ALSO:
 */

extern yCamicaz_set_chopping
/* DOCUMENT 
     chopping = yCamicaz_set_chopping(cam, chopping);
     yCamicaz_set_chopping, cam, chopping;
   SEE ALSO:
 */

extern yCamicaz_set_wait
/* DOCUMENT 
     wait = yCamicaz_set_wait(cam, wait);
     yCamicaz_set_wait, cam, wait;
   SEE ALSO:
 */

extern yCamicaz_set_expo
/* DOCUMENT 
     expo = yCamicaz_set_expo(cam, expo);
     yCamicaz_set_expo, cam, expo;
   SEE ALSO:
 */

extern yCamicaz_set_latency
/* DOCUMENT 
     latency = yCamicaz_set_latency(cam, latency);
     yCamicaz_set_latency, cam, latency;
   SEE ALSO:
 */

extern yCamicaz_set_filter
/* DOCUMENT 
     res = yCamicaz_set_filter(cam, filter);
     yCamicaz_set_filter, cam, filter;
   SEE ALSO:
 */

extern yCamicaz_save_filter
/* DOCUMENT 
     res = yCamicaz_save_filter(cam, filter);
     yCamicaz_save_filter, cam, filter;
   SEE ALSO:
 */

extern yCamicaz_move_filter
/* DOCUMENT 
     res = yCamicaz_move_filter(cam, nbSteps);
     yCamicaz_move_filter, cam, nbSteps;
   SEE ALSO:
 */

extern yCamicaz_set_param
/* DOCUMENT 
     ret = yCamicaz_set_param(cam, expo, latency, filter);
     yCamicaz_set_param, expo, latency, cam, filter;
   SEE ALSO:
 */

extern yCamicaz_get_monitoring
/* DOCUMENT 
     monitoring = yCamicaz_get_monitoring(cam);
   SEE ALSO:
 */

extern yCamicaz_set_home
/* DOCUMENT 
     res = yCamicaz_set_home(cam);
     yCamicaz_set_home, cam;
   SEE ALSO:
 */

extern yCamicaz_get_freq
/* DOCUMENT 
     freq = yCamicaz_get_freq(cam);
   SEE ALSO:
 */

extern yCamicaz_is_open
/* DOCUMENT
     isOpen = yCamicaz_is_open(cam);
   SEE ALSO:
 */

cam = camicaz_handle
