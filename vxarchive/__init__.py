import sys
import zipack
sys.modules['vxarchive'] = zipack
sys.modules['vxarchive.core'] = zipack.core
sys.modules['vxarchive.gui'] = zipack.gui
