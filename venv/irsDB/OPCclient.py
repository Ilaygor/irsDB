import time
from opcua import Client, ua


class SubHandler(object):

    def __init__(self, Nodes, weldProg, eqwNum):
        self.volt = 0
        self.curr = 0
        self.speed = 0
        self.wireSpeed = 0
        self.arcStb = False
        self.period = 0
        self.times = []
        self.eqwNum = eqwNum

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
        if node == self.nodes["ROB_Weld_Start"] and val:
            print("new seam")
            self.voltMass = []
            self.currMass = []
            self.speedMass = []
            self.wireSpeedMass = []
            self.startTime = time.time()
            self.times = []
            self.errCode = 0
        elif node == self.nodes["ROB_Weld_Start"] and not val:
            print("end seam")
            self.endTime = time.time()
            self.period = (self.times[-1]-self.times[0])/len(self.times)
            print("times", self.startTime, self.endTime, self.endTime - self.startTime)
            print("period", self.period)
            print("errCode", self.errCode)
            print("weldProg",self.weldingProgramm)
            print("eqwNum", self.eqwNum)
            print("volt",self.voltMass)
            print("curr",self.currMass)
            print("speed",self.speedMass)
            print("wire",self.wireSpeedMass)
            print(len(self.voltMass))
            #addSeam([],[],[],self.volt,[],[])
        elif node == self.nodes["PS_Weld_Voltage"]:
            self.volt = val
        elif node == self.nodes["PS_Weld_Current"]:
            self.curr = val
        elif node == self.nodes["ROB_Actual_Speed"]:
            self.speed = val
        elif node == self.nodes["PS_Wire_Feed"]:
            self.wireSpeed = val
        elif node == self.nodes["PS_Error_Number"]:
            self.errCode = val
        elif node == self.nodes["ROB_Job_Number"]:
            self.weldingProgramm = val
        elif node == self.nodes["PLC_time"]:
            self.voltMass.append(self.volt)
            self.currMass.append(self.curr)
            self.speedMass.append(self.speed)
            self.wireSpeedMass.append(self.wireSpeed)
            self.times.append(val)


    def event_notification(self, event):
        print("new event", event)


class DataHarvestr():
    #ActSeam = ActualSeam()

    def __init__(self, IP):
        self.IP = IP
        self.client = Client("opc.tcp://"+self.IP+":4840")
        self.client.connect()
        root = self.client.get_root_node()
        try:
            print("eqw",Equipment.get(Equipment.ip == self.IP).id)
            eqwNum = Equipment.get(Equipment.ip == self.IP).id
        except:
            eqwNum = None
        speedNode = root.get_child(["0:Objects", "2:ROB_DB", "2:ROB_Actual_Speed"])
        jobNumbNode = root.get_child(["0:Objects", "2:ROB_DB", "2:ROB_Job_Number"])
        wireSpeedNode = root.get_child(["0:Objects", "2:ROB_DB", "2:ROB_Wire_Speed"])
        processNode = root.get_child(["0:Objects", "2:ROB_DB", "2:ROB_Weld_Start"])

        processPsNode = root.get_child(["0:Objects", "2:PS_DB", "2:PS_Process_Active"])
        voltPsNode = root.get_child(["0:Objects", "2:PS_DB", "2:PS_Weld_Voltage"])
        currPsNode = root.get_child(["0:Objects", "2:PS_DB", "2:PS_Weld_Current"])
        wirePsNode = root.get_child(["0:Objects", "2:PS_DB", "2:PS_Wire_Feed"])
        errPsNode = root.get_child(["0:Objects", "2:PS_DB", "2:PS_Error_Number"])
        arcStbNode = root.get_child(["0:Objects", "2:PS_DB", "2:PS_Arc_Stable"])

        plcTimeNode = root.get_child(["0:Objects", "2:PLC_DB", "2:PLC_time"])

        Nodes = {"ROB_Actual_Speed":speedNode,
                 "ROB_Weld_Start":processNode,
                 "ROB_Job_Number":jobNumbNode,
                 "ROB_Wire_Speed":wireSpeedNode,
                 "ROB_Process_Active":processPsNode,
                 "PS_Weld_Voltage":voltPsNode,
                 "PS_Weld_Current":currPsNode,
                 "PS_Wire_Feed":wirePsNode,
                 "PS_Error_Number":errPsNode,
                 "PS_Arc_Stable":arcStbNode,
                 "PLC_time":plcTimeNode
                 }

        weldProg = jobNumbNode.get_value()
        handler = SubHandler(Nodes, weldProg, eqwNum)
        sub = self.client.create_subscription(100, handler)
        speedHandle = sub.subscribe_data_change(speedNode)
        processHandle = sub.subscribe_data_change(processNode)
        jobNumbHandle = sub.subscribe_data_change(jobNumbNode)
        wireSpeedNode = sub.subscribe_data_change(wireSpeedNode)

        processPsHandle = sub.subscribe_data_change(processPsNode)
        voltPsHandle = sub.subscribe_data_change(voltPsNode)
        currPsHandle = sub.subscribe_data_change(currPsNode)
        wirePsHandle = sub.subscribe_data_change(wirePsNode)
        errPsHandle = sub.subscribe_data_change(errPsNode)
        plcTimeHandle = sub.subscribe_data_change(plcTimeNode)

        arcStbHandle = sub.subscribe_data_change(arcStbNode)

if __name__ == "__main__":
    client1 = Client(URL1)
    client1.connect()
    root1 = client1.get_root_node()
    print(root1)
    print("Children of root are: ", root1.get_children())
    print(root1.get_children()[0].get_children()[1])#

    DB1 = root1.get_child(["0:Objects", "3:ServerInterfaces","4:WELD_DATA","4:ROB_DB"])
    robWeldStart1 = DB1.get_child("4:ROB_Actual_Speed")

    client2 = Client(URL2)
    client2.connect()
    root2 = client2.get_root_node()
    DB2 = root2.get_child(["0:Objects", "3:ServerInterfaces", "4:WELD_DATA", "4:ROB_DB"])
    robWeldStart2 = DB2.get_child("4:ROB_Actual_Speed")

    while True:
        print("ROB_Actual_Speed1:", robWeldStart1.get_value()/10, "м/c")
        print("ROB_Actual_Speed2:", robWeldStart2.get_value() / 10, "м/c")
        #print("ROB_Act_Speed_Factor:", spFactor.get_value())
        time.sleep(0.1)