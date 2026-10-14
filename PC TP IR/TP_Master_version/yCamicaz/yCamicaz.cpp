#include <yapi.h>
#include <string>
#include <sstream>
#include <iomanip>
#include <camicaz.h>

using namespace std;

extern "C" {

typedef struct camicaz_struct {
  /**
   * @typedef Yorick API context structure
   */
  void *camera;
} camicaz_struct;

void yCamicaz_free(void *obj) {
  camicaz_struct *handler = (camicaz_struct *) obj;
  try {
    Camicaz *camicaz_handler = (Camicaz *) (handler->camera);
    delete camicaz_handler;
  } catch (string &msg) {
    y_error(msg.c_str());
  } catch (char const * msg) {
    y_error(msg);
  }
}

void yCamicaz_print(void *obj)
/** @brief context_struct printer.
 *  @param[in] obj : context_struct to print
 */
{
  //    context_struct *handler = (context_struct *)obj;
  //    yoga_context *context_handler = (yoga_context *)(handler->yoga_context);
  //    unsigned int activeDevice = context_handler->get_activeDevice();
  //    unsigned int nDevice = context_handler->get_ndevice();
  //    cout << "YoGA Context : " << endl;
  //    cout << nDevice << " CUDA device(s)" << endl;
  //    cout << "Dev Id" << " | " << "multiproc" << " | " << "cores" << " | "
  //	 << "compute" << " | " << "Perf (GFlops)" << endl;
  //    for (size_t idx = 0; idx < nDevice; idx++) {
  //      cout << ((idx==activeDevice)?"<U>":"   ") << setw(3) << idx << " | "
  //	   << setw(9) << context_handler->get_device(idx)->get_properties().multiProcessorCount
  //	   << " | "
  //	   << setw(5) << context_handler->get_device(idx)->get_sm_per_multiproc() *
  //	context_handler->get_device(idx)->get_properties().multiProcessorCount
  //	   << " | "
  //	   << setw(5) << context_handler->get_device(idx)->get_properties().major
  //	   << "."
  //	   << context_handler->get_device(idx)->get_properties().minor
  //	   << " | "
  //	   << context_handler->get_device(idx)->get_compute_perf()/1.e6
  //	   << endl;
  //    }
}

string y_CamicazName("yCamicaz Object");
static y_userobj_t yCamicaz =
    {
    /**
     * @typedef Yorick API yCamicaz userobj
     */
    const_cast<char*>(y_CamicazName.c_str()), &yCamicaz_free, &yCamicaz_print, 0, 0, 0 };

void Y_yCamicaz_new(int argc)
/** @brief camicaz creator.
 *  @param[in] argc : command line argument (current context expected)
 */
{
  try {
    //long int *ntot=0, *dims=0;
    char *configFile = ygets_q(argc - 1);
    camicaz_struct *handle = (camicaz_struct *) ypush_obj(&yCamicaz,
        sizeof(camicaz_struct));
    handle->camera = new Camicaz(configFile);
  } catch (string &msg) {
    y_error(msg.c_str());
  } catch (char const * msg) {
    y_error(msg);
  } catch (...) {
    stringstream buf;
    buf << "unknown error with yCamicaz construction in " << __FILE__ << "@"
        << __LINE__ << endl;
    y_error(buf.str().c_str());
  }
}

void Y_yCamicaz_get_image(int argc) {
  camicaz_struct *handle = (camicaz_struct *) yget_obj(argc - 1, &yCamicaz);
  Camicaz *camera = (Camicaz *) (handle->camera);
  const long int nbDims = camera->getNbDims() + 1;
  long int *camDims = camera->getDims();
  long int dims[nbDims];
  dims[0] = camera->getNbDims();
  for (int i = 1; i < nbDims; i++)
    dims[i] = camDims[i - 1];

  //short *data = (short *)ypush_s(dims);
  //int *data = (int *)ypush_i(dims);
  long *data = (long *) ypush_l(dims);

  camera->getLastImage(data);
}

void Y_yCamicaz_get_next_image(int argc) {
  camicaz_struct *handle = (camicaz_struct *) yget_obj(argc - 1, &yCamicaz);
  Camicaz *camera = (Camicaz *) (handle->camera);
  const long int nbDims = camera->getNbDims() + 1;
  long int *camDims = camera->getDims();
  long int dims[nbDims];
  dims[0] = camera->getNbDims();
  for (int i = 1; i < nbDims; i++)
    dims[i] = camDims[i - 1];

  //short *data = (short *)ypush_s(dims);
  //int *data = (int *)ypush_i(dims);
  long *data = (long *) ypush_l(dims);

  camera->getNextImage(data);
}

void Y_yCamicaz_get_cube(int argc) {
  camicaz_struct *handle = (camicaz_struct *) yget_obj(argc - 1, &yCamicaz);
  long int nbFrames = ygets_l(argc - 2);

  Camicaz *camera = (Camicaz *) (handle->camera);
  const long int nbDims = camera->getNbDims() + 2;
  long int *camDims = camera->getDims();
  long int dims[nbDims];
  dims[0] = camera->getNbDims() + 1;
  for (int i = 1; i < nbDims - 1; i++)
    dims[i] = camDims[i - 1];
  dims[nbDims - 1] = nbFrames;

  long *data = (long *) ypush_l(dims);

  for (int i = 0; i < nbFrames; i++)
    camera->getLastImage((long *) (data + i * camera->getSize()));

}

void Y_yCamicaz_set_expo(int argc) {
  camicaz_struct *handle = (camicaz_struct *) yget_obj(argc - 1, &yCamicaz);
  long int expo = ygets_l(argc - 2);

  Camicaz *camera = (Camicaz *) (handle->camera);
  int ret = camera->setExpo(expo);
  ypush_int(ret);
}

void Y_yCamicaz_set_chopping(int argc) {
  camicaz_struct *handle = (camicaz_struct *) yget_obj(argc - 1, &yCamicaz);
  long int chopping = ygets_l(argc - 2);

  Camicaz *camera = (Camicaz *) (handle->camera);
  int ret = camera->setChopping(chopping);
  ypush_int(ret);
}

void Y_yCamicaz_set_wait(int argc) {
  camicaz_struct *handle = (camicaz_struct *) yget_obj(argc - 1, &yCamicaz);
  long int wait = ygets_l(argc - 2);

  Camicaz *camera = (Camicaz *) (handle->camera);
  int ret = camera->setWaitFrame(wait);
  ypush_int(ret);
}

void Y_yCamicaz_set_latency(int argc) {
  camicaz_struct *handle = (camicaz_struct *) yget_obj(argc - 1, &yCamicaz);
  long int latency = ygets_l(argc - 2);

  Camicaz *camera = (Camicaz *) (handle->camera);
  int ret = camera->setLatency(latency);
  ypush_int(ret);
}

void Y_yCamicaz_set_filter(int argc) {
  camicaz_struct *handle = (camicaz_struct *) yget_obj(argc - 1, &yCamicaz);
  long int filter = ygets_l(argc - 2);

  Camicaz *camera = (Camicaz *) (handle->camera);
  int ret = camera->setFilter(filter);
  ypush_int(ret);
}

void Y_yCamicaz_save_filter(int argc) {
  camicaz_struct *handle = (camicaz_struct *) yget_obj(argc - 1, &yCamicaz);
  Camicaz *camera = (Camicaz *) (handle->camera);
  long int filter = ygets_l(argc - 2);
  int ret = camera->saveFilter(filter);
  ypush_int(ret);
}

void Y_yCamicaz_move_filter(int argc) {
  camicaz_struct *handle = (camicaz_struct *) yget_obj(argc - 1, &yCamicaz);
  Camicaz *camera = (Camicaz *) (handle->camera);
  long int nbSteps = ygets_l(argc - 2);
  int ret = camera->moveMotor(nbSteps);
  ypush_int(ret);
}

void Y_yCamicaz_set_param(int argc) {
  camicaz_struct *handle = (camicaz_struct *) yget_obj(argc - 1, &yCamicaz);
  long int expo = ygets_l(argc - 2);
  long int latency = ygets_l(argc - 3);
  long int filter = ygets_l(argc - 4);

  Camicaz *camera = (Camicaz *) (handle->camera);
  int ret = camera->setParam(expo, latency, filter);
  ypush_long(ret);
}

void Y_yCamicaz_get_monitoring(int argc) {
  camicaz_struct *handle = (camicaz_struct *) yget_obj(argc - 1, &yCamicaz);
  Camicaz *camera = (Camicaz *) (handle->camera);
  int size = camera->getMonitoringSize();
  long int dims[2] = {1,size};
  int *toto = ypush_i(dims);
  int ret = camera->getMonitoring(toto,size);
  //ypush_int(ret);
}

void Y_yCamicaz_set_home(int argc) {
  camicaz_struct *handle = (camicaz_struct *) yget_obj(argc - 1, &yCamicaz);
  Camicaz *camera = (Camicaz *) (handle->camera);
  int ret = camera->setHome();
  ypush_int(ret);
}

void Y_yCamicaz_get_freq(int argc) {
  camicaz_struct *handle = (camicaz_struct *) yget_obj(argc - 1, &yCamicaz);
  Camicaz *camera = (Camicaz *) (handle->camera);
  double ret = camera->getFreq();
  ypush_double(ret);
}

void Y_yCamicaz_is_open(int argc) {
  camicaz_struct *handle = (camicaz_struct *) yget_obj(argc - 1, &yCamicaz);
  Camicaz *camera = (Camicaz *) (handle->camera);
  ypush_int(camera->isOpen() ? 1 : 0);
}
}
