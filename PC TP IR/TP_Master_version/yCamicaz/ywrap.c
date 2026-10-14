/* codger-generated yorick package wrapper file */
#include "play.h"
#include "ydata.h"

/*----------------begin yorick/yCamicaz.i */
extern BuiltIn Y_yCamicaz_new;
extern BuiltIn Y_yCamicaz_get_image;
extern BuiltIn Y_yCamicaz_get_next_image;
extern BuiltIn Y_yCamicaz_get_cube;
extern BuiltIn Y_yCamicaz_set_chopping;
extern BuiltIn Y_yCamicaz_set_wait;
extern BuiltIn Y_yCamicaz_set_expo;
extern BuiltIn Y_yCamicaz_set_latency;
extern BuiltIn Y_yCamicaz_set_filter;
extern BuiltIn Y_yCamicaz_save_filter;
extern BuiltIn Y_yCamicaz_move_filter;
extern BuiltIn Y_yCamicaz_set_param;
extern BuiltIn Y_yCamicaz_get_monitoring;
extern BuiltIn Y_yCamicaz_set_home;
extern BuiltIn Y_yCamicaz_get_freq;

/*----------------list include files */

static char *y0_includes[] = {
  "yorick/yCamicaz.i",
  0,
  0
};

/*----------------collect pointers and names */

static BuiltIn *y0_routines[] = {
  &Y_yCamicaz_new,
  &Y_yCamicaz_get_image,
  &Y_yCamicaz_get_next_image,
  &Y_yCamicaz_get_cube,
  &Y_yCamicaz_set_chopping,
  &Y_yCamicaz_set_wait,
  &Y_yCamicaz_set_expo,
  &Y_yCamicaz_set_latency,
  &Y_yCamicaz_set_filter,
  &Y_yCamicaz_save_filter,
  &Y_yCamicaz_move_filter,
  &Y_yCamicaz_set_param,
  &Y_yCamicaz_get_monitoring,
  &Y_yCamicaz_set_home,
  &Y_yCamicaz_get_freq,
  0
};

static void *y0_values[] = {
  0
};

static char *y0_names[] = {
  "yCamicaz_new",
  "yCamicaz_get_image",
  "yCamicaz_get_next_image",
  "yCamicaz_get_cube",
  "yCamicaz_set_chopping",
  "yCamicaz_set_wait",
  "yCamicaz_set_expo",
  "yCamicaz_set_latency",
  "yCamicaz_set_filter",
  "yCamicaz_save_filter",
  "yCamicaz_move_filter",
  "yCamicaz_set_param",
  "yCamicaz_get_monitoring",
  "yCamicaz_set_home",
  "yCamicaz_get_freq",
  0
};

/*----------------define package initialization function */

PLUG_EXPORT char *yk_yCamicaz(char ***,
                         BuiltIn ***, void ***, char ***);
static char *y0_pkgname = "yCamicaz";

char *
yk_yCamicaz(char ***ifiles,
       BuiltIn ***code, void ***data, char ***varname)
{
  *ifiles = y0_includes;
  *code = y0_routines;
  *data = y0_values;
  *varname = y0_names;
  return y0_pkgname;
}
