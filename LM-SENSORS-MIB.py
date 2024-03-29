# PySNMP SMI module. Autogenerated from smidump -f python LM-SENSORS-MIB
# by libsmi2pysnmp-0.0.7-alpha at Wed Apr 18 01:00:32 2012,
# Python version sys.version_info(major=2, minor=7, micro=1, releaselevel='final', serial=0)

# Imported just in case new ASN.1 types would be created
from pyasn1.type import constraint, namedval

# Imports

( Integer, ObjectIdentifier, OctetString, ) = mibBuilder.importSymbols("ASN1", "Integer", "ObjectIdentifier", "OctetString")
( Bits, Gauge32, Integer32, Integer32, ModuleIdentity, MibIdentifier, MibScalar, MibTable, MibTableRow, MibTableColumn, TimeTicks, ) = mibBuilder.importSymbols("SNMPv2-SMI", "Bits", "Gauge32", "Integer32", "Integer32", "ModuleIdentity", "MibIdentifier", "MibScalar", "MibTable", "MibTableRow", "MibTableColumn", "TimeTicks")
( DisplayString, ) = mibBuilder.importSymbols("SNMPv2-TC", "DisplayString")
( ucdExperimental, ) = mibBuilder.importSymbols("UCD-SNMP-MIB", "ucdExperimental")

# Objects

lmSensors = MibIdentifier((1, 3, 6, 1, 4, 1, 2021, 13, 16))
lmSensorsMIB = ModuleIdentity((1, 3, 6, 1, 4, 1, 2021, 13, 16, 1)).setRevisions(("2000-11-05 00:00",))
lmTempSensorsTable = MibTable((1, 3, 6, 1, 4, 1, 2021, 13, 16, 2))
lmTempSensorsEntry = MibTableRow((1, 3, 6, 1, 4, 1, 2021, 13, 16, 2, 1)).setIndexNames((0, "LM-SENSORS-MIB", "lmTempSensorsIndex"))
lmTempSensorsIndex = MibTableColumn((1, 3, 6, 1, 4, 1, 2021, 13, 16, 2, 1, 1), Integer32().subtype(subtypeSpec=constraint.ValueRangeConstraint(0, 65535))).setMaxAccess("readonly")
lmTempSensorsDevice = MibTableColumn((1, 3, 6, 1, 4, 1, 2021, 13, 16, 2, 1, 2), DisplayString()).setMaxAccess("readonly")
lmTempSensorsValue = MibTableColumn((1, 3, 6, 1, 4, 1, 2021, 13, 16, 2, 1, 3), Gauge32()).setMaxAccess("readonly")
lmFanSensorsTable = MibTable((1, 3, 6, 1, 4, 1, 2021, 13, 16, 3))
lmFanSensorsEntry = MibTableRow((1, 3, 6, 1, 4, 1, 2021, 13, 16, 3, 1)).setIndexNames((0, "LM-SENSORS-MIB", "lmFanSensorsIndex"))
lmFanSensorsIndex = MibTableColumn((1, 3, 6, 1, 4, 1, 2021, 13, 16, 3, 1, 1), Integer32().subtype(subtypeSpec=constraint.ValueRangeConstraint(0, 65535))).setMaxAccess("readonly")
lmFanSensorsDevice = MibTableColumn((1, 3, 6, 1, 4, 1, 2021, 13, 16, 3, 1, 2), DisplayString()).setMaxAccess("readonly")
lmFanSensorsValue = MibTableColumn((1, 3, 6, 1, 4, 1, 2021, 13, 16, 3, 1, 3), Gauge32()).setMaxAccess("readonly")
lmVoltSensorsTable = MibTable((1, 3, 6, 1, 4, 1, 2021, 13, 16, 4))
lmVoltSensorsEntry = MibTableRow((1, 3, 6, 1, 4, 1, 2021, 13, 16, 4, 1)).setIndexNames((0, "LM-SENSORS-MIB", "lmVoltSensorsIndex"))
lmVoltSensorsIndex = MibTableColumn((1, 3, 6, 1, 4, 1, 2021, 13, 16, 4, 1, 1), Integer32().subtype(subtypeSpec=constraint.ValueRangeConstraint(0, 65535))).setMaxAccess("readonly")
lmVoltSensorsDevice = MibTableColumn((1, 3, 6, 1, 4, 1, 2021, 13, 16, 4, 1, 2), DisplayString()).setMaxAccess("readonly")
lmVoltSensorsValue = MibTableColumn((1, 3, 6, 1, 4, 1, 2021, 13, 16, 4, 1, 3), Gauge32()).setMaxAccess("readonly")
lmMiscSensorsTable = MibTable((1, 3, 6, 1, 4, 1, 2021, 13, 16, 5))
lmMiscSensorsEntry = MibTableRow((1, 3, 6, 1, 4, 1, 2021, 13, 16, 5, 1)).setIndexNames((0, "LM-SENSORS-MIB", "lmMiscSensorsIndex"))
lmMiscSensorsIndex = MibTableColumn((1, 3, 6, 1, 4, 1, 2021, 13, 16, 5, 1, 1), Integer32().subtype(subtypeSpec=constraint.ValueRangeConstraint(0, 65535))).setMaxAccess("readonly")
lmMiscSensorsDevice = MibTableColumn((1, 3, 6, 1, 4, 1, 2021, 13, 16, 5, 1, 2), DisplayString()).setMaxAccess("readonly")
lmMiscSensorsValue = MibTableColumn((1, 3, 6, 1, 4, 1, 2021, 13, 16, 5, 1, 3), Gauge32()).setMaxAccess("readonly")

# Augmentions

# Exports

# Module identity
mibBuilder.exportSymbols("LM-SENSORS-MIB", PYSNMP_MODULE_ID=lmSensorsMIB)

# Objects
mibBuilder.exportSymbols("LM-SENSORS-MIB", lmSensors=lmSensors, lmSensorsMIB=lmSensorsMIB, lmTempSensorsTable=lmTempSensorsTable, lmTempSensorsEntry=lmTempSensorsEntry, lmTempSensorsIndex=lmTempSensorsIndex, lmTempSensorsDevice=lmTempSensorsDevice, lmTempSensorsValue=lmTempSensorsValue, lmFanSensorsTable=lmFanSensorsTable, lmFanSensorsEntry=lmFanSensorsEntry, lmFanSensorsIndex=lmFanSensorsIndex, lmFanSensorsDevice=lmFanSensorsDevice, lmFanSensorsValue=lmFanSensorsValue, lmVoltSensorsTable=lmVoltSensorsTable, lmVoltSensorsEntry=lmVoltSensorsEntry, lmVoltSensorsIndex=lmVoltSensorsIndex, lmVoltSensorsDevice=lmVoltSensorsDevice, lmVoltSensorsValue=lmVoltSensorsValue, lmMiscSensorsTable=lmMiscSensorsTable, lmMiscSensorsEntry=lmMiscSensorsEntry, lmMiscSensorsIndex=lmMiscSensorsIndex, lmMiscSensorsDevice=lmMiscSensorsDevice, lmMiscSensorsValue=lmMiscSensorsValue)

