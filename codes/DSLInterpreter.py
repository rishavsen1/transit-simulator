#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: danielgui
"""
import os
from textx import metamodel_from_file
from bs4 import BeautifulSoup

# initialize model
metamodel = metamodel_from_file("TransitSimulatorDSL.tx")
current_model = metamodel.model_from_file('test.ts')

class Simulation(object):
    def __init__(self):
        self.start_time = 0;
        self.end_time=0;
        self.routeSet = {}
    
    # interpret model
    def interpret(self, model):
        self.start_time = model.timeStart
        self.end_time = model.timeEnd
        for route in model.routeSet:
            vehicles = []
            # build a list of vehicle for each file
            if route.how == "INCLUDE":
                vehicles = ['INCLUDE']
                for vehicle in route.vehicleSet:
                    vehicles.append(vehicle.vehicleid)
            
            elif route.how == 'EXCLUDE':
                vehicles = ['EXCLUDE']
                for vehicle in route.vehicleSet:
                    vehicles.append(vehicle.vehicleid)
            else:
                vehicles = ['ALL']
            self.routeSet[route.routeFileName] = vehicles
    
    # generate route files
    def generateRouteFiles(self):
        count = 0
        for file in self.routeSet:
            infile = open('../SUMO_simulation/' + file, 'r')
            contents = infile.read()
            route = BeautifulSoup(contents, 'xml')
            vehlist = self.routeSet[file]
            # include those vehicle if use INCLUDE option
            if vehlist[0] == 'INCLUDE':
                for vehicle in route.find_all('vehicle'):
                    if not vehicle['id'] in vehlist:
                        vehicle.decompose()
            # exclude those vehicle if use EXCLUDE option
            elif vehlist[0] == 'EXCLUDE':
                for vehicle in route.routes.vehicle:
                    if vehicle['id'] in vehlist:
                        vehicle.decompose()
            # do nothing if include ALL option
            xml = route.prettify('utf-8')
            with open('../SUMO_simulation/DSL_OUTPUT/output_' + str(count) + '.xml', 'wb') as file:
                file.write(xml)
                file.close()
            count += 1
        
    
    def generateConfig(self, export_file):
        self.generateRouteFiles()
        
        # write SUMOCFG file to initialize simulation
        f = open(export_file, "x")
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<configuration xmlns:xsi="http://www.w3.org' +
                '/2001/XMLSchema-instance" xsi:noNamespaceSchema'+ 
                'Location="http://sumo.dlr.de/xsd/sumoConfiguration.xsd">\n')
        f.write('\t<input>\n\t\t<net-file value="Chattanooga_SUMO_Network.net.xml"/>\n')
        f.write('\t\t<route-files value="')
        count = 0
        for key in self.routeSet:
            f.write('output_' + str(count) + '.xml' + ',')
            count = count + 1
        f.write('"/>\n')
        f.write('\t\t<additional-files value="busStopsCARTA.add.xml"/>\n')
        f.write('\t</input>\n')
        f.write('\t<time>\n\t\t<begin value="' + str(self.start_time) + '"/>\n')
        f.write('\t\t<end value="'+  str(self.end_time) + '"/>\n')
        f.write('\t\t<time-to-teleport value="150" />\n\t</time>\n')
        f.write('\t<processing>\n\t\t<ignore-route-errors value="true"/>\n'+
                '\t</processing>\n')
        f.write('\t<output>\n\t\t<netstate-dump value="Trajectory_Output.xml"/>\n')
        f.write('\t</output>\n\t<gui_only>\n\t\t<gui-settings-file value="gui.view.xml"/>\n')
        f.write('\t</gui_only>\n</configuration>')
        f.close()
            

if os.path.exists('../SUMO_simulation/DSL_OUTPUT/test.sumocfg'):
    os.remove("../SUMO_simulation/DSL_OUTPUT/test.sumocfg")
test = Simulation()
test.interpret(current_model)
test.generateConfig('../SUMO_simulation/DSL_OUTPUT/test.sumocfg')
                    
            
            
        