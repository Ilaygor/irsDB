import time
import datetime
from opcua import Client, ua
import struct
from models import Seam, Equipment, OscilationType

def addSeam(torchSpeed,wireSpeed,current,voltage,
            burnerOscillation, errNum, weldingProgramm,
            startTime,endTime, period,
            equpmetId, userId):
    gasConsumption = []
    btorchSpeed = struct.pack('%sf' % len(torchSpeed), *torchSpeed)
    bwireSpeed = struct.pack('%sf' % len(wireSpeed), *wireSpeed)
    bcurrent = struct.pack('%sf' % len(current), *current)
    bvoltage = struct.pack('%sf' % len(voltage), *voltage)
    #активировать, когда будет готов ПЛК !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    oscId = OscilationType.get(OscilationType.oscNumber == burnerOscillation).id

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
         burnerOscillation=burnerOscillation,  # BlobField()
         current=bcurrent,  # BlobField()
         voltage=bvoltage,  # BlobField()
         voltageCorrection=b'0',  # BlobField()
         wireSpeed=bwireSpeed,  # BlobField()
         gasConsumption=b'0',
         period = period# BlobField()
         ).save()


class SubHandler(object):

    def __init__(self, Nodes, weldProg, eqwNum, userId, statusBar = None):
        self.statusBar = statusBar

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
            if self.statusBar is not None:
                self.statusBar.showMessage("Начат новый шов", 3000)
        elif node == self.nodes["PS_Process_Active"] and not val:
            if self.startTime is not None:
                print("end seam")
                self.endTime = datetime.datetime.now()
                print(self.endTime - self.startTime)
                periodDateTime =(self.endTime - self.startTime)/len(self.voltMass)
                self.period = periodDateTime.seconds + periodDateTime.microseconds/1000000
                #print("times", self.startTime, self.endTime, self.endTime - self.startTime)
                print("period", self.period)
                print("errCode", self.errCode)
                print("weldProg",self.weldingProgramm)
                print("eqwNum", self.eqwNum)
                print("oscNum",self.oscTypeNum)
                print("user", self.userId)
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
                if self.statusBar is not None:
                    self.statusBar.showMessage("Шов добавлен", 3000)
            #except: print("no seam")
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

    def __init__(self, IP, statusBar, userId):
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
            node = root.get_child(["0:Objects","3:ServerInterfaces"])#,"4:WELD_DATA_RAMY"])
            for n in node.get_children():
                print(n.get_browse_name())
            print(self.IP)
            if self.IP == "172.31.1.32":
                ustanovka = "4:WELD_DATA_RAMY"
            elif self.IP == "172.31.1.33":
                ustanovka = "4:WELD_DATA_OBECHAYKI"
            else:
                ustanovka = "4:WELD_DATA_RAMY"
            speedNode = root.get_child(["0:Objects","3:ServerInterfaces",ustanovka, "4:ROB_DB", "4:ROB_Actual_Speed"])
            jobNumbNode = root.get_child(["0:Objects","3:ServerInterfaces",ustanovka, "4:ROB_DB", "4:ROB_Job_Number"])
            wireSpeedNode = root.get_child(["0:Objects","3:ServerInterfaces",ustanovka, "4:ROB_DB", "4:ROB_Wire_Speed"])
            processNode = root.get_child(["0:Objects","3:ServerInterfaces",ustanovka, "4:ROB_DB", "4:ROB_Weld_Start"])
            oscNode = root.get_child(["0:Objects","3:ServerInterfaces",ustanovka, "4:ROB_DB", "4:ROB_Weaving_Set_Num"])

            processPsNode = root.get_child(["0:Objects","3:ServerInterfaces",ustanovka, "4:PS_DB", "4:PS_Process_Active"])
            voltPsNode = root.get_child(["0:Objects","3:ServerInterfaces",ustanovka, "4:PS_DB", "4:PS_Weld_Voltage"])
            currPsNode = root.get_child(["0:Objects","3:ServerInterfaces",ustanovka, "4:PS_DB", "4:PS_Weld_Current"])
            wirePsNode = root.get_child(["0:Objects","3:ServerInterfaces",ustanovka, "4:PS_DB", "4:PS_Wire_Feed"])
            errPsNode = root.get_child(["0:Objects","3:ServerInterfaces",ustanovka, "4:PS_DB", "4:PS_Error_Number"])
            arcStbNode = root.get_child(["0:Objects","3:ServerInterfaces",ustanovka, "4:PS_DB", "4:PS_Arc_Stable"])

            plcTimeNode = root.get_child(["0:Objects","3:ServerInterfaces",ustanovka, "4:PLC_DB", "4:PLC_time","4:NANOSECOND"])

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
            handler = SubHandler(Nodes, weldProg, eqwNum, self.userId, self.statusBar)
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
            if self.statusBar is not None:
                self.statusBar.showMessage("Подключение не установлено", 3000)
        return self.active

    def stop(self):
        if self.client.keepalive is not None:
            self.client.disconnect()
        self.active = False

if __name__ == "__main__":
    h = DataHarvestr("localhost", None,1)
    h.start()
    """h2 = DataHarvestr("172.31.1.32", None, 1)
    h2.start()"""
    #volt = [17.28, 17.28, 15.4, 15.92, 16.32, 16.48, 16.41, 16.43, 16.23, 16.04, 16.41, 15.39, 16.15, 16.63, 16.64, 16.43, 16.73, 16.04, 15.95, 16.36, 16.09, 16.56, 15.56, 15.97, 15.81, 16.39, 16.21, 16.2, 15.97, 15.7, 15.98, 16.16, 15.88, 15.92, 14.93, 16.16, 16.16]
    #speed = [144.2, 144.2, 171.8, 170.2, 159.2, 164.0, 161.1, 155.6, 161.0, 164.6, 164.0, 170.4, 163.9, 156.3, 163.7, 166.7, 161.9, 169.4, 169.0, 165.1, 167.1, 162.3, 173.2, 173.8, 176.2, 172.3, 168.2, 170.3, 173.8, 174.4, 169.6, 170.6, 180.3, 172.3, 140.7, 163.0, 163.0]
    #curr = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    #wire = [4.0, 4.0, 3.93, 3.93, 3.93, 3.93, 3.93, 3.93, 3.93, 3.93, 3.93, 3.93, 3.93, 3.94, 3.93, 3.93, 3.93, 3.93, 3.93, 3.93, 3.93, 3.93, 3.93, 3.93, 3.94, 3.94, 3.94, 3.93, 3.93, 3.93, 3.94, 3.94, 3.93, 3.93, 3.1, 3.93, 3.93]
    """mass = [1,2,3,4]
    stTime = datetime.datetime.now()
    time.sleep(5)
    enTime = datetime.datetime.now()
    periodDateTime = (enTime - stTime) / len(mass)
    period = periodDateTime.seconds + periodDateTime.microseconds / 1000000
    print(period)"""
    """addSeam(speed, wire, curr, volt,
            0, 0, 4,
            stTime, enTime, 1.061148,
            2,1)"""