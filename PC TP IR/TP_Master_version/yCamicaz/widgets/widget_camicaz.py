#!/usr/bin/env python

import gobject
import gtk
import gtk.glade
import os
import sys
import time
import os, fcntl, errno

styctop = os.environ['STYCTOP']

class widget_camicaz:

   def get_text(self,wdg):     
      self.pyk_resume(self.glade.get_widget(wdg).get_text())

   def get_value(self,wdg):      
      self.pyk_resume(str(self.glade.get_widget(wdg).get_value()))

   def destroy(self, wdg, data=None):
      self.py2yo('camicaz_quit')
      raise SystemExit

   def __init__(self, path=os.path.join(styctop, 'glade'), parent=None,py2yo=None):
      
      self.path=path

      self.gladefile = 'widget_camicaz.glade'

      self.glade = gtk.glade.XML(os.path.join(path,self.gladefile), root='top')
      self.window = self.glade.get_widget('window1')
      self.top = self.glade.get_widget('top')
      # handle destroy event
      if (self.top):
         self.top.connect('destroy', self.destroy)

      self.glade.signal_autoconnect(self)
      
      if parent:
         parent.foreach(parent.remove)
         parent.add(self.top)

      self.glade.get_widget('seq_frame').hide()
      self.glade.get_widget('num_filter').set_active(0)
      self.glade.get_widget('num_expo').set_active(0)
      self.glade.get_widget('num_latency').set_active(0)
      self.glade.get_widget('button_abort').set_sensitive(0)

      # Do not open stdin event if not in standalone mode
      if not py2yo:
         # set stdin non blocking, this will prevent readline to block
         fd = sys.stdin.fileno()
         flags = fcntl.fcntl(fd, fcntl.F_GETFL)
         fcntl.fcntl(fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)
         
         # add stdin to the event loop (yorick input pipe by spawn)
         gobject.io_add_watch(sys.stdin,gobject.IO_IN|gobject.IO_HUP,self.yo2py,None)

   ######################################################
   # THIS IS WHERE YOU PLACE METHODS ASSOCIATED TO GLADE
   # Example of a button
   ######################################################
   def on_send2spydr_clicked(self,wdg):
      ntype = self.glade.get_widget("winselect_camicaz").get_active()
      nim = self.glade.get_widget("winselect_camicaz1").get_active()
      self.py2yo('camicaz_send2spydr %d %d' % (ntype,nim))

   def on_save_camicaz_clicked(self,wdg):
      ntype = self.glade.get_widget("winselect_camicaz").get_active()
      nim = self.glade.get_widget("winselect_camicaz1").get_active()
      nframes = self.glade.get_widget("spin_nframes").get_value()
      filter = self.glade.get_widget("num_filter").get_active()
      texp = self.glade.get_widget("num_expo").get_active()
      self.py2yo('create_camicaz_filename %d %d %d %d %d' % (ntype,nim,nframes,filter,texp))

   def save_camicaz_data(self,file_name):
      tmp_path = os.path.join(styctop, 'glade')
      self.dlg = gtk.glade.XML(os.path.join(tmp_path,self.gladefile), "camicazsave_dialog").get_widget("camicazsave_dialog")
      self.dlg.set_current_folder(os.path.join(styctop, 'data/dump'))
      self.dlg.set_current_name(file_name)
      self.dlg.add_button(gtk.STOCK_CANCEL, 0);
      self.dlg.add_button(gtk.STOCK_OK, 1);
      result = self.dlg.run()
      if (result):
         filename = self.dlg.get_filename()
         ntype = self.glade.get_widget("winselect_camicaz").get_active()
         nim = self.glade.get_widget("winselect_camicaz1").get_active()
         nframes = self.glade.get_widget("spin_nframes").get_value()
         self.py2yo('camicazdata_save "%s" %d %d' % (filename,ntype,nframes))
      self.dlg.hide()

   def on_savebckg_clicked(self,wdg):
      self.py2yo('camicaz_savebckg')

   def on_winselect_camicaz_changed(self,wdg):
      self.py2yo('camicaz_disp_select %d %d' % (self.glade.get_widget("winselect_camicaz").get_active(),self.glade.get_widget("winselect_camicaz1").get_active()))

   def on_drawingarea_camicaz_enter_notify_event(self,wdg,*args):
      self.glade.get_widget('eventbox_cam').grab_focus()
      self.py2yo('camicaz_start_zoom')
#      if (self.doing_zoom==0):
#         self.py2yo('disp_zoom')
#         self.doing_zoom=1

   def on_drawingarea_zoomcam_map(self,wdg,*args):
      drawingarea = self.glade.get_widget('drawingarea_camicaz')
      mwid1 = drawingarea.window.xid;
      drawingarea = self.glade.get_widget('drawingarea_zoomcam')
      mwid2 = drawingarea.window.xid;
      self.py2yo('camicaz_win_init %d %d' % (mwid1,mwid2))

#   def on_camicaz_server_changed(self,wdg,*args):
#      self.py2yo('pyk_set camicaz_server "%s"' % wdg.get_text() )

   def on_setip_clicked(self,wdg,*args):
      self.py2yo('camicaz_set_server "%s"' % self.glade.get_widget('camicaz_server').get_text() )

   def on_apply_param_clicked(self,wdg,*args):
      self.glade.get_widget('apply_param').set_sensitive(0)
      self.glade.get_widget('acquire').set_sensitive(0)
      self.glade.get_widget('button_abort').set_sensitive(0)
      filter = self.glade.get_widget('num_filter').get_active()
      if(filter==1):
         filter = 2
      elif(filter==2):
         filter = 3
      elif(filter==3):
         filter = 1
      expo   = self.glade.get_widget('num_expo').get_active()
      latency  = self.glade.get_widget('num_latency').get_active()
      self.py2yo('apply_param %d %d %d' % (filter,expo,latency))

   def on_acquire_clicked(self,wdg,*args):
      self.glade.get_widget('apply_param').set_sensitive(0)
      self.glade.get_widget('freerun').set_sensitive(0)
      self.glade.get_widget('acquire').set_sensitive(0)
      self.glade.get_widget('button_abort').set_sensitive(1)
      nb_images  = self.glade.get_widget('spin_nframes').get_value_as_int()
      self.py2yo('snap_image %d' % (nb_images))

   def on_button_abort_clicked(self,wdg,*args):
      self.py2yo('pyk_set camicaz_run %d' % 0)

   def on_freerun_toggled(self,wdg):
      active = wdg.get_active();
      self.glade.get_widget('acquire').set_sensitive(1-active)
      self.py2yo('camicaz_start_freerun %d'%active)
      if active:
         self.glade.get_widget('freerun_status').set_from_stock('gtk-media-play',gtk.ICON_SIZE_BUTTON)
      else:
         self.glade.get_widget('freerun_status').set_from_stock('gtk-media-pause',gtk.ICON_SIZE_BUTTON)

   def on_toggle_status_clicked(self,wdg,*args):
     self.py2yo('start_monitoring %d' % (wdg.get_active()))

   def on_follow_toggle_toggled(self,wdg,*args):
      self.py2yo('start_follow %d' % (wdg.get_active()))

   def y_camicaz_text_parm_update(self,name,txt):
      self.glade.get_widget(name).set_text(txt)

   def y_camicaz_set_xyz(self,x,y,z):
      self.glade.get_widget('xvalue').set_text(x)
      self.glade.get_widget('yvalue').set_text(y)
      self.glade.get_widget('zvalue').set_text(z)

   def pyk_status_push(self,id,txt):
      self.glade.get_widget('statusbar').push(id,txt)
      
   def pyk_status_pop(self,id):
      self.glade.get_widget('statusbar').pop(id)
      
   def y_mainctl_set_lut(self,value):
#      if (self.done_init):
      self.glade.get_widget('colors_spin').set_value(value)

   def on_colors_spin_value_changed(self,wdg):
      self.glade.get_widget('invert_check').set_active(0)
      self.py2yo('camicaz_set_lut %d' % self.glade.get_widget('colors_spin').get_value())

   def on_invert_check_toggled(self,wdg):
      self.py2yo('pyk_set camicaz_invertlut %d' % wdg.get_active())
      self.py2yo('camicaz_set_lut')

   def camicaz_set_invertlut(self,value):
#      if (self.done_init):
      self.glade.get_widget('invert_check').set_active(value)

   def camicaz_set_itt(self,value):
#      if (self.done_init):
      self.glade.get_widget('itt').set_active(value)
      
   def on_itt_changed(self,wdg):
      itt = wdg.get_active_text()
      if (itt=="linear"):
         self.py2yo('pyk_set camicaz_itt 1')
      elif (itt=="sqrt"):
         self.py2yo('pyk_set camicaz_itt 2')
      elif (itt=="square"):
         self.py2yo('pyk_set camicaz_itt 3')
      elif (itt=="log"):
         self.py2yo('pyk_set camicaz_itt 4')
      elif (itt=="histeq"):
         self.py2yo('pyk_set camicaz_itt 5')
      self.py2yo('camicaz_set_lut')
      self.py2yo('camicaz_disp')

   def on_cmin_spin_value_changed(self,wdg):
         self.py2yo('camicaz_set_cmin %f' % self.glade.get_widget('cmin_spin').get_value())

   def on_cmax_spin_value_changed(self,wdg):
         self.py2yo('camicaz_set_cmax %f' % self.glade.get_widget('cmax_spin').get_value())

   def camicaz_set_cmincmax(self,cmin,cmax,incr):
      self.glade.get_widget('cmin_spin').set_sensitive(1)
      self.glade.get_widget('cmin_spin').set_value(cmin)
      self.glade.get_widget('cmax_spin').set_value(cmax)
      self.glade.get_widget('cmin_spin').set_increments(incr,incr)
      self.glade.get_widget('cmax_spin').set_increments(incr,incr)

   def on_unzoom_button_clicked(self,wdg):
      self.py2yo('camicaz_unzoom')

   def on_setcuts_button_clicked(self,wdg):
      self.py2yo('camicaz_setcuts')

   def set_cursor_busy(self,state):
      if state:
         self.window.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.WATCH))
      else:
         self.window.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.LEFT_PTR))

   def on_itp_help_activate(self,wdg):
      self.py2yo('camicaz_shortcut_help')

   def on_redisp_activate(self,wdg):
      self.py2yo('camicaz_redisp')

   def on_rezoom_activate(self,wdg):
      self.py2yo('camicaz_disp_zoom')

   def on_open_activate(self,wdg):
      chooser = gtk.FileChooserDialog(title='Open file',action=gtk.FILE_CHOOSER_ACTION_OPEN,buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))
      filter = gtk.FileFilter()
      filter.add_pattern('*.fits')
      filter.set_name('Fits files')
      chooser.add_filter(filter)
      chooser.set_select_multiple(1)
      chooser.set_current_folder(os.path.join(styctop, 'data'))
      res = chooser.run()
      if res == gtk.RESPONSE_OK:
         files=chooser.get_filenames()
         self.currentdir = chooser.get_current_folder()
         fs = ''
         for file in files:
            fs += '\"'+file+'\" '
         self.py2yo('camicaz_openfile %s' % fs)
      chooser.destroy()
         
   def on_saveas_activate(self,wdg):
      chooser = gtk.FileChooserDialog(title='Save as...',action=gtk.FILE_CHOOSER_ACTION_SAVE,buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_SAVE,gtk.RESPONSE_OK))
      filter = gtk.FileFilter()
      filter.add_pattern('*.fits')
      filter.set_name('Fits files')
      chooser.add_filter(filter)
      chooser.set_current_folder(os.path.join(styctop, 'data'))
      chooser.set_current_name('test')
      res = chooser.run()
      if res == gtk.RESPONSE_OK:
         file=chooser.get_filename()
         self.currentsavedir = chooser.get_current_folder()
         self.py2yo('camicaz_saveas \"%s\"' % file)
      chooser.destroy()

   def on_save_activate(self,wdg):
      self.py2yo('camicaz_save')
            
   def on_export_activate(self,wdg):
      chooser = gtk.FileChooserDialog(title='Export Image as png',action=gtk.FILE_CHOOSER_ACTION_SAVE,buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_SAVE,gtk.RESPONSE_OK))
      filter = gtk.FileFilter()
      filter.add_pattern('*.png')
      filter.set_name('PNG files')
      chooser.add_filter(filter)
      chooser.set_current_folder(os.path.join(styctop, 'data'))
      chooser.set_current_name('test.png')
      res = chooser.run()
      if res == gtk.RESPONSE_OK:
         file=chooser.get_filename()
         self.currentsavedir = chooser.get_current_folder()
         self.py2yo('itp_exportpng \"%s\" 1' % file)
      chooser.destroy()

   def on_plugins_toggled(self,wdg):
      self.window = self.glade.get_widget('top').get_parent()

      show_state = self.glade.get_widget('plugins').get_active()

      if (show_state):
         try:
            s = self.size
         except:
            s = 0
         self.size = self.window.get_size()
         self.glade.get_widget('seq_frame').show()
         if (s):
            self.window.resize(s[0],s[1])
      else:
         s = self.size
         self.size = self.window.get_size()
         self.glade.get_widget('seq_frame').hide()
         self.window.resize(s[0],s[1])

   ###################################################
   # END OF GLADE RELATED METHOD DEFINITION
   # minimal wrapper for yorick/python communication
   ###################################################
      
   def yo2py_flush(self):
      sys.stdin.flush()
   
   def py2yo(self,msg):
      # sends string command to yorick's eval
      sys.stdout.write(msg+'\n')
      sys.stdout.flush()
   
   def yo2py(self,cb_condition,*args):
      if cb_condition == gobject.IO_HUP:
         raise SystemExit, "lost pipe to yorick"
      # handles string command from yorick
      # note: individual message needs to end with /n for proper ungarbling
      while 1:
         try:
            msg = sys.stdin.readline()
            msg = "self."+msg
            #  self.py2yo('\"%s\"' % msg)
            try:
               exec(msg)
            except Exception, e:
               exc_type, exc_obj, exc_tb = sys.exc_info()
               sys.stderr.write('yo2py eval: '+str(e)+'\n')
               if exc_type == SyntaxError:
                  raise SystemExit, "lost pipe to yorick"
         except IOError, e:
            if e.errno == errno.EAGAIN:
               # the pipe's empty, good
               break
            # else bomb out
            raise SystemExit, "yo2py unexpected IOError:" + str(e)
         except Exception, ee:
            raise SystemExit, "yo2py unexpected Exception:" + str(ee)
      # carefull with the ident here
      return True

####################################
# CODE FOR STANDALONE MODE
####################################
if __name__ == "__main__":
   #print 'standalone demo'
   demo=gtk.Window(type=gtk.WINDOW_TOPLEVEL)
   demo.connect('destroy', gtk.main_quit)
   demo.show()
   w = widget_camicaz(parent=demo)
   gtk.main()
