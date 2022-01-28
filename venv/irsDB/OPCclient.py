import time
import datetime
from opcua import Client, ua
import struct
from models import Seam, Equipment

def addSeam(torchSpeed,wireSpeed,current,voltage,
            burnerOscillation, errNum, weldingProgramm,
            startTime,endTime, period,
            equpmetId, userId):
    gasConsumption = []
    btorchSpeed = struct.pack('%sf' % len(torchSpeed), *torchSpeed)
    bwireSpeed = struct.pack('%sf' % len(wireSpeed), *wireSpeed)
    bcurrent = struct.pack('%sf' % len(current), *current)
    bvoltage = struct.pack('%sf' % len(voltage), *voltage)
    #bburnerOscillation = struct.pack('%sf' % len(burnerOscillation), *burnerOscillation)
    #bvoltageCorrection = struct.pack('%sf' % len(voltageCorrection), *voltageCorrection)

    #bgasConsumption = struct.pack('%sf' % len(gasConsumption), *gasConsumption)

    Seam(connId=None,  # ForeignKeyField(Connection)
         detailId=None,  # ForeignKeyField(Detail)
         equipmentId=equpmetId,
         batchNumber="",  # CharField()
         detailNumber="",  # CharField()
         authorizedUser=userId,  # CharField()
         weldingProgram=str(weldingProgramm),  # CharField()
         startTime=startTime,  # DateTimeField()
         endTime=endTime,  # DateTimeField()
         endStatus=errNum,  # BooleanField()
         torchSpeed=btorchSpeed,  # BlobField()
         burnerOscillation=1,  # BlobField()
         current=bcurrent,  # BlobField()
         voltage=bvoltage,  # BlobField()
         voltageCorrection=b'0',  # BlobField()
         wireSpeed=bwireSpeed,  # BlobField()
         gasConsumption=b'0',
         period = period# BlobField()
         ).save()


class SubHandler(object):

    def __init__(self, Nodes, weldProg, eqwNum, userId):
        self.volt = 0
        self.curr = 0
        self.speed = 0
        self.wireSpeed = 0
        self.arcStb = False
        self.period = 0
        self.times = []
        self.eqwNum = eqwNum
        self.userId = userId
        self.oscTypeNum = 1

        self.weldingProgramm = weldProg
        self.errCode = 0

        self.startTime = None
        self.endTime = None

        self.voltMass = []
        self.currMass = []
        self.speedMass = []
        self.wireSpeedMass = []
        self.arcStbMass = []

        self.nodes = Nodes

    def datachange_notification(self, node, val, data):
        #print("dataChange", node, val)
        if node == self.nodes["PS_Process_Active"] and val:
            print("new seam")
            self.startTime = datetime.datetime.now()
            self.voltMass = []
            self.currMass = []
            self.speedMass = []
            self.wireSpeedMass = []
            self.times = []
            self.errCode = 0
        elif node == self.nodes["PS_Process_Active"] and not val:
            try:
                print("end seam")
                self.endTime = datetime.datetime.now()
                print(self.endTime - self.startTime)
                self.period = ((self.endTime - self.startTime)/len(self.voltMass)).microseconds/1000000
                #print("times", self.startTime, self.endTime, self.endTime - self.startTime)
                print("period", self.period)
                print("errCode", self.errCode)
                print("weldProg",self.weldingProgramm)
                print("eqwNum", self.eqwNum)
                print("volt",self.voltMass)
                print("curr",self.currMass)
                print("speed",self.speedMass)
                print("wire",self.wireSpeedMass)
                print(len(self.voltMass))
                addSeam(self.speedMass,self.wireSpeedMass,self.currMass,self.voltMass,
                        self.oscTypeNum,self.errCode,self.weldingProgramm,
                        self.startTime,self.endTime,self.period,
                        self.eqwNum, self.userId)
                self.startTime = None
            except: print("no seam")
        elif node == self.nodes["PS_Weld_Voltage"]:
            self.volt = val
        elif node == self.nodes["PS_Weld_Current"]:
            self.curr = val
        elif node == self.nodes["ROB_Actual_Speed"]:
            self.speed = val
        elif node == self.nodes["PS_Wire_Feed"]:
            self.wireSpeed = val/100
        elif node == self.nodes["PS_Error_Number"]:
            self.errCode = val
        elif node == self.nodes["ROB_Job_Number"]:
            self.weldingProgramm = val
        elif node == self.nodes["ROB_Welding_Set_Num"]:
            self.oscTypeNum = val
        elif node == self.nodes["PLC_time"]:
            self.voltMass.append(self.volt/100)
            self.currMass.append(self.curr/10)
            self.speedMass.append(self.speed*60*100/10000)
            self.wireSpeedMass.append(self.wireSpeed)
            self.times.append(val)


    def event_notification(self, event):
        print("new event", event)


class DataHarvestr():
    #ActSeam = ActualSeam()

    def __init__(self, IP, statusBar,userId):
        self.IP = IP
        self.client = Client("opc.tcp://"+self.IP+":4840")
        self.statusBar = statusBar
        self.userId = userId
        self.active = False

    def start(self):
        try:
            eqwNum = Equipment.get(Equipment.ip == self.IP).id
        except:
            eqwNum = None
        try:
            self.client.connect()
            self.active = True
            root = self.client.get_root_node()
            """node = root.get_child(["0:Objects","3:ServerInterfaces","4:WELD_DATA_RAMY"])
            for n in node.get_children():
                print(n.get_browse_name())"""
            speedNode = root.get_child(["0:Objects","3:ServerInterfaces","4:WELD_DATA_RAMY", "4:ROB_DB", "4:ROB_Actual_Speed"])
            jobNumbNode = root.get_child(["0:Objects","3:ServerInterfaces","4:WELD_DATA_RAMY", "4:ROB_DB", "4:ROB_Job_Number"])
            wireSpeedNode = root.get_child(["0:Objects","3:ServerInterfaces","4:WELD_DATA_RAMY", "4:ROB_DB", "4:ROB_Wire_Speed"])
            processNode = root.get_child(["0:Objects","3:ServerInterfaces","4:WELD_DATA_RAMY", "4:ROB_DB", "4:ROB_Weld_Start"])
            oscNode = root.get_child(["0:Objects","3:ServerInterfaces","4:WELD_DATA_RAMY", "4:ROB_DB", "4:ROB_Weaving_Set_Num"])

            processPsNode = root.get_child(["0:Objects","3:ServerInterfaces","4:WELD_DATA_RAMY", "4:PS_DB", "4:PS_Process_Active"])
            voltPsNode = root.get_child(["0:Objects","3:ServerInterfaces","4:WELD_DATA_RAMY", "4:PS_DB", "4:PS_Weld_Voltage"])
            currPsNode = root.get_child(["0:Objects","3:ServerInterfaces","4:WELD_DATA_RAMY", "4:PS_DB", "4:PS_Weld_Current"])
            wirePsNode = root.get_child(["0:Objects","3:ServerInterfaces","4:WELD_DATA_RAMY", "4:PS_DB", "4:PS_Wire_Feed"])
            errPsNode = root.get_child(["0:Objects","3:ServerInterfaces","4:WELD_DATA_RAMY", "4:PS_DB", "4:PS_Error_Number"])
            arcStbNode = root.get_child(["0:Objects","3:ServerInterfaces","4:WELD_DATA_RAMY", "4:PS_DB", "4:PS_Arc_Stable"])

            plcTimeNode = root.get_child(["0:Objects","3:ServerInterfaces","4:WELD_DATA_RAMY", "4:PLC_DB", "4:PLC_time","4:NANOSECOND"])

            print("plc time", plcTimeNode.get_value())
            print("Nodes")

            Nodes = {"ROB_Actual_Speed":speedNode,
                     "ROB_Weld_Start":processNode,
                     "ROB_Job_Number":jobNumbNode,
                     "ROB_Wire_Speed":wireSpeedNode,
                     "PS_Process_Active":processPsNode,
                     "PS_Weld_Voltage":voltPsNode,
                     "PS_Weld_Current":currPsNode,
                     "PS_Wire_Feed":wirePsNode,
                     "PS_Error_Number":errPsNode,
                     "PS_Arc_Stable":arcStbNode,
                     "PLC_time":plcTimeNode,
                     "ROB_Welding_Set_Num":oscNode
                     }

            weldProg = jobNumbNode.get_value()
            handler = SubHandler(Nodes, weldProg, eqwNum, self.userId)
            sub = self.client.create_subscription(100, handler)
            speedHandle = sub.subscribe_data_change(speedNode)
            processHandle = sub.subscribe_data_change(processNode)
            jobNumbHandle = sub.subscribe_data_change(jobNumbNode)
            wireSpeedHandle = sub.subscribe_data_change(wireSpeedNode)
            oscHandle = sub.subscribe_data_change(oscNode)

            processPsHandle = sub.subscribe_data_change(processPsNode)
            voltPsHandle = sub.subscribe_data_change(voltPsNode)
            currPsHandle = sub.subscribe_data_change(currPsNode)
            wirePsHandle = sub.subscribe_data_change(wirePsNode)
            errPsHandle = sub.subscribe_data_change(errPsNode)
            plcTimeHandle = sub.subscribe_data_change(plcTimeNode)

            arcStbHandle = sub.subscribe_data_change(arcStbNode)
        except:
            print("end of connection")
            self.active = False

    def stop(self):
        self.client.disconnect()
        self.active = False

if __name__ == "__main__":
    """h = DataHarvestr("172.31.1.32")
    h.start()"""
    mass = [1,2,3,2,3,2,2,4,3,2]
    stTime = datetime.datetime.now()
    time.sleep(1)
    enTime = datetime.datetime.now()
    addSeam(mass, mass, mass, mass,
            1, 0, 2, stTime, enTime, 0.1)
    addSeam(torchSpeed, wireSpeed, current, voltage,
            burnerOscillation, errNum, weldingProgramm,
            startTime, endTime, period)