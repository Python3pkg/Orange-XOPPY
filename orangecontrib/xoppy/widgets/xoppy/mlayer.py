import sys, os
import numpy
from PyQt4.QtGui import QIntValidator, QDoubleValidator, QApplication, QSizePolicy
from orangewidget import gui
from orangewidget.settings import Setting
from oasys.widgets import widget

from orangecontrib.xoppy.util.xoppy_util import locations

from orangecontrib.xoppy.util import xoppy_util
from orangecontrib.xoppy.widgets.xoppy.xoppy_xraylib_util import f1f2_calc
from oasys.widgets.exchange import DataExchangeObject


import scipy.constants as codata
import xraylib

class OWmlayer(widget.OWWidget):
    name = "mlayer"
    id = "orange.widgets.datamlayer"
    description = "xoppy application to compute..."
    icon = "icons/xoppy_mlayer.png"
    author = "create_widget.py"
    maintainer_email = "srio@esrf.eu"
    priority = 10
    category = ""
    keywords = ["xoppy", "mlayer"]
    outputs = [{"name": "ExchangeData",
                "type": DataExchangeObject,
                "doc": "send ExchangeData"}]

    #inputs = [{"name": "Name",
    #           "type": type,
    #           "handler": None,
    #           "doc": ""}]

    want_main_area = False

    MODE = Setting(0)
    SCAN = Setting(0)
    F12_FLAG = Setting(0)
    SUBSTRATE = Setting("Si")
    ODD_MATERIAL = Setting("Si")
    EVEN_MATERIAL = Setting("W")
    ENERGY = Setting(8050.0)
    THETA = Setting(0.0)
    SCAN_STEP = Setting(0.009999999776483)
    NPOINTS = Setting(600)
    ODD_THICKNESS = Setting(25.0)
    EVEN_THICKNESS = Setting(25.0)
    NLAYERS = Setting(50)
    FILE = Setting("layers.dat")


    def __init__(self):
        super().__init__()

        box0 = gui.widgetBox(self.controlArea, " ",orientation="horizontal") 
        #widget buttons: compute, set defaults, help
        gui.button(box0, self, "Compute", callback=self.compute)
        gui.button(box0, self, "Defaults", callback=self.defaults)
        gui.button(box0, self, "Help", callback=self.help1)
        self.process_showers()
        box = gui.widgetBox(self.controlArea, " ",orientation="vertical") 
        
        
        idx = -1 
        
        #widget index 0 
        idx += 1 
        box1 = gui.widgetBox(box) 
        gui.comboBox(box1, self, "MODE",
                     label=self.unitLabels()[idx], addSpace=True,
                    items=['Periodic Layers', 'Individual Layers'],
                    valueType=int, orientation="horizontal")
        self.show_at(self.unitFlags()[idx], box1) 
        
        #widget index 1 
        idx += 1 
        box1 = gui.widgetBox(box) 
        gui.comboBox(box1, self, "SCAN",
                     label=self.unitLabels()[idx], addSpace=True,
                    items=['Grazing Angle', 'Photon Energy'],
                    valueType=int, orientation="horizontal")
        self.show_at(self.unitFlags()[idx], box1) 
        
        #widget index 2 
        idx += 1 
        box1 = gui.widgetBox(box) 
        gui.comboBox(box1, self, "F12_FLAG",
                     label=self.unitLabels()[idx], addSpace=True,
                    items=['Create on the fly', 'Use existing file: mlayers.f12'],
                    valueType=int, orientation="horizontal")
        self.show_at(self.unitFlags()[idx], box1) 
        
        #widget index 3 
        idx += 1 
        box1 = gui.widgetBox(box) 
        gui.lineEdit(box1, self, "SUBSTRATE",
                     label=self.unitLabels()[idx], addSpace=True)
        self.show_at(self.unitFlags()[idx], box1) 
        
        #widget index 4 
        idx += 1 
        box1 = gui.widgetBox(box) 
        gui.lineEdit(box1, self, "ODD_MATERIAL",
                     label=self.unitLabels()[idx], addSpace=True)
        self.show_at(self.unitFlags()[idx], box1) 
        
        #widget index 5 
        idx += 1 
        box1 = gui.widgetBox(box) 
        gui.lineEdit(box1, self, "EVEN_MATERIAL",
                     label=self.unitLabels()[idx], addSpace=True)
        self.show_at(self.unitFlags()[idx], box1) 
        
        #widget index 6 
        idx += 1 
        box1 = gui.widgetBox(box) 
        gui.lineEdit(box1, self, "ENERGY",
                     label=self.unitLabels()[idx], addSpace=True,
                    valueType=float, validator=QDoubleValidator())
        self.show_at(self.unitFlags()[idx], box1) 
        
        #widget index 7 
        idx += 1 
        box1 = gui.widgetBox(box) 
        gui.lineEdit(box1, self, "THETA",
                     label=self.unitLabels()[idx], addSpace=True,
                    valueType=float, validator=QDoubleValidator())
        self.show_at(self.unitFlags()[idx], box1) 
        
        #widget index 8 
        idx += 1 
        box1 = gui.widgetBox(box) 
        gui.lineEdit(box1, self, "SCAN_STEP",
                     label=self.unitLabels()[idx], addSpace=True,
                    valueType=float, validator=QDoubleValidator())
        self.show_at(self.unitFlags()[idx], box1) 
        
        #widget index 9 
        idx += 1 
        box1 = gui.widgetBox(box) 
        gui.lineEdit(box1, self, "NPOINTS",
                     label=self.unitLabels()[idx], addSpace=True,
                    valueType=int, validator=QIntValidator())
        self.show_at(self.unitFlags()[idx], box1) 
        
        #widget index 10 
        idx += 1 
        box1 = gui.widgetBox(box) 
        gui.lineEdit(box1, self, "ODD_THICKNESS",
                     label=self.unitLabels()[idx], addSpace=True,
                    valueType=float, validator=QDoubleValidator())
        self.show_at(self.unitFlags()[idx], box1) 
        
        #widget index 11 
        idx += 1 
        box1 = gui.widgetBox(box) 
        gui.lineEdit(box1, self, "EVEN_THICKNESS",
                     label=self.unitLabels()[idx], addSpace=True,
                    valueType=float, validator=QDoubleValidator())
        self.show_at(self.unitFlags()[idx], box1) 
        
        #widget index 12 
        idx += 1 
        box1 = gui.widgetBox(box) 
        gui.lineEdit(box1, self, "NLAYERS",
                     label=self.unitLabels()[idx], addSpace=True,
                    valueType=int, validator=QIntValidator())
        self.show_at(self.unitFlags()[idx], box1) 
        
        #widget index 13 
        idx += 1 
        box1 = gui.widgetBox(box) 
        gui.lineEdit(box1, self, "FILE",
                     label=self.unitLabels()[idx], addSpace=True)
        self.show_at(self.unitFlags()[idx], box1) 

        gui.rubber(self.controlArea)

    def unitLabels(self):
         return ['Layer periodicity: ','Scanning variable: ','Material parameters:','Substrate: ','Odd layer material (closer to vacuum): ','Even layer material (closer to substrate): ','Photon energy [eV]:','Grazing angle [degrees]:','Scanning variable step: ','Number of scanning points','Thickness [A] for odd material:','Thickness [A] for even material:','Number of layer pairs:','File with layer thicknesses:']


    def unitFlags(self):
         return ['True','True','True','self.F12_FLAG  ==  0','self.F12_FLAG  ==  0','self.F12_FLAG  ==  0','True','True','True','True','self.MODE  ==  0  &  self.F12_FLAG  ==  0','self.MODE  ==  0  &  self.F12_FLAG  ==  0','self.MODE  ==  0  &  self.F12_FLAG  ==  0','self.MODE  ==  1']

    def compute(self):

        # copy the variable locally, so no more use of self.
        MODE = self.MODE
        SCAN = self.SCAN
        F12_FLAG = self.F12_FLAG
        SUBSTRATE = self.SUBSTRATE
        ODD_MATERIAL = self.ODD_MATERIAL
        EVEN_MATERIAL = self.EVEN_MATERIAL
        ENERGY = self.ENERGY
        THETA = self.THETA
        SCAN_STEP = self.SCAN_STEP
        NPOINTS = self.NPOINTS
        ODD_THICKNESS = self.ODD_THICKNESS
        EVEN_THICKNESS = self.EVEN_THICKNESS
        NLAYERS = self.NLAYERS
        FILE=self.FILE


        #
        # write input file for Fortran mlayer: mlayer.inp
        #
        f = open('mlayer.inp','w')

        if SCAN == 0 and MODE == 0: a0 = 1
        if SCAN == 1 and MODE == 0: a0 = 5
        if SCAN == 0 and MODE == 1: a0 = 3
        if SCAN == 1 and MODE == 1: a0 = 5

        f.write("%d \n"%a0)
        f.write("N\n")

        f.write("%g\n"%( codata.h * codata.c / codata.e * 1e10 / ENERGY))
        f.write("%g\n"%THETA)

        if SCAN == 0:
            f.write("%g\n"%SCAN_STEP)

        a2 = codata.h * codata.c / codata.e * 1e10 / ENERGY
        a3 = codata.h * codata.c / codata.e * 1e10 / (ENERGY + SCAN_STEP)
        a4 = a3 - a2

        if SCAN != 0:
            f.write("%g\n"%a4)

        f.write("%d\n"%NPOINTS)

        if MODE == 0:
            f.write("%d\n"%NLAYERS)

        if MODE == 0:
            if a0 != 5:
                f.write("%g  %g  \n"%(ODD_THICKNESS,EVEN_THICKNESS))
            else:
                for i in range(NLAYERS):
                    f.write("%g  %g  \n"%(ODD_THICKNESS,EVEN_THICKNESS))

        if MODE != 0:
            f1 = open(FILE,'r')
            a5 = f1.read()
            f1.close()

        if MODE != 0:
            print("Number of layers in %s file is %d "%(FILE,NLAYERS))
            f.write("%d\n"%NLAYERS)
            f.write(a5)

        f.write("mlayer.par\n")
        f.write("mlayer.dat\n")

        f.write("6\n")

        f.close()
        print('File written to disk: mlayer.inp')

        #
        # create f12 file
        #

        if F12_FLAG == 0:
            energy = numpy.arange(0,500)
            elefactor = numpy.log10(10000.0 / 30.0) / 300.0
            energy = 10.0 * 10**(energy * elefactor)

            f12_s = f1f2_calc(SUBSTRATE,energy)
            f12_e = f1f2_calc(EVEN_MATERIAL,energy)
            f12_o = f1f2_calc(ODD_MATERIAL,energy)

            f = open("mlayer.f12",'w')
            f.write('; File created by xoppy for materials [substrate=%s,even=%s,odd=%s]: \n'%(SUBSTRATE,EVEN_MATERIAL,ODD_MATERIAL))
            f.write('; Atomic masses: \n')
            f.write("%g %g %g \n"%(xraylib.AtomicWeight(xraylib.SymbolToAtomicNumber(SUBSTRATE)),
                                   xraylib.AtomicWeight(xraylib.SymbolToAtomicNumber(EVEN_MATERIAL)),
                                   xraylib.AtomicWeight(xraylib.SymbolToAtomicNumber(ODD_MATERIAL)) ))
            f.write('; Densities: \n')
            f.write("%g %g %g \n"%(xraylib.ElementDensity(xraylib.SymbolToAtomicNumber(SUBSTRATE)),
                                   xraylib.ElementDensity(xraylib.SymbolToAtomicNumber(EVEN_MATERIAL)),
                                   xraylib.ElementDensity(xraylib.SymbolToAtomicNumber(ODD_MATERIAL)) ))
            f.write('; Number of energy points: \n')

            f.write("%d\n"%(energy.size))
            f.write('; For each energy point, energy[eV], f1[substrate], f2[substrate], f1[even], f2[even], f1[odd], f2[odd]: \n')
            for i in range(energy.size):
                f.write("%g %g %g %g %g %g %g \n"%(energy[i],f12_s[0,i],f12_s[1,i],f12_e[0,i],f12_e[1,i],f12_o[0,i],f12_o[1,i]))

            f.close()

            print('File written to disk: mlayer.f12')

        #
        # run external program mlayer
        #
        command = os.path.join(locations.home_bin(), 'mlayer') + " < mlayer.inp"
        print("Running command '%s' in directory: %s "%(command, locations.home_bin_run()))
        print("\n--------------------------------------------------------\n")
        os.system(command)
        print("\n--------------------------------------------------------\n")


        #send exchange
        tmp = DataExchangeObject("xoppy_mlayer","mlayer")

        try:
            tmp.add_content("data",numpy.loadtxt("mlayer.dat").T)
            tmp.add_content("plot_x_col",0)
            tmp.add_content("plot_y_col",3)
        except:
            pass
        try:
            tmp.add_content("labels",["Grazing angle Theta [deg]","s-reflectivity","p-reflectivity","averaged reflectivity","s-phase shift","p-phase shift","(s-electric field)^2","(p-electric field)^2"])

        except:
            pass
        try:
            info = "ML %s(%3.2f A):%s(%3.2f A) %d pairs; E=%5.3f eV"%(ODD_MATERIAL,ODD_THICKNESS,EVEN_MATERIAL,EVEN_THICKNESS,NLAYERS,ENERGY)
            tmp.add_content("info",info)
        except:
            pass

        self.send("ExchangeData",tmp)

    def defaults(self):
         self.resetSettings()
         self.compute()
         return

    def help1(self):
        print("help pressed.")
        xoppy_util.xoppy_doc('mlayer')


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = OWmlayer()
    w.show()
    app.exec()
    w.saveSettings()