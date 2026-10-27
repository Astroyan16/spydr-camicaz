#ifndef _POSIX_C_SOURCE
#define _POSIX_C_SOURCE 199309L
#endif
#include <time.h>
#include <yapi.h>

extern "C" {

void Y_yCamicaz_clock(int argc) {
  if (argc != 0 && !(argc == 1 && yarg_nil(0)))
    y_error("yCamicaz_clock takes no arguments");
  struct timespec utc, monotonic;
  if (clock_gettime(CLOCK_REALTIME, &utc) != 0 ||
      clock_gettime(CLOCK_MONOTONIC, &monotonic) != 0)
    y_error("Cannot read UTC/monotonic clocks; recording stopped");
  long dims[2] = {1, 4};
  double *values = ypush_d(dims);
  // Keep seconds and nanoseconds separate to avoid epoch-double rounding.
  values[0] = static_cast<double>(utc.tv_sec);
  values[1] = static_cast<double>(utc.tv_nsec);
  values[2] = static_cast<double>(monotonic.tv_sec);
  values[3] = static_cast<double>(monotonic.tv_nsec);
}

void Y_yCamicaz_clock_resolution(int argc) {
  if (argc != 0 && !(argc == 1 && yarg_nil(0)))
    y_error("yCamicaz_clock_resolution takes no arguments");
  struct timespec utc, monotonic;
  if (clock_getres(CLOCK_REALTIME, &utc) != 0 ||
      clock_getres(CLOCK_MONOTONIC, &monotonic) != 0)
    y_error("Cannot read UTC/monotonic clock resolutions");
  long dims[2] = {1, 2};
  double *values = ypush_d(dims);
  values[0] = utc.tv_sec + utc.tv_nsec * 1.e-9;
  values[1] = monotonic.tv_sec + monotonic.tv_nsec * 1.e-9;
}

}
