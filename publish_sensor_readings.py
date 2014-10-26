#!/usr/bin/env python
#
# Copyright (c) 2014, InviNets sp. z.o.o.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS ORIMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
# OF THE POSSIBILITY OF SUCH DAMAGE.
#
# Author: Przemyslaw Horban (p.horban@invinets.com)
#         Konrad Iwanicki (k.iwanicki@invinets.com)
#

import re
import threading
import time
import socket
import argparse

import pysnmp
from pysnmp.entity import engine, config
from pysnmp.smi import error
from pysnmp.carrier.asynsock.dgram import udp
from pysnmp.entity.rfc3413 import cmdrsp, context


STALE_AFTER_SEC = 120


class SensorModel(object):
    def __init__(self, assetTag):
        self.assetTag = assetTag
        self.lastReadTime = 0
        self.lock = threading.Lock()

    def newReading(self, temp, humid, batVolt):
        with self.lock:
            self.temp = temp
            self.humid = humid
            self.batVolt = batVolt
            self.lastReadTime = time.time()

    def _getValue(self, name):
        with self.lock:
            if time.time() - self.lastReadTime > STALE_AFTER_SEC:
                return None
            else:
                return getattr(self, name, None)

    def getName(self):
        with self.lock:
            return self.assetTag

    def getTemp(self):
        return self._getValue('temp')

    def getHumid(self):
        return self._getValue('humid')

    def getBatVolt(self):
        return self._getValue('batVolt')


class SNMPAgentForSensors(object):
    def __init__(self, udpIp, udpPort):
        # Create SNMP engine with autogenernated engineID and pre-bound
        # to socket transport dispatcher
        self.snmpEngine = engine.SnmpEngine()
        self.mibBuilder = self.snmpEngine.msgAndPduDsp.mibInstrumController.mibBuilder

        mibPath = self.mibBuilder.getMibPath() + ('.',)
        self.mibBuilder.setMibPath(*mibPath)

        # Setup UDP over IPv4 transport endpoint
        config.addSocketTransport(
            self.snmpEngine,
            udp.domainName,
            udp.UdpSocketTransport().openServerMode((udpIp, udpPort))
        )

        print 'Publishing readings via SNMP'
        print 'Agent address {}:{}'.format(udpIp, udpPort)
        print 'Community name public'

        # v1/2 setup
        config.addV1System(self.snmpEngine, 'test-agent', 'public')

        # v3 setup
        config.addV3User(
            self.snmpEngine, 'test-user'
        )

        # VACM setup
        config.addContext(self.snmpEngine, '')
        config.addRwUser(self.snmpEngine, 1, 'test-agent', 'noAuthNoPriv', (1,3,6)) # v1
        config.addRwUser(self.snmpEngine, 2, 'test-agent', 'noAuthNoPriv', (1,3,6)) # v2c
        config.addRwUser(self.snmpEngine, 3, 'test-user', 'noAuthNoPriv', (1,3,6)) # v3

        # SNMP context
        snmpContext = context.SnmpContext(self.snmpEngine)

        # Apps registration
        cmdrsp.GetCommandResponder(self.snmpEngine, snmpContext)
        cmdrsp.SetCommandResponder(self.snmpEngine, snmpContext)
        cmdrsp.NextCommandResponder(self.snmpEngine, snmpContext)
        cmdrsp.BulkCommandResponder(self.snmpEngine, snmpContext)

        MibScalarInstance, = self.mibBuilder.importSymbols('SNMPv2-SMI', 'MibScalarInstance')

        class ScalarFromCallback(MibScalarInstance):
            def __init__(self, sensorId, valueGetter, typeName, instId, syntax):
                MibScalarInstance.__init__(self, typeName, instId, syntax)
                self.valueGetter = valueGetter

            def readTest(self, name, val, idx, (acFun, acCtx)):
                if not self.valueGetter():
                    raise error.NoAccessError(idx=idx, name=name)

            def readGet(self, name, val, idx, (acFun, acCtx)):
                value = self.valueGetter()
                if not value:
                    raise error.NoAccessError(idx=idx, name=name)
                else:
                    return name, self.syntax.clone(value)

        self.ScalarFromCallback = ScalarFromCallback
        self.nextSensorId = 1

    def publishSensor(self, sensorModel):
        sensorId = self.nextSensorId
        self.nextSensorId += 1

        PUBLISHED_SCALARS = {
            'lmTempSensorsIndex': lambda: sensorId,
            'lmTempSensorsValue': sensorModel.getTemp,
            'lmTempSensorsDevice': sensorModel.getName,

            'lmMiscSensorsIndex': lambda: sensorId,
            'lmMiscSensorsValue': sensorModel.getHumid,
            'lmMiscSensorsDevice': sensorModel.getName,

            'lmVoltSensorsIndex': lambda: sensorId,
            'lmVoltSensorsValue': sensorModel.getBatVolt,
            'lmVoltSensorsDevice': sensorModel.getName,
        }

        for scalarName, valueGetter in PUBLISHED_SCALARS.iteritems():
            symbol, = self.mibBuilder.importSymbols('LM-SENSORS-MIB', scalarName)

            self.mibBuilder.exportSymbols('LM-SENSORS-MIB',
                                          self.ScalarFromCallback(
                                              sensorId,
                                              valueGetter,
                                              symbol.name,
                                              (sensorId,),
                                              symbol.getSyntax().clone(None)))

    def startPublishLoop(self):
        try:
            self.snmpEngine.transportDispatcher.jobStarted(1)
            while True:  # Just wait for a signal.
                self.snmpEngine.transportDispatcher.runDispatcher(timeout=1.0)
        finally:
            self.snmpEngine.transportDispatcher.jobFinished(1)


class SensorSet(object):
    def __init__(self, euiToTagFile):
        self.sensorsByEui = {}

        for line in euiToTagFile:
            parts = line.split(',')
            parts = [s.strip() for s in parts]
            if len(parts) == 2:
                eui, tag = parts
                if eui not in self.sensorsByEui:
                    self.sensorsByEui[eui] = SensorModel(tag)

    def getAll(self):
        return self.sensorsByEui.values()

    def getSensorByEUI(self, eui):
        return self.sensorsByEui.get(eui, None)


class UDPReadingsReceiver(object):
    def __init__(self, sensorSet, udpIp, udpPort):
        self.lock = threading.Lock()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((udpIp, udpPort))
        print 'Waiting for packets from sensors at address {}:{}'.format(udpIp, udpPort)
        self.thread = threading.Thread(target=self._thread)
        self.keepRunning = False
        self.sensorSet = sensorSet

    def startAsyncListening(self):
        with self.lock:
            if not self.keepRunning:
                self.keepRunning = True
                self.thread.start()

    def stopListening(self):
        self.lock.acquire()
        if self.keepRunning:
            self.keepRunning = False
            self.lock.release()
            self.thread.join()
        else:
            self.lock.release()


    def _thread(self):
        while True:
            try:
                self.socket.settimeout(1.0)
                data, addr = self.socket.recvfrom(1024)
                self._processData(data)
            except socket.timeout:
                pass

            with self.lock:
                if not self.keepRunning:
                    return

    def _extract(self, data, pattern):
        match = re.search(pattern, data)
        if not match:
            print "Pattern was not found in the data {}".format(pattern)
            return None
        return match.group(1)

    def _processData(self, data):
        try:
            eui = self._extract(data, 'EUI-64=([^;]+);')
            temp = self._extract(data, 'temperature=([^^]+)\^C;')
            humid = self._extract(data, 'humidity=([^%]+)%;')
            batVolt = self._extract(data, 'voltage=([^V]+)V;')

            temp = round(float(temp) * 1000)
            humid = round(float(humid) * 10)
            batVolt = round(float(batVolt) * 1000)
        except ValueError as e:
            print 'Cause: {}'.format(str(e))
            print 'Received invalid data packet "{}"'.format(data)

        sensor = self.sensorSet.getSensorByEUI(eui)
        if sensor:
            sensor.newReading(temp, humid, batVolt)
        else:
            print 'Sensor with EUI {} is not in the given configuration file.'.format(eui)


class PublisherApp(object):
    def main(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('CONFIG_FILE',
                            help='configuration file obtained from InviNets website',
        )
        parser.add_argument('--incoming_readings_port',
                            help='port on which this scripts expects readings from the router (default: 9001)',
                            default=9001, type=int)
        parser.add_argument('--snmp_publish_port',
                            help='port on which the SNPM agent will publish the readings (default: 161)',
                            default=161, type=int)
        args = parser.parse_args()

        self.sensorSet = SensorSet(open(args.CONFIG_FILE))

        self.readingsReceiver = UDPReadingsReceiver(self.sensorSet, '127.0.0.1',
                                                    args.incoming_readings_port)

        try:
            self.agent = SNMPAgentForSensors('127.0.0.1', args.snmp_publish_port)
        except pysnmp.carrier.error.CarrierError as e:
            if (('bind()' in str(e) and 'Permission denied' in str(e)) or
                'access permission' in str(e)):
                print ('To use the default SNMP publishing port 161 you need '
                       'administrator rights.\n'
                       'Either grant them to this script (sudo, run as administrator) ' \
                       'or change the publishing port to value larger than 1024 (see -h).')
                return
            raise

        for s in self.sensorSet.getAll():
            self.agent.publishSensor(s)

        self.readingsReceiver.startAsyncListening()
        try:
            print 'Starting the SNMP agent. Ctrl+C to stop.'
            self.agent.startPublishLoop()
        except KeyboardInterrupt:
            print 'Stopping the SNMP agent.'
        finally:
            self.readingsReceiver.stopListening()


if __name__ == '__main__':
    app = PublisherApp()
    app.main()








