""" PI"""

def initial_pi_device(pi_device):

    try:
        pi_device.ConnectUSB ('0111176619')  # Connect to the controller via USB with serial number 0111176619
        print(pi_device.qIDN()) #Out[]: 'Physik Instrumente, E-517, 0111176619, V01.243'
        axes = ['A','B','C']
        allTrue = [True, True, True]
        allFalse = [False, False, False]
        pi_device.ONL([1,2,3],[1,1,1])  # Turn on the Online config (PC master)
        pi_device.DCO(axes, allTrue)  # Turn on the drift compensation mode
        pi_device.SVO (axes, allTrue)  # Turn on servo control
        pi_device.VCO(axes, allFalse)  # Turn off Velocity control. Can't move if ON
        
        pi_device.MOV(axes, [100, 100, 50])  # move away from origin (0,0,0)
        
    except IOError as e:
        
        print("I/O error({0}): {1}".format(e.errno, e.strerror))
        print("Can't connect to the platine.")
    
    servo_time = 0.000040  # seconds  # tiempo del servo: 40­µs. lo dice qGWD()