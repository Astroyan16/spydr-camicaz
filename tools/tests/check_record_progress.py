"""Check GTK2 Record completion text, colours, and reset using widget doubles."""
from pathlib import Path
from types import SimpleNamespace
import textwrap
import unittest

SOURCE=Path(__file__).resolve().parents[2]/'PC TP IR/TP_Master_version/yCamicaz/yorick/spydr/spydr.py'

class Bar:
    def __init__(self):self.colours={}
    def modify_bg(self,state,colour):self.colours[state]=colour
    def set_fraction(self,value):self.fraction=value
    def set_text(self,value):self.text=value
    def set_tooltip_text(self,value):self.tooltip=value

class ProgressTests(unittest.TestCase):
    def setUp(self):
        text=SOURCE.read_text()
        start=text.index('   def record_progress_state(')
        end=text.index('\n   def ',start+1)
        ns={'gtk':SimpleNamespace(STATE_PRELIGHT=2,STATE_SELECTED=3,
                                 gdk=SimpleNamespace(color_parse=lambda c:c))}
        exec(textwrap.dedent(text[start:end]),ns)
        self.bar=Bar()
        self.gui=SimpleNamespace(glade=SimpleNamespace(get_widget=lambda name:self.bar))
        self.render=lambda state,saved,total:ns['record_progress_state'](self.gui,state,saved,total)
    def test_success_and_next_record_reset(self):
        self.render(2,2,2)
        self.assertEqual(self.bar.text,'Record successful - 2/2 saved')
        self.assertEqual(self.bar.fraction,1.)
        self.assertEqual(self.bar.colours,{2:'#36834A',3:'#36834A'})
        self.render(0,0,0)
        self.assertEqual(self.bar.colours,{2:None,3:None})
        self.assertEqual(self.bar.fraction,0.)
        self.assertEqual(self.bar.text,'Preparing record...')
    def test_saving_is_not_green(self):
        self.render(2,2,2)
        self.render(1,2,2)
        self.assertEqual(self.bar.text,'Saving FITS...')
        self.assertTrue(all(c is None for c in self.bar.colours.values()))
    def test_partial_and_disk_failure(self):
        self.render(3,1,3)
        self.assertEqual(self.bar.text,'Record interrupted - 1/3 saved')
        self.assertAlmostEqual(self.bar.fraction,1./3.)
        self.assertEqual(self.bar.colours[2],'#B57918')
        self.render(4,3,3)
        self.assertEqual(self.bar.text,'Save failed - data retained')
        self.assertEqual(self.bar.colours[2],'#B53636')
    def test_no_frames_and_fraction_bounds(self):
        self.render(5,0,0)
        self.assertEqual(self.bar.text,'Record failed - no images saved')
        self.render(6,0,0)
        self.assertEqual(self.bar.text,'Record stopped - no images saved')
        self.render(1,5,3)
        self.assertEqual(self.bar.fraction,1.)
        self.assertEqual(self.bar.tooltip,self.bar.text)

if __name__=='__main__':unittest.main()
