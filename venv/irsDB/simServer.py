# сервер для симуляции выдачи данных с ПЛК
URL = "opc.tcp://0.0.0.0:4840"

import sys
import random
import time

from opcua import Server

if __name__ == "__main__":
    server = Server()
    server.set_endpoint(URL)

    objects = server.get_objects_node()
    ns = server.register_namespace("WELD_DATA1")
    ns3 = server.register_namespace("ServerInter")
    ns4 = server.register_namespace("WELD_DATA")

    ServerInterfaces = objects.add_object(ns3, "ServerInterfaces")
    WELD_DATA = ServerInterfaces.add_object(ns4, "WELD_DATA_RAMY")
    db = WELD_DATA.add_object(ns4, "ROB_DB")
    speed = db.add_variable(ns4, "ROB_Actual_Speed", 0.0)
    process = db.add_variable(ns4, "ROB_Weld_Start", False)
    jobNumb = db.add_variable(ns4, "ROB_Job_Number", 1)
    wireSpeed = db.add_variable(ns4, "ROB_Wire_Speed", 0.0)
    oscnode = db.add_variable(ns4, "ROB_Weaving_Set_Num", 1)

    db1 = WELD_DATA.add_object(ns4, "PS_DB")
    processPs = db1.add_variable(ns4, "PS_Process_Active", False)
    voltPs = db1.add_variable(ns4, "PS_Weld_Voltage", 0.0)
    currPs = db1.add_variable(ns4, "PS_Weld_Current", 0.0)
    wirePs = db1.add_variable(ns4, "PS_Wire_Feed", 0.0)
    errPs = db1.add_variable(ns4, "PS_Error_Number", 0)
    errPs = db1.add_variable(ns4, "PS_Arc_Stable", True)


    db2 = WELD_DATA.add_object(ns4, "PLC_DB")
    plcTime = db2.add_object(ns4, "PLC_time")
    nanoTime = plcTime.add_variable(ns4, "NANOSECOND", time.time())



    server.start()

    while True:
        processPs.set_value(True)
        for i in range(60):
            V = random.uniform(19.0, 24.0)
            print("{:8.1f} В".format(V))
            voltPs.set_value(V)

            V = random.uniform(115.0, 125.0)
            print("{:8.1f} A".format(V))
            currPs.set_value(V)

            V = random.uniform(65.0, 75.0)
            print("{:8.1f} cм/м".format(V))
            speed.set_value(V)

            V = random.uniform(4.0, 5.0)
            print("{:8.1f} м/м".format(V))
            wirePs.set_value(V)

            time.sleep(0.1)
            nanoTime.set_value(time.time())
        processPs.set_value(False)

    server.stop()