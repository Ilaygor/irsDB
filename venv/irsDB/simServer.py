URL = "opc.tcp://0.0.0.0:4840"

import sys
import random
import time

from opcua import Server

if __name__ == "__main__":
    server = Server()
    server.set_endpoint(URL)

    objects = server.get_objects_node()
    ns = server.register_namespace("WELD_DATA")
    db = objects.add_object(ns, "ROB_DB")
    speed = db.add_variable(ns, "ROB_Actual_Speed", 0.0)
    process = db.add_variable(ns, "ROB_Weld_Start", False)
    jobNumb = db.add_variable(ns, "ROB_Job_Number", 1)
    wireSpeed = db.add_variable(ns, "ROB_Wire_Speed", 0.0)

    db1 = objects.add_object(ns, "PS_DB")
    processPs = db1.add_variable(ns, "PS_Process_Active", False)
    voltPs = db1.add_variable(ns, "PS_Weld_Voltage", 0.0)
    currPs = db1.add_variable(ns, "PS_Weld_Current", 0.0)
    wirePs = db1.add_variable(ns, "PS_Wire_Feed", 0.0)
    errPs = db1.add_variable(ns, "PS_Error_Number", 0)
    errPs = db1.add_variable(ns, "PS_Arc_Stable", True)


    db2 = objects.add_object(ns, "PLC_DB")
    plcTime = db2.add_variable(ns, "PLC_time", time.time())



    server.start()

    while True:
        process.set_value(True)
        for i in range(60):
            V = random.uniform(190.0, 240.0)
            print("{:8.1f} В".format(V))
            voltPs.set_value(V)

            V = random.uniform(10.0, 20.0)
            print("{:8.1f} A".format(V))
            currPs.set_value(V)

            V = random.uniform(1.0, 3.0)
            print("{:8.1f} м/м".format(V))
            speed.set_value(V)

            V = random.uniform(15.0, 20.0)
            print("{:8.1f} см/м".format(V))
            wirePs.set_value(V)

            time.sleep(0.1)
            plcTime.set_value(time.time())
        process.set_value(False)

    server.stop()