from ctypes import *
import time
import platform
import os, sys

MAX_PATH = 256


class Shamrock:
  __version__ = '0.1'
  
  def __init__(self):
    if sys.platform == "linux":
      self.dll = cdll.LoadLibrary("/usr/local/lib/libshamrockcif.so")
    elif sys.platform == "win32":
      os.environ['PATH'] = os.path.dirname(__file__) + '\\libs\\Windows\\64;' + os.environ['PATH']
      self.dll = windll.LoadLibrary("ShamrockCIF.dll")
    else:
      print("Cannot detect operating system, will now stop")
      raise
      
  # Error Code Returns and Definitions
  SHAMROCK_COMMUNICATION_ERROR = 20201
  SHAMROCK_SUCCESS = 20202
  SHAMROCK_P1INVALID = 20266
  SHAMROCK_P2INVALID = 20267
  SHAMROCK_P3INVALID = 20268
  SHAMROCK_P4INVALID = 20269
  SHAMROCK_P5INVALID = 20270
  SHAMROCK_NOT_INITIALIZED = 20275
  SHAMROCK_NOT_AVAILABLE = 20292
  SHAMROCK_ACCESSORYMIN = 0
  SHAMROCK_ACCESSORYMAX = 1
  SHAMROCK_FILTERMIN = 1
  SHAMROCK_FILTERMAX = 6
  SHAMROCK_TURRETMIN = 1
  SHAMROCK_TURRETMAX = 3
  SHAMROCK_GRATINGMIN = 1
  SHAMROCK_SLITWIDTHMIN = 10
  SHAMROCK_SLITWIDTHMAX = 2500
  SHAMROCK_I24SLITWIDTHMAX = 24000
  SHAMROCK_SHUTTERMODEMIN = 0
  SHAMROCK_SHUTTERMODEMAX = 2
  SHAMROCK_DET_OFFSET_MAX = 240000
  SHAMROCK_GRAT_OFFSET_MAX = 20000
  SHAMROCK_SLIT_INDEX_MIN = 1
  SHAMROCK_SLIT_INDEX_MAX = 4
  SHAMROCK_INPUT_SLIT_SIDE = 1
  SHAMROCK_INPUT_SLIT_DIRECT = 2
  SHAMROCK_OUTPUT_SLIT_SIDE = 3
  SHAMROCK_OUTPUT_SLIT_DIRECT = 4
  SHAMROCK_FLIPPER_INDEX_MIN = 1
  SHAMROCK_FLIPPER_INDEX_MAX = 2
  SHAMROCK_PORTMIN = 0
  SHAMROCK_PORTMAX = 1
  SHAMROCK_INPUT_FLIPPER = 1
  SHAMROCK_OUTPUT_FLIPPER = 2
  SHAMROCK_DIRECT_PORT = 0
  SHAMROCK_SIDE_PORT = 1
  SHAMROCK_ERRORLENGTH = 64
  def ShamrockAccessoryIsPresent(self, device):
    ''' 
        Description:
          Finds if Accessory is present.

        Synopsis:
          (ret, present) = ShamrockAccessoryIsPresent(device)

        Inputs:
          device - Shamrock to interrogate

        Outputs:
          ret - Function Return Code:
            SHAMROCK_SUCCESS - Accessory presence flag returned
            SHAMROCK_NOT_INITIALIZED - Shamrock not initialized
            SHAMROCK_P1INVALID - Invalid device
            SHAMROCK_COMMUNICATION_ERROR - Unable to communicate with Shamrock
          present - pointer to flag::
            0 - Accessory is NOT present
            1 - Accessory IS present

        C++ Equiv:
          unsigned int ShamrockAccessoryIsPresent(int device, int * present);

        See Also:
          ShamrockGetAccessoryState ShamrockSetAccessory 

    '''
    cdevice = c_int(device)
    cpresent = c_int()
    ret = self.dll.ShamrockAccessoryIsPresent(cdevice, byref(cpresent))
    return (ret, cpresent.value)

  def ShamrockAtZeroOrder(self, device):
    ''' 
        Description:
          Finds if wavelength is at zero order.

        Synopsis:
          (ret, atZeroOrder) = ShamrockAtZeroOrder(device)

        Inputs:
          device - Shamrock to interrogate

        Outputs:
          ret - Function Return Code:
            SHAMROCK_SUCCESS - At zero order flag returned
            SHAMROCK_NOT_INITIALIZED - Shamrock not initialized
            SHAMROCK_P1INVALID - Invalid device
            SHAMROCK_COMMUNICATION_ERROR - Unable to communicate with Shamrock
          atZeroOrder - pointer to flag::
            0 - wavelength is NOT at zero order
            1 - wavelength IS at zero order

        C++ Equiv:
          unsigned int ShamrockAtZeroOrder(int device, int * atZeroOrder);

        See Also:
          ShamrockWavelengthIsPresent ShamrockGetWavelength ShamrockGetWavelengthLimits ShamrockSetWavelength ShamrockGotoZeroOrder 

    '''
    cdevice = c_int(device)
    catZeroOrder = c_int()
    ret = self.dll.ShamrockAtZeroOrder(cdevice, byref(catZeroOrder))
    return (ret, catZeroOrder.value)

  def ShamrockAutoSlitIsPresent(self, device, index):
    ''' 
        Description:
          Finds if a specified slit is present.
          

        Synopsis:
          (ret, present) = ShamrockAutoSlitIsPresent(device, index)

        Inputs:
          device - Shamrock to interrogate
          index - Specifies which slit to test whether it is present.:
            SHAMROCK_INPUT_SLIT_SIDE  - (1)
            SHAMROCK_INPUT_SLIT_DIRECT  - (2)
            SHAMROCK_INPUT_SLIT_SIDE - (3)
             SHAMROCK_INPUT_SLIT_DIRECT  - (4)

        Outputs:
          ret - Function Return Code:
            SHAMROCK_SUCCESS - Slit presence flag returned
            SHAMROCK_NOT_INITIALIZED - Shamrock not initialized
            SHAMROCK_P1INVALID - Invalid device
            SHAMROCK_P2INVALID - Invalid slit index
            SHAMROCK_P3INVALID - Parameter is NULL
            SHAMROCK_COMMUNICATION_ERROR - Unable to communicate with Shamrock
          present - pointer to flag:
            0 - Slit is not present
            1 - Slit is present

        C++ Equiv:
          unsigned int ShamrockAutoSlitIsPresent(int device, int index, int * present);

        See Also:
          ShamrockGetAutoSlitWidth ShamrockSetAutoSlitWidth ShamrockAutoSlitReset 

    '''
    cdevice = c_int(device)
    cindex = c_int(index)
    cpresent = c_int()
    ret = self.dll.ShamrockAutoSlitIsPresent(cdevice, cindex, byref(cpresent))
    return (ret, cpresent.value)

  def ShamrockAutoSlitReset(self, device, index):
    ''' 
        Description:
          Resets the specified Slit to its default (10um).
          

        Synopsis:
          ret = ShamrockAutoSlitReset(device, index)

        Inputs:
          device - Select Shamrock to control.
          index - Specifies which slit to reset.:
            SHAMROCK_INPUT_SLIT_SIDE - (1)
            SHAMROCK_INPUT_SLIT_DIRECT - (2)
            SHAMROCK_INPUT_SLIT_SIDE - (3)
             SHAMROCK_INPUT_SLIT_DIRECT  - (4)

        Outputs:
          ret - Function Return Code:
            SHAMROCK_SUCCESS - Shutter presence flag returned
            SHAMROCK_NOT_INITIALIZED - Shamrock not initialized
            SHAMROCK_P1INVALID - Invalid device
            SHAMROCK_P2INVALID - Invalid slit index
            SHAMROCK_COMMUNICATION_ERROR - Unable to communicate with Shamrock

        C++ Equiv:
          unsigned int ShamrockAutoSlitReset(int device, int index);

        See Also:
          ShamrockAutoSlitIsPresent ShamrockGetAutoSlitWidth ShamrockSetAutoSlitWidth 

    '''
    cdevice = c_int(device)
    cindex = c_int(index)
    ret = self.dll.ShamrockAutoSlitReset(cdevice, cindex)
    return (ret)

  def ShamrockClose(self):
    ''' 
        Description:
          Closes the Shamrock system down.

        Synopsis:
          ret = ShamrockClose()

        Inputs:
          None

        Outputs:
          ret - Function Return Code:
            SHAMROCK_SUCCESS - Shamrock shut down

        C++ Equiv:
          unsigned int ShamrockClose(void);

        See Also:
          ShamrockInitialize ShamrockGetNumberDevices ShamrockGetFunctionReturnDescription 

    '''
    ret = self.dll.ShamrockClose()
    return (ret)

  def ShamrockEepromGetOpticalParams(self, device):
    ''' 
        Description:
          Returns the Focal Length, Angular Deviation and Focal Tilt from the Shamrock device.

        Synopsis:
          (ret, FocalLength, AngularDeviation, FocalTilt) = ShamrockEepromGetOpticalParams(device)

        Inputs:
          device - Shamrock to interrogate

        Outputs:
          ret - Function Return Code:
            SHAMROCK_SUCCESS - Focal Length, Angular Deviation and Focal Tilt returned
            SHAMROCK_NOT_INITIALIZED - Shamrock not initialized
            SHAMROCK_P1INVALID - Invalid device
            SHAMROCK_COMMUNICATION_ERROR - Unable to communicate with Shamrock
          FocalLength - pointer to Focal Length
          AngularDeviation - pointer to Angular Deviation
          FocalTilt - pointer to Focal Tilt

        C++ Equiv:
          unsigned int ShamrockEepromGetOpticalParams(int device, float * FocalLength, float * AngularDeviation, float * FocalTilt);

        See Also:
          ShamrockGetSerialNumber 

    '''
    cdevice = c_int(device)
    cFocalLength = c_float()
    cAngularDeviation = c_float()
    cFocalTilt = c_float()
    ret = self.dll.ShamrockEepromGetOpticalParams(cdevice, byref(cFocalLength), byref(cAngularDeviation), byref(cFocalTilt))
    return (ret, cFocalLength.value, cAngularDeviation.value, cFocalTilt.value)

  def ShamrockFilterIsPresent(self, device):
    ''' 
        Description:
          Finds if Filter is present.

        Synopsis:
          (ret, present) = ShamrockFilterIsPresent(device)

        Inputs:
          device - Shamrock to interrogate

        Outputs:
          ret - Function Return Code:
            SHAMROCK_SUCCESS - Filter presence flag returned
            SHAMROCK_NOT_INITIALIZED - Shamrock not initialized
            SHAMROCK_P1INVALID - Invalid device
            SHAMROCK_COMMUNICATION_ERROR - Unable to communicate with Shamrock
          present - pointer to flag::
            0 - Filter is NOT present
            1 - Filter IS present

        C++ Equiv:
          unsigned int ShamrockFilterIsPresent(int device, int * present);

        See Also:
          ShamrockGetFilter ShamrockSetFilter ShamrockGetFilterInfo ShamrockSetFilterInfo 

    '''
    cdevice = c_int(device)
    cpresent = c_int()
    ret = self.dll.ShamrockFilterIsPresent(cdevice, byref(cpresent))
    return (ret, cpresent.value)

  def ShamrockFilterReset(self, device):
    ''' 
        Description:
          Resets the filter to its default position. 
          

        Synopsis:
          ret = ShamrockFilterReset(device)

        Inputs:
          device - Shamrock to reset the filter

        Outputs:
          ret - Function Return Code:
            SHAMROCK_SUCCESS - Filter reset
            SHAMROCK_NOT_INITIALIZED - Shamrock not initialized
            SHAMROCK_P1INVALID - Invalid device
            SHAMROCK_COMMUNICATION_ERROR - Unable to communicate with Shamrock

        C++ Equiv:
          unsigned int ShamrockFilterReset(int device);

        See Also:
          ShamrockSetFilter ShamrockGetFilter ShamrockSetFilterInfo ShamrockGetFilterInfo ShamrockFilterIsPresent 

    '''
    cdevice = c_int(device)
    ret = self.dll.ShamrockFilterReset(cdevice)
    return (ret)

  def ShamrockFlipperIsPresent(self, device):
    ''' 
        Description:
          Finds if Flipper is present.

        Synopsis:
          (ret, present) = ShamrockFlipperIsPresent(device)

        Inputs:
          device - Shamrock to interrogate

        Outputs:
          ret - Function Return Code:
            SHAMROCK_SUCCESS - Flipper presence flag returned
            SHAMROCK_NOT_INITIALIZED - Shamrock not initialized
            SHAMROCK_P1INVALID - Invalid device
            SHAMROCK_COMMUNICATION_ERROR - Unable to communicate with Shamrock
          present - pointer to flag::
            0 - Flipper is NOT present
            1 - Flipper IS present

        C++ Equiv:
          unsigned int ShamrockFlipperIsPresent(int device, int * present);

        See Also:
          ShamrockSetPort ShamrockGetPort ShamrockFlipperReset ShamrockGetCCDLimits 

    '''
    cdevice = c_int(device)
    cpresent = c_int()
    ret = self.dll.ShamrockFlipperIsPresent(cdevice, byref(cpresent))
    return (ret, cpresent.value)

  def ShamrockFlipperMirrorIsPresent(self, device, flipper):
    ''' 
        Description:
          Finds if Flipper is present.
          

        Synopsis:
          (ret, present) = ShamrockFlipperMirrorIsPresent(device, flipper)

        Inputs:
          device - Shamrock to interrogate
          flipper - The flipper can have two values which are as follows::
             SHAMROCK_INPUT_FLIPPER (1) - 
            SHAMROCK_OUTPUT_FLIPPER  (2) - 

        Outputs:
          ret - Function Return Code:
            SHAMROCK_SUCCESS - Flipper presence flag returned
            SHAMROCK_NOT_INITIALIZED - Shamrock not initialized
            SHAMROCK_P1INVALID - Invalid device
            SHAMROCK_P2INVALID - Invalid flipper
            SHAMROCK_P3INVALID - Invalid present
            SHAMROCK_COMMUNICATION_ERROR - Unable to communicate with Shamrock
          present -  pointer to flag:
            0 - Flipper is NOT present
            1 - Flipper is present

        C++ Equiv:
          unsigned int ShamrockFlipperMirrorIsPresent(int device, int flipper, int * present);

        See Also:
          ShamrockSetFlipperMirror ShamrockGetFlipperMirror ShamrockFlipperMirrorReset ShamrockGetCCDLimits 

    '''
    cdevice = c_int(device)
    cflipper = c_int(flipper)
    cpresent = c_int()
    ret = self.dll.ShamrockFlipperMirrorIsPresent(cdevice, cflipper, byref(cpresent))
    return (ret, cpresent.value)

  def ShamrockFlipperMirrorReset(self, device, flipper):
    ''' 
        Description:
          Resets the specified flipper to its default.
          

        Synopsis:
          ret = ShamrockFlipperMirrorReset(device, flipper)

        Inputs:
          device -  Shamrock to interrogate
          flipper - The flipper can have two values which are as follows::
             SHAMROCK_INPUT_FLIPPER (1) - 
            SHAMROCK_OUTPUT_FLIPPER ( 2) - 

        Outputs:
          ret - Function Return Code:
            SHAMROCK_SUCCESS - Flipper reset
            SHAMROCK_NOT_INITIALIZED - Shamrock not initialized
            SHAMROCK_P1INVALID - Invalid device
            SHAMROCK_P2INVALID - Invalid flipper
            SHAMROCK_COMMUNICATION_ERROR - Unable to communicate with Shamrock

        C++ Equiv:
          unsigned int ShamrockFlipperMirrorReset(int device, int flipper);

        See Also:
          ShamrockSetFlipperMirror ShamrockGetFlipperMirror ShamrockGetCCDLimits ShamrockFlipperMirrorIsPresent 

    '''
    cdevice = c_int(device)
    cflipper = c_int(flipper)
    ret = self.dll.ShamrockFlipperMirrorReset(cdevice, cflipper)
    return (ret)

  def ShamrockFlipperReset(self, device):
    ''' 
        Description:
          Resets the Flipper to its default.

        Synopsis:
          ret = ShamrockFlipperReset(device)

        Inputs:
          device - Shamrock to which reset the Flipper

        Outputs:
          ret - Function Return Code:
            SHAMROCK_SUCCESS - Flipper reset
            SHAMROCK_NOT_INITIALIZED - Shamrock not initialized
            SHAMROCK_P1INVALID - Invalid device
            SHAMROCK_COMMUNICATION_ERROR - Unable to communicate with Shamrock

        C++ Equiv:
          unsigned int ShamrockFlipperReset(int device);

        See Also:
          ShamrockSetPort ShamrockGetPort ShamrockGetCCDLimits ShamrockFlipperIsPresent 

    '''
    cdevice = c_int(device)
    ret = self.dll.ShamrockFlipperReset(cdevice)
    return (ret)

  def ShamrockFocusMirrorIsPresent(self, device):
    ''' 
        Description:
          Resets the filter to its default position.

        Synopsis:
          (ret, present) = ShamrockFocusMirrorIsPresent(device)

        Inputs:
          device - Shamrock to interrogate

        Outputs:
          ret - Function Return Code:
            SHAMROCK_SUCCESS - Focus Mirror presence flag returned
            SHAMROCK_NOT_INITIALIZED - Shamrock not initialized
            SHAMROCK_P1INVALID - Invalid device
            SHAMROCK_COMMUNICATION_ERROR - Unable to communicate with Shamrock
          present - pointer to flag: 
            0 Focus Mirror is NOT present
            1 Focus Mirror IS present

        C++ Equiv:
          unsigned int ShamrockFocusMirrorIsPresent(int device, int * present);

        See Also:
          ShamrockSetFocusMirror ShamrockGetFocusMirror ShamrockGetFocusMirrorMaxSteps ShamrockFocusMirrorIsPresent 

    '''
    cdevice = c_int(device)
    cpresent = c_int()
    ret = self.dll.ShamrockFocusMirrorIsPresent(cdevice, byref(cpresent))
    return (ret, cpresent.value)

  def ShamrockFocusMirrorReset(self, device):
    ''' 
        Description:
          Resets the filter to its default position.

        Synopsis:
          ret = ShamrockFocusMirrorReset(device)

        Inputs:
          device - Shamrock to reset the filter

        Outputs:
          ret - Function Return Code:
            SHAMROCK_SUCCESS - Focus Mirror reset
            SHAMROCK_NOT_INITIALIZED - Shamrock not initialized
            SHAMROCK_P1INVALID - Invalid device
            SHAMROCK_COMMUNICATION_ERROR - Unable to communicate with Shamrock

        C++ Equiv:
          unsigned int ShamrockFocusMirrorReset(int device);

        See Also:
          ShamrockSetFocusMirror ShamrockGetFocusMirror ShamrockGetFocusMirrorMaxSteps ShamrockFocusMirrorIsPresent 

    '''
    cdevice = c_int(device)
    ret = self.dll.ShamrockFocusMirrorReset(cdevice)
    return (ret)

  def ShamrockGetAccessoryState(self, device, Accessory):
    ''' 
        Description:
          Gets the Accessory state.

        Synopsis:
          (ret, state) = ShamrockGetAccessoryState(device, Accessory)

        Inputs:
          device - Shamrock to interrogate
          Accessory - line to interrogate::
            1 - line 1
            2 - line 2

        Outputs:
          ret - Function Return Code:
            SHAMROCK_SUCCESS - Line state returned
            SHAMROCK_NOT_INITIALIZED - Shamrock not initialized
            SHAMROCK_P1INVALID - Invalid device
            SHAMROCK_P2INVALID - Invalid line
            SHAMROCK_COMMUNICATION_ERROR - Unable to communicate with Shamrock
          state - pointer to line state::
            0 - OFF
            1 - ON

        C++ Equiv:
          unsigned int ShamrockGetAccessoryState(int device, int Accessory, int * state);

        See Also:
          ShamrockSetAccessory ShamrockAccessoryIsPresent 

    '''
    cdevice = c_int(device)
    cAccessory = c_int(Accessory)
    cstate = c_int()
    ret = self.dll.ShamrockGetAccessoryState(cdevice, cAccessory, byref(cstate))
    return (ret, cstate.value)

  def ShamrockGetAutoSlitCoefficients(self, device, index):
    ''' 
        Description:
          Gets the auto slit coefficients used by the Shamrock

        Synopsis:
          (ret, x1, y1, x2, y2) = ShamrockGetAutoSlitCoefficients(device, index)

        Inputs:
          device - Shamrock to interrogate
          index - Slit

        Outputs:
          ret - Function Return Code:
            SHAMROCK_SUCCESS - Coefficients successfully returned
            SHAMROCK_NOT_INITIALIZED - SDK not initialised
            SHAMROCK_P1INVALID - Invalid Device
            SHAMROCK_P2INVALID - Slit is not side input slit side
            SHAMROCK_COMMUNICATION_ERROR - Error communicating with shamrock
          x1 - first coordinate x value
          y1 - first coordinate y value
          x2 - second coordinate x value
          y2 - second coordinate y value

        C++ Equiv:
          unsigned int ShamrockGetAutoSlitCoefficients(int device, int index, int & x1, int & y1, int & x2, int & y2);

        See Also:
          ShamrockSetAutoSlitCoefficients 

    '''
    cdevice = c_int(device)
    cindex = c_int(index)
    cx1 = c_int()
    cy1 = c_int()
    cx2 = c_int()
    cy2 = c_int()
    ret = self.dll.ShamrockGetAutoSlitCoefficients(cdevice, cindex, byref(cx1), byref(cy1), byref(cx2), byref(cy2))
    return (ret, cx1.value, cy1.value, cx2.value, cy2.value)

  def ShamrockGetAutoSlitWidth(self, device, index):
    ''' 
        Description:
          Returns the specified Slit width.
          

        Synopsis:
          (ret, width) = ShamrockGetAutoSlitWidth(device, index)

        Inputs:
          device - Shamrock to interrogate
          index - Specifies which slit to get the width of.:
             SHAMROCK_INPUT_SLIT_SIDE (1) - 
            SHAMROCK_INPUT_SLIT_DIRECT (2) - 
             SHAMROCK_INPUT_SLIT_SIDE (3) - 
             SHAMROCK_INPUT_SLIT_DIRECT (4) - 

        Outputs:
          ret - Function Return Code:
            SHAMROCK_SUCCESS - Output Slit width returned
            SHAMROCK_NOT_INITIALIZED - Shamrock not initialized
            SHAMROCK_P1INVALID - Invalid device
            SHAMROCK_P2INVALID - Invalid slit index
            SHAMROCK_P3INVALID - Invalid width
            SHAMROCK_COMMUNICATION_ERROR - Unable to communicate with Shamrock
          width - pointer to the Output Slit width (um)

        C++ Equiv:
          unsigned int ShamrockGetAutoSlitWidth(int device, int index, float * width);

        See Also:
          ShamrockAutoSlitIsPresent ShamrockSetAutoSlitWidth ShamrockAutoSlitReset 

    '''
    cdevice = c_int(device)
    cindex = c_int(index)
    cwidth = c_float()
    ret = self.dll.ShamrockGetAutoSlitWidth(cdevice, cindex, byref(cwidth))
    return (ret, cwidth.value)

  def ShamrockGetCalibration(self, device, NumberPixels):
    ''' 
        Description:
          Obtains the wavelength calibration of each pixel of attached sensor.

        Synopsis:
          (ret, CalibrationValues) = ShamrockGetCalibration(device, NumberPixels)

        Inputs:
          device - Select Shamrock to control
          NumberPixels - number of pixels of attached sensor

        Outputs:
          ret - Function Return Code:
            SHAMROCK_SUCCESS - port set
            SHAMROCK_NOT_INITIALIZED - Shamrock not initialized
            SHAMROCK_P1INVALID - Invalid device
            SHAMROCK_P3INVALID - Invalid number
            SHAMROCK_COMMUNICATION_ERROR - Unable to communicate with Shamrock
          CalibrationValues - wavelength calibration of each pixel of attached sensor

        C++ Equiv:
          unsigned int ShamrockGetCalibration(int device, float * CalibrationValues, int NumberPixels);

        See Also:
          ShamrockGetPixelWidth ShamrockSetPixelWidth ShamrockGetNumberPixels ShamrockSetNumberPixels 

    '''
    cdevice = c_int(device)
    cCalibrationValues = (c_float * NumberPixels)()
    cNumberPixels = c_int(NumberPixels)
    ret = self.dll.ShamrockGetCalibration(cdevice, cCalibrationValues, cNumberPixels)
    return (ret, cCalibrationValues)

  def ShamrockGetCCDLimits(self, device, port):
    ''' 
        Description:
          Gets the upper and lower accessible wavelength through the port.

        Synopsis:
          (ret, Low, High) = ShamrockGetCCDLimits(device, port)

        Inputs:
          device - Shamrock to interrogate
          port - port to interrogate:
            1 - port 1
            2 - port 2

        Outputs:
          ret - Function Return Code:
            SHAMROCK_SUCCESS - Accessible wavelength limits returned
            SHAMROCK_NOT_INITIALIZED - Shamrock not initialized
            SHAMROCK_P1INVALID - Invalid device
            SHAMROCK_P2INVALID - Invalid port
            SHAMROCK_COMMUNICATION_ERROR - Unable to communicate with Shamrock
          Low - pointer to lower accessible wavelength (nm)
          High - pointer to upper accessible wavelength (nm)

        C++ Equiv:
          unsigned int ShamrockGetCCDLimits(int device, int port, float * Low, float * High);

        See Also:
          ShamrockFlipperIsPresent ShamrockGetPort ShamrockSetPort ShamrockFlipperReset 

    '''
    cdevice = c_int(device)
    cport = c_int(port)
    cLow = c_float()
    cHigh = c_float()
    ret = self.dll.ShamrockGetCCDLimits(cdevice, cport, byref(cLow), byref(cHigh))
    return (ret, cLow.value, cHigh.value)

  def ShamrockGetDetectorOffset(self, device):
    ''' 
        Description:
          Gets the detector offset.

        Synopsis:
          (ret, offset) = ShamrockGetDetectorOffset(device)

        Inputs:
          device - Shamrock to interrogate

        Outputs:
          ret - Function Return Code:
            SHAMROCK_SUCCESS - Detector offset returned
            SHAMROCK_NOT_INITIALIZED - Shamrock not initialized
            SHAMROCK_P1INVALID - Invalid device
            SHAMROCK_COMMUNICATION_ERROR - Unable to communicate with Shamrock
          offset - pointer to detector offset (steps)

        C++ Equiv:
          unsigned int ShamrockGetDetectorOffset(int device, int * offset);

        See Also:
          ShamrockGratingIsPresent ShamrockGetTurret ShamrockGetNumberGratings ShamrockGetGrating ShamrockGetGratingInfo ShamrockGetGratingOffset ShamrockSetTurret ShamrockSetGrating ShamrockWavelengthReset ShamrockSetGratingOffset ShamrockSetDetectorOffset 

    '''
    cdevice = c_int(device)
    coffset = c_int()
    ret = self.dll.ShamrockGetDetectorOffset(cdevice, byref(coffset))
    return (ret, coffset.value)

  def ShamrockGetDetectorOffsetEx(self, device, entrancePort, exitPort):
    ''' 
        Description:
          Sets the detector offset. Use this function if the system has 4 ports and a detector offset value of a specific entrance and exit port combination is required.
          DIRECT, DIRECT = 0, 0
          DIRECT, SIDE = 0, 1
          SIDE, DIRECT = 1, 0
          SIDE, SIDE = 1, 1

        Synopsis:
          (ret, offset) = ShamrockGetDetectorOffsetEx(device, entrancePort, exitPort)

        Inputs:
          device - Shamrock to interrogate
          entrancePort - Select entrance port to use
          exitPort - Select exit port to use

        Outputs:
          ret - Function Return Code:
            SHAMROCK_SUCCESS - Detector offset set
            SHAMROCK_NOT_INITIALIZED - Shamrock not initialized
            SHAMROCK_P1INVALID - Invalid device
            SHAMROCK_COMMUNICATION_ERROR - Unable to communicate with Shamrock
          offset - pointer to detector offset (steps)

        C++ Equiv:
          unsigned int ShamrockGetDetectorOffsetEx(int device, int entrancePort, int exitPort, int * offset);

        See Also:
          ShamrockGratingIsPresent ShamrockGetTurret ShamrockGetNumberGratings ShamrockGetGrating ShamrockGetGratingInfo ShamrockGetGratingOffset ShamrockGetDetectorOffset ShamrockSetDetectorOffsetEx ShamrockSetDetectorOffset ShamrockSetTurret ShamrockSetGrating ShamrockWavelengthReset ShamrockSetGratingOffset 

    '''
    cdevice = c_int(device)
    centrancePort = c_int(entrancePort)
    cexitPort = c_int(exitPort)
    coffset = c_int()
    ret = self.dll.ShamrockGetDetectorOffsetEx(cdevice, centrancePort, cexitPort, byref(coffset))
    return (ret, coffset.value)

  def ShamrockGetDetectorOffsetPort2(self, device):
    ''' 
        Description:
          

        Synopsis:
          (ret, offset) = ShamrockGetDetectorOffsetPort2(device)

        Inputs:
          device - 

        Outputs:
          ret - Function Return Code
          offset - 

        C++ Equiv:
          unsigned int ShamrockGetDetectorOffsetPort2(int device, int * offset);

        See Also:
          ShamrockSetDetectorOffsetPort2 

    '''
    cdevice = c_int(device)
    coffset = c_int()
    ret = self.dll.ShamrockGetDetectorOffsetPort2(cdevice, byref(coffset))
    return (ret, coffset.value)

  def ShamrockGetFilter(self, device):
    ''' 
        Description:
          Gets current Filter.

        Synopsis:
          (ret, filter) = ShamrockGetFilter(device)

        Inputs:
          device - Shamrock to interrogate

        Outputs:
          ret - Function Return Code:
            SHAMROCK_SUCCESS - Filter returned
            SHAMROCK_NOT_INITIALIZED - Shamrock not initialized
            SHAMROCK_P1INVALID - Invalid device
            SHAMROCK_COMMUNICATION_ERROR - Unable to communicate with Shamrock
          filter - pointer to Filter

        C++ Equiv:
          unsigned int ShamrockGetFilter(int device, int * filter);

        See Also:
          ShamrockFilterIsPresent ShamrockGetFilterInfo ShamrockSetFilter ShamrockSetFilterInfo 

    '''
    cdevice = c_int(device)
    cfilter = c_int()
    ret = self.dll.ShamrockGetFilter(cdevice, byref(cfilter))
    return (ret, cfilter.value)

  def ShamrockGetFilterInfo(self, device, Filter):
    ''' 
        Description:
          Gets the filter information.

        Synopsis:
          (ret, Info) = ShamrockGetFilterInfo(device, Filter)

        Inputs:
          device - Shamrock to interrogate
          Filter - Filter to interrogate

        Outputs:
          ret - Function Return Code:
            SHAMROCK_SUCCESS - Filter information returned
            SHAMROCK_NOT_INITIALIZED - Shamrock not initialized
            SHAMROCK_P1INVALID - Invalid device
            SHAMROCK_P2INVALID - Invalid filter
            SHAMROCK_COMMUNICATION_ERROR - Unable to communicate with Shamrock
          Info - pointer to the filter information

        C++ Equiv:
          unsigned int ShamrockGetFilterInfo(int device, int Filter, char * Info);

        See Also:
          ShamrockFilterIsPresent ShamrockGetFilter ShamrockSetFilter ShamrockSetFilterInfo 

    '''
    cdevice = c_int(device)
    cFilter = c_int(Filter)
    cInfo = create_string_buffer(MAX_PATH)
    ret = self.dll.ShamrockGetFilterInfo(cdevice, cFilter, cInfo)
    return (ret, cInfo.value)

  def ShamrockGetFlipperMirror(self, device, flipper):
    ''' 
        Description:
          Returns the current port for the specified flipper mirror.
          

        Synopsis:
          (ret, port) = ShamrockGetFlipperMirror(device, flipper)

        Inputs:
          device - Shamrock to interrogate
          flipper - The flipper can have two values which are as follows:
            :
            SHAMROCK_INPUT_FLIPPER - 1
            SHAMROCK_OUTPUT_FLIPPER - 2

        Outputs:
          ret - Function Return Code:
            SHAMROCK_SUCCESS - port returned
            SHAMROCK_NOT_INITIALIZED - Shamrock not initialized
            SHAMROCK_P1INVALID - Invalid device
            SHAMROCK_COMMUNICATION_ERROR - Unable to communicate with Shamrock
          port - pointer to the current port:
            SHAMROCK_DIRECT_PORT - 0
            SHAMROCK_SIDE_PORT - 1

        C++ Equiv:
          unsigned int ShamrockGetFlipperMirror(int device, int flipper, int * port);

        See Also:
          ShamrockFlipperMirrorIsPresent ShamrockGetCCDLimits ShamrockSetFlipperMirror ShamrockFlipperMirrorReset 

    '''
    cdevice = c_int(device)
    cflipper = c_int(flipper)
    cport = c_int()
    ret = self.dll.ShamrockGetFlipperMirror(cdevice, cflipper, byref(cport))
    return (ret, cport.value)

  def ShamrockGetFlipperMirrorMaxPosition(self, device, flipper):
    ''' 
        Description:
          Returns the maximum position for the specified flipper mirror.

        Synopsis:
          (ret, position) = ShamrockGetFlipperMirrorMaxPosition(device, flipper)

        Inputs:
          device - Shamrock to interrogate
          flipper - The flipper can have two values which are as follows:
            SHAMROCK_INPUT_FLIPPER 1
            SHAMROCK_OUTPUT_FLIPPER 2

        Outputs:
          ret - Function Return Code:
            SHAMROCK_SUCCESS - position returned
            SHAMROCK_NOT_INITIALIZED - Shamrock not initialized
            SHAMROCK_P1INVALID - Invalid device
            SHAMROCK_COMMUNICATION_ERROR - Unable to communicate with Shamrock
          position - pointer to the maximum flipper mirror position

        C++ Equiv:
          unsigned int ShamrockGetFlipperMirrorMaxPosition(int device, int flipper, int * position);

        See Also:
          ShamrockFlipperMirrorIsPresent ShamrockGetFlipperMirrorPosition ShamrockSetFlipperMirrorPosition ShamrockFlipperMirrorReset 

    '''
    cdevice = c_int(device)
    cflipper = c_int(flipper)
    cposition = c_int()
    ret = self.dll.ShamrockGetFlipperMirrorMaxPosition(cdevice, cflipper, byref(cposition))
    return (ret, cposition.value)

  def ShamrockGetFlipperMirrorPosition(self, device , flipper):
    ''' 
        Description:
          Returns the current position for the specified flipper mirror.

        Synopsis:
          (ret, position) = ShamrockGetFlipperMirrorPosition(device , flipper)

        Inputs:
          device  - Shamrock to interrogate
          flipper - The flipper can have two values which are as follows:
            SHAMROCK_INPUT_FLIPPER 1
            SHAMROCK_OUTPUT_FLIPPER 2

        Outputs:
          ret - Function Return Code:
            SHAMROCK_SUCCESS - position returned
            SHAMROCK_NOT_INITIALIZED - Shamrock not initialized
            SHAMROCK_P1INVALID - Invalid device
            SHAMROCK_COMMUNICATION_ERROR - Unable to communicate with Shamrock
          position - pointer to the current flipper mirror position

        C++ Equiv:
          unsigned int ShamrockGetFlipperMirrorPosition(int device , int flipper, int * position);

        See Also:
          ShamrockFlipperMirrorIsPresent ShamrockGetFlipperMirrorMaxPosition ShamrockSetFlipperMirrorPosition ShamrockFlipperMirrorReset 

    '''
    cdevice  = c_int(device )
    cflipper = c_int(flipper)
    cposition = c_int()
    ret = self.dll.ShamrockGetFlipperMirrorPosition(cdevice , cflipper, byref(cposition))
    return (ret, cposition.value)

  def ShamrockGetFocusMirror(self, device):
    ''' 
        Description:
          Gets current focus position in steps.

        Synopsis:
          (ret, focus) = ShamrockGetFocusMirror(device)

        Inputs:
          device - Shamrock to interrogate

        Outputs:
          ret - Function Return Code:
            SHAMROCK_SUCCESS - Current focus position returned
            SHAMROCK_NOT_INITIALIZED - Shamrock not initialized
            SHAMROCK_P1INVALID - Invalid device
            SHAMROCK_COMMUNICATION_ERROR - Unable to communicate with Shamrock
          focus - pointer to focus 

        C++ Equiv:
          unsigned int ShamrockGetFocusMirror(int device, int * focus);

        See Also:
          ShamrockSetFocusMirror ShamrockGetFocusMirrorMaxSteps ShamrockFocusMirrorReset ShamrockFocusMirrorIsPresent 

    '''
    cdevice = c_int(device)
    cfocus = c_int()
    ret = self.dll.ShamrockGetFocusMirror(cdevice, byref(cfocus))
    return (ret, cfocus.value)

  def ShamrockGetFocusMirrorMaxSteps(self, device):
    ''' 
        Description:
          Gets maximum possible focus position in steps.

        Synopsis:
          (ret, steps) = ShamrockGetFocusMirrorMaxSteps(device)

        Inputs:
          device - Shamrock to interrogate

        Outputs:
          ret - Function Return Code:
            SHAMROCK_SUCCESS - Max focus position returned
            SHAMROCK_NOT_INITIALIZED - Shamrock not initialized
            SHAMROCK_P1INVALID - Invalid device
            SHAMROCK_COMMUNICATION_ERROR - Unable to communicate with Shamrock
          steps - pointer to steps

        C++ Equiv:
          unsigned int ShamrockGetFocusMirrorMaxSteps(int device, int * steps);

        See Also:
          ShamrockSetFocusMirror ShamrockGetFocusMirror ShamrockFocusMirrorReset ShamrockFocusMirrorIsPresent 

    '''
    cdevice = c_int(device)
    csteps = c_int()
    ret = self.dll.ShamrockGetFocusMirrorMaxSteps(cdevice, byref(csteps))
    return (ret, csteps.value)

  def ShamrockGetFunctionReturnDescription(self, error, MaxDescStrLen):
    ''' 
        Description:
          Returns a short description of an Error Code.

        Synopsis:
          (ret, description) = ShamrockGetFunctionReturnDescription(error, MaxDescStrLen)

        Inputs:
          error - Error Code to identify
          MaxDescStrLen - number of char allocated for the description string

        Outputs:
          ret - Function Return Code:
            SHAMROCK_SUCCESS - Error Code description returned
            SHAMROCK_P3INVALID - Invalid MaxDescStrLen
          description - pointer to the Error Code description

        C++ Equiv:
          unsigned int ShamrockGetFunctionReturnDescription(int error, char * description, int MaxDescStrLen);

        See Also:
          ShamrockInitialize ShamrockGetNumberDevices ShamrockClose 

        Note: Returns a short description of an Error Code.

    '''
    cerror = c_int(error)
    cdescription = create_string_buffer(MaxDescStrLen)
    cMaxDescStrLen = c_int(MaxDescStrLen)
    ret = self.dll.ShamrockGetFunctionReturnDescription(cerror, cdescription, cMaxDescStrLen)
    return (ret, cdescription.value)

  def ShamrockGetGrating(self, device):
    ''' 
        Description:
          Returns the current grating.

        Synopsis:
          (ret, grating) = ShamrockGetGrating(device)

        Inputs:
          device - Shamrock to interrogate

        Outputs:
          ret - Function Return Code:
            SHAMROCK_SUCCESS - grating returned
            SHAMROCK_NOT_INITIALIZED - Shamrock not initialized
            SHAMROCK_P1INVALID - Invalid device
            SHAMROCK_COMMUNICATION_ERROR - Unable to communicate with Shamrock
          grating - pointer to grating

        C++ Equiv:
          unsigned int ShamrockGetGrating(int device, int * grating);

        See Also:
          ShamrockGratingIsPresent ShamrockGetTurret ShamrockGetNumberGratings ShamrockGetGratingInfo ShamrockGetGratingOffset ShamrockGetDetectorOffset ShamrockSetTurret ShamrockSetGrating ShamrockWavelengthReset ShamrockSetGratingOffset ShamrockSetDetectorOffset 

    '''
    cdevice = c_int(device)
    cgrating = c_int()
    ret = self.dll.ShamrockGetGrating(cdevice, byref(cgrating))
    return (ret, cgrating.value)

  def ShamrockGetGratingInfo(self, device, Grating):
    ''' 
        Description:
          Returns the grating information

        Synopsis:
          (ret, Lines, Blaze, Home, Offset) = ShamrockGetGratingInfo(device, Grating)

        Inputs:
          device - Shamrock to interrogate
          Grating - grating to interrogate

        Outputs:
          ret - Function Return Code:
            SHAMROCK_SUCCESS - grating information returned
            SHAMROCK_NOT_INITIALIZED - Shamrock not initialized
            SHAMROCK_P1INVALID - Invalid device
            SHAMROCK_P2INVALID - Invalid grating
            SHAMROCK_COMMUNICATION_ERROR - Unable to communicate with Shamrock
          Lines - pointer to the grating lines/mm
          Blaze - pointer to the grating blaze wavelength (nm)
          Home - pointer to the grating home (steps)
          Offset - pointer to the grating offset (steps)

        C++ Equiv:
          unsigned int ShamrockGetGratingInfo(int device, int Grating, float * Lines, char * Blaze, int * Home, int * Offset);

        See Also:
          ShamrockGratingIsPresent ShamrockGetTurret ShamrockGetNumberGratings ShamrockGetGrating ShamrockGetGratingOffset ShamrockGetDetectorOffset ShamrockSetTurret ShamrockSetGrating ShamrockWavelengthReset ShamrockSetGratingOffset ShamrockSetDetectorOffset 

    '''
    cdevice = c_int(device)
    cGrating = c_int(Grating)
    cLines = c_float()
    cBlaze = create_string_buffer(MAX_PATH)
    cHome = c_int()
    cOffset = c_int()
    ret = self.dll.ShamrockGetGratingInfo(cdevice, cGrating, byref(cLines), cBlaze, byref(cHome), byref(cOffset))
    return (ret, cLines.value, cBlaze.value, cHome.value, cOffset.value)

  def ShamrockGetGratingOffset(self, device, Grating):
    ''' 
        Description:
          Returns the grating offset

        Synopsis:
          (ret, offset) = ShamrockGetGratingOffset(device, Grating)

        Inputs:
          device - Shamrock to interrogate
          Grating - grating to interrogate

        Outputs:
          ret - Function Return Code:
            SHAMROCK_SUCCESS - grating offset returned
            SHAMROCK_NOT_INITIALIZED - Shamrock not initialized
            SHAMROCK_P1INVALID - Invalid device
            SHAMROCK_P2INVALID - Invalid grating
            SHAMROCK_COMMUNICATION_ERROR - Unable to communicate with Shamrock
          offset - pointer to the grating offset (steps)

        C++ Equiv:
          unsigned int ShamrockGetGratingOffset(int device, int Grating, int * offset);

        See Also:
          ShamrockGratingIsPresent ShamrockGetTurret ShamrockGetNumberGratings ShamrockGetGrating ShamrockGetGratingInfo ShamrockGetDetectorOffset ShamrockSetTurret ShamrockSetGrating ShamrockWavelengthReset ShamrockSetGratingOffset ShamrockSetDetectorOffset 

    '''
    cdevice = c_int(device)
    cGrating = c_int(Grating)
    coffset = c_int()
    ret = self.dll.ShamrockGetGratingOffset(cdevice, cGrating, byref(coffset))
    return (ret, coffset.value)

  def ShamrockGetIris(self, device, iris):
    ''' 
        Description:
          Gets iris position for the specified iris port. Value will be in the range 0 to 100.

        Synopsis:
          (ret, value) = ShamrockGetIris(device, iris)

        Inputs:
          device - Shamrock to interrogate
          iris - Iris to query: Direct=0; Side=1

        Outputs:
          ret - Function Return Code:
            SHAMROCK_SUCCESS - Current focus position returned
            SHAMROCK_NOT_INITIALIZED - Shamrock not initialized
            SHAMROCK_P1INVALID - Invalid device
            SHAMROCK_P2INVALID - Invalid iris specified.
            SHAMROCK_P3INVALID - Value pointer is null
            SHAMROCK_NOT_AVAILABLE - No iris at specified index
            SHAMROCK_COMMUNICATION_ERROR - Unable to communicate with Shamrock
          value - pointer to an int to store the position of the iris, in the range 0-100

        C++ Equiv:
          unsigned int ShamrockGetIris(int device, int iris, int * value);

        See Also:
          ShamrockSetIris ShamrockIsIrisPresent 

    '''
    cdevice = c_int(device)
    ciris = c_int(iris)
    cvalue = c_int()
    ret = self.dll.ShamrockGetIris(cdevice, ciris, byref(cvalue))
    return (ret, cvalue.value)

  def ShamrockGetNumberDevices(self):
    ''' 
        Description:
          Returns the number of available Shamrocks.

        Synopsis:
          (ret, nodevices) = ShamrockGetNumberDevices()

        Inputs:
          None

        Outputs:
          ret - Function Return Code:
            SHAMROCK_SUCCESS - Number of available Shamrocks returned
            SHAMROCK_NOT_INITIALIZED - Shamrock not initialized
          nodevices - pointer to the number of available Shamrocks

        C++ Equiv:
          unsigned int ShamrockGetNumberDevices(int * nodevices);

        See Also:
          ShamrockInitialize ShamrockGetFunctionReturnDescription ShamrockClose 

    '''
    cnodevices = c_int()
    ret = self.dll.ShamrockGetNumberDevices(byref(cnodevices))
    return (ret, cnodevices.value)

  def ShamrockGetNumberGratings(self, device):
    ''' 
        Description:
          Returns the number of available gratings.

        Synopsis:
          (ret, noGratings) = ShamrockGetNumberGratings(device)

        Inputs:
          device - Shamrock to interrogate

        Outputs:
          ret - Function Return Code:
            SHAMROCK_SUCCESS - number of available gratings returned
            SHAMROCK_NOT_INITIALIZED - Shamrock not initialized
            SHAMROCK_P1INVALID - Invalid device
            SHAMROCK_COMMUNICATION_ERROR - Unable to communicate with Shamrock
          noGratings - pointer to the number of available gratings

        C++ Equiv:
          unsigned int ShamrockGetNumberGratings(int device, int * noGratings);

        See Also:
          ShamrockGratingIsPresent ShamrockGetTurret ShamrockGetGrating ShamrockGetGratingInfo ShamrockGetGratingOffset ShamrockGetDetectorOffset ShamrockSetTurret ShamrockSetGrating ShamrockWavelengthReset ShamrockSetGratingOffset ShamrockSetDetectorOffset 

    '''
    cdevice = c_int(device)
    cnoGratings = c_int()
    ret = self.dll.ShamrockGetNumberGratings(cdevice, byref(cnoGratings))
    return (ret, cnoGratings.value)

  def ShamrockGetNumberPixels(self, device):
    ''' 
        Description:
          Gets the number of pixels of the attached sensor.

        Synopsis:
          (ret, NumberPixels) = ShamrockGetNumberPixels(device)

        Inputs:
          device - Select Shamrock to control

        Outputs:
          ret - Function Return Code:
            SHAMROCK_SUCCESS - port set
            SHAMROCK_NOT_INITIALIZED - Shamrock not initialized
            SHAMROCK_P1INVALID - Invalid device
            SHAMROCK_COMMUNICATION_ERROR - Unable to communicate with Shamrock
          NumberPixels - number of pixels of attached sensor

        C++ Equiv:
          unsigned int ShamrockGetNumberPixels(int device, int * NumberPixels);

        See Also:
          ShamrockGetPixelWidth ShamrockSetPixelWidth ShamrockSetNumberPixels ShamrockGetCalibration 

    '''
    cdevice = c_int(device)
    cNumberPixels = c_int()
    ret = self.dll.ShamrockGetNumberPixels(cdevice, byref(cNumberPixels))
    return (ret, cNumberPixels.value)

  def ShamrockGetOutputSlit(self, device):
    ''' 
        Description:
          Returns the Output Slit width.

        Synopsis:
          (ret, width) = ShamrockGetOutputSlit(device)

        Inputs:
          device - Shamrock to interrogate

        Outputs:
          ret - Function Return Code:
            SHAMROCK_SUCCESS - Output Slit width returned
            SHAMROCK_NOT_INITIALIZED - Shamrock not initialized
            SHAMROCK_P1INVALID - Invalid device
            SHAMROCK_COMMUNICATION_ERROR - Unable to communicate with Shamrock
          width - pointer to the Output Slit width (m)

        C++ Equiv:
          unsigned int ShamrockGetOutputSlit(int device, float * width);

        See Also:
          ShamrockOutputSlitIsPresent ShamrockGetOutputSlit ShamrockSetOutputSlit ShamrockOutputSlitReset 

    '''
    cdevice = c_int(device)
    cwidth = c_float()
    ret = self.dll.ShamrockGetOutputSlit(cdevice, byref(cwidth))
    return (ret, cwidth.value)

  def ShamrockGetPixelCalibrationCoefficients(self, device):
    ''' 
        Description:
          Gets pixel calibration coefficients.

        Synopsis:
          (ret, A, B, C, D) = ShamrockGetPixelCalibrationCoefficients(device)

        Inputs:
          device - Shamrock to interrogate

        Outputs:
          ret - Function Return Code:
            SHAMROCK_SUCCESS - Constants returned
            SHAMROCK_NOT_INITIALIZED - Shamrock not initialized
            SHAMROCK_P1INVALID - Invalid device
            SHAMROCK_P2INVALID - Pointer is NULL
            SHAMROCK_P3INVALID - Pointer is NULL
            SHAMROCK_P4INVALID - Pointer is NULL
            SHAMROCK_P5INVALID - Pointer is NULL
            SHAMROCK_COMMUNICATION_ERROR - Unable to communicate with Shamrock
          A - pointer to constant 1
          B - pointer to constant 2
          C - pointer to constant 3
          D - pointer to constant 4

        C++ Equiv:
          unsigned int ShamrockGetPixelCalibrationCoefficients(int device, float * A, float * B, float * C, float * D);

        See Also:
          ShamrockGetPixelWidth ShamrockSetGratingOffset ShamrockGetNumberPixels ShamrockGetCalibration 

    '''
    cdevice = c_int(device)
    cA = c_float()
    cB = c_float()
    cC = c_float()
    cD = c_float()
    ret = self.dll.ShamrockGetPixelCalibrationCoefficients(cdevice, byref(cA), byref(cB), byref(cC), byref(cD))
    return (ret, cA.value, cB.value, cC.value, cD.value)

  def ShamrockGetPixelWidth(self, device):
    ''' 
        Description:
          Gets the current value of the pixel width in microns of the attached sensor.

        Synopsis:
          (ret, Width) = ShamrockGetPixelWidth(device)

        Inputs:
          device - Select Shamrock to control

        Outputs:
          ret - Function Return Code:
            SHAMROCK_SUCCESS - Pixel width returned
            SHAMROCK_NOT_INITIALIZED - Shamrock not initialized
            SHAMROCK_P1INVALID - Invalid device
            SHAMROCK_COMMUNICATION_ERROR - Unable to communicate with Shamrock
          Width - current pixel width of attached sensor

        C++ Equiv:
          unsigned int ShamrockGetPixelWidth(int device, float * Width);

        See Also:
          ShamrockSetPixelWidth ShamrockGetNumberPixels ShamrockSetNumberPixels ShamrockGetCalibration 

    '''
    cdevice = c_int(device)
    cWidth = c_float()
    ret = self.dll.ShamrockGetPixelWidth(cdevice, byref(cWidth))
    return (ret, cWidth.value)

  def ShamrockGetPort(self, device):
    ''' 
        Description:
          Returns the current port.

        Synopsis:
          (ret, port) = ShamrockGetPort(device)

        Inputs:
          device - Shamrock to interrogate

        Outputs:
          ret - Function Return Code:
            SHAMROCK_SUCCESS - port returned
            SHAMROCK_NOT_INITIALIZED - Shamrock not initialized
            SHAMROCK_P1INVALID - Invalid device
            SHAMROCK_COMMUNICATION_ERROR - Unable to communicate with Shamrock
          port - pointer to the current port

        C++ Equiv:
          unsigned int ShamrockGetPort(int device, int * port);

        See Also:
          ShamrockFlipperIsPresent ShamrockGetCCDLimits ShamrockSetPort ShamrockFlipperReset 

    '''
    cdevice = c_int(device)
    cport = c_int()
    ret = self.dll.ShamrockGetPort(cdevice, byref(cport))
    return (ret, cport.value)

  def ShamrockGetSerialNumber(self, device):
    ''' 
        Description:
          Returns the device serial number.

        Synopsis:
          (ret, serial) = ShamrockGetSerialNumber(device)

        Inputs:
          device - Shamrock to interrogate

        Outputs:
          ret - Function Return Code:
            SHAMROCK_SUCCESS - serial number returned
            SHAMROCK_NOT_INITIALIZED - Shamrock not initialized
            SHAMROCK_P1INVALID - Invalid device
            SHAMROCK_COMMUNICATION_ERROR - Unable to communicate with Shamrock
          serial - pointer to the device serial number

        C++ Equiv:
          unsigned int ShamrockGetSerialNumber(int device, char * serial);

        See Also:
          ShamrockEepromGetOpticalParams 

    '''
    cdevice = c_int(device)
    cserial = create_string_buffer(MAX_PATH)
    ret = self.dll.ShamrockGetSerialNumber(cdevice, cserial)
    return (ret, cserial.value)

  def ShamrockGetShutter(self, device):
    ''' 
        Description:
          Returns the current device shutter mode.

        Synopsis:
          (ret, mode) = ShamrockGetShutter(device)

        Inputs:
          device - Shamrock to interrogate

        Outputs:
          ret - Function Return Code:
            SHAMROCK_SUCCESS - device shutter mode returned
            SHAMROCK_NOT_INITIALIZED - Shamrock not initialized
            SHAMROCK_P1INVALID - Invalid device
            SHAMROCK_COMMUNICATION_ERROR - Unable to communicate with Shamrock
          mode - pointer to the device shutter mode:
            -1 - Shutter not set yet
            0 - Closed
            1 - Open

        C++ Equiv:
          unsigned int ShamrockGetShutter(int device, int * mode);

        See Also:
          ShamrockShutterIsPresent ShamrockSetShutter ShamrockIsModePossible 

    '''
    cdevice = c_int(device)
    cmode = c_int()
    ret = self.dll.ShamrockGetShutter(cdevice, byref(cmode))
    return (ret, cmode.value)

  def ShamrockGetSlit(self, device):
    ''' 
        Description:
          Returns the Input Slit width.

        Synopsis:
          (ret, width) = ShamrockGetSlit(device)

        Inputs:
          device - Shamrock to interrogate

        Outputs:
          ret - Function Return Code:
            SHAMROCK_SUCCESS - Input Slit width returned
            SHAMROCK_NOT_INITIALIZED - Shamrock not initialized
            SHAMROCK_P1INVALID - Invalid device
            SHAMROCK_COMMUNICATION_ERROR - Unable to communicate with Shamrock
          width - pointer to the Input Slit width (m)

        C++ Equiv:
          unsigned int ShamrockGetSlit(int device, float * width);

        See Also:
          ShamrockSlitIsPresent ShamrockSetSlit ShamrockSlitReset 

    '''
    cdevice = c_int(device)
    cwidth = c_float()
    ret = self.dll.ShamrockGetSlit(cdevice, byref(cwidth))
    return (ret, cwidth.value)

  def ShamrockGetSlitCoefficients(self, device):
    ''' 
        Description:
          

        Synopsis:
          (ret, x1, y1, x2, y2) = ShamrockGetSlitCoefficients(device)

        Inputs:
          device - 

        Outputs:
          ret - Function Return Code
          x1 - 
          y1 - 
          x2 - 
          y2 - 

        C++ Equiv:
          unsigned int ShamrockGetSlitCoefficients(int device, int & x1, int & y1, int & x2, int & y2);

    '''
    cdevice = c_int(device)
    cx1 = c_int()
    cy1 = c_int()
    cx2 = c_int()
    cy2 = c_int()
    ret = self.dll.ShamrockGetSlitCoefficients(cdevice, byref(cx1), byref(cy1), byref(cx2), byref(cy2))
    return (ret, cx1.value, cy1.value, cx2.value, cy2.value)

  def ShamrockGetSlitZeroPosition(self, device, index):
    ''' 
        Description:
          Gets the zero position for the slit at the given index.

        Synopsis:
          (ret, offset) = ShamrockGetSlitZeroPosition(device, index)

        Inputs:
          device - Select Shamrock to control
          index - index of the slit, must be one of the following,
            SHAMROCK_INPUT_SLIT_SIDE 
            SHAMROCK_INPUT_SLIT_DIRECT 
            SHAMROCK_OUTPUT_SLIT_SIDE 
            SHAMROCK_OUTPUT_SLIT_DIRECT 

        Outputs:
          ret - Function Return Code:
            SHAMROCK_SUCCESS - Slit zero position set
            SHAMROCK_NOT_INITIALIZED - Shamrock not initialized
            SHAMROCK_P1INVALID - Invalid device
            SHAMROCK_P2INVALID - Invalid index
            SHAMROCK_P3INVALID - Invalid offset
            SHAMROCK_COMMUNICATION_ERROR - Unable to communicate with Shamrock
          offset - the offset returned by the shamrock. valid only if the return is SHAMROCK_SUCCESS

        C++ Equiv:
          unsigned int ShamrockGetSlitZeroPosition(int device, int index, int * offset);

        See Also:
          ShamrockSetSlitZeroPosition 

    '''
    cdevice = c_int(device)
    cindex = c_int(index)
    coffset = c_int()
    ret = self.dll.ShamrockGetSlitZeroPosition(cdevice, cindex, byref(coffset))
    return (ret, coffset.value)

  def ShamrockGetTurret(self, device):
    ''' 
        Description:
          Returns the current Turret.

        Synopsis:
          (ret, Turret) = ShamrockGetTurret(device)

        Inputs:
          device - Shamrock to interrogate

        Outputs:
          ret - Function Return Code:
            SHAMROCK_SUCCESS - Turret returned
            SHAMROCK_NOT_INITIALIZED - Shamrock not initialized
            SHAMROCK_P1INVALID - Invalid device
            SHAMROCK_COMMUNICATION_ERROR - Unable to communicate with Shamrock
          Turret - pointer to the Turret

        C++ Equiv:
          unsigned int ShamrockGetTurret(int device, int * Turret);

        See Also:
          ShamrockGratingIsPresent ShamrockGetNumberGratings ShamrockGetGrating ShamrockGetGratingInfo ShamrockGetGratingOffset ShamrockGetDetectorOffset ShamrockSetTurret ShamrockSetGrating ShamrockWavelengthReset ShamrockSetGratingOffset ShamrockSetDetectorOffset 

    '''
    cdevice = c_int(device)
    cTurret = c_int()
    ret = self.dll.ShamrockGetTurret(cdevice, byref(cTurret))
    return (ret, cTurret.value)

  def ShamrockGetWavelength(self, device):
    ''' 
        Description:
          Returns the current wavelength.

        Synopsis:
          (ret, wavelength) = ShamrockGetWavelength(device)

        Inputs:
          device - Shamrock to interrogate

        Outputs:
          ret - Function Return Code:
            SHAMROCK_SUCCESS - wavelength returned
            SHAMROCK_NOT_INITIALIZED - Shamrock not initialized
            SHAMROCK_P1INVALID - Invalid device
            SHAMROCK_COMMUNICATION_ERROR - Unable to communicate with Shamrock
          wavelength - pointer to the wavelength

        C++ Equiv:
          unsigned int ShamrockGetWavelength(int device, float * wavelength);

        See Also:
          ShamrockWavelengthIsPresent ShamrockAtZeroOrder ShamrockGetWavelengthLimits ShamrockSetWavelength ShamrockGotoZeroOrder 

    '''
    cdevice = c_int(device)
    cwavelength = c_float()
    ret = self.dll.ShamrockGetWavelength(cdevice, byref(cwavelength))
    return (ret, cwavelength.value)

  def ShamrockGetWavelengthLimits(self, device, Grating):
    ''' 
        Description:
          Returns the Grating wavelength limits.

        Synopsis:
          (ret, Min, Max) = ShamrockGetWavelengthLimits(device, Grating)

        Inputs:
          device - Shamrock to interrogate
          Grating - grating to interrogate

        Outputs:
          ret - Function Return Code:
            SHAMROCK_SUCCESS - wavelength returned
            SHAMROCK_NOT_INITIALIZED - Shamrock not initialized
            SHAMROCK_P1INVALID - Invalid device
            SHAMROCK_P2INVALID - Invalid grating
            SHAMROCK_COMMUNICATION_ERROR - Unable to communicate with Shamrock
          Min - pointer to the lower wavelength limit (nm)
          Max - pointer to the upper wavelength limit (nm)

        C++ Equiv:
          unsigned int ShamrockGetWavelengthLimits(int device, int Grating, float * Min, float * Max);

        See Also:
          ShamrockWavelengthIsPresent ShamrockGetWavelength ShamrockAtZeroOrder ShamrockSetWavelength ShamrockGotoZeroOrder 

    '''
    cdevice = c_int(device)
    cGrating = c_int(Grating)
    cMin = c_float()
    cMax = c_float()
    ret = self.dll.ShamrockGetWavelengthLimits(cdevice, cGrating, byref(cMin), byref(cMax))
    return (ret, cMin.value, cMax.value)

  def ShamrockGotoZeroOrder(self, device):
    ''' 
        Description:
          Sets wavelength to zero order.

        Synopsis:
          ret = ShamrockGotoZeroOrder(device)

        Inputs:
          device - Shamrock to send command to.

        Outputs:
          ret - Function Return Code:
            SHAMROCK_SUCCESS - Wavelength set to zero order
            SHAMROCK_NOT_INITIALIZED - Shamrock not initialized
            SHAMROCK_P1INVALID - Invalid device
            SHAMROCK_COMMUNICATION_ERROR - Unable to communicate with Shamrock

        C++ Equiv:
          unsigned int ShamrockGotoZeroOrder(int device);

        See Also:
          ShamrockWavelengthIsPresent ShamrockGetWavelength ShamrockAtZeroOrder ShamrockGetWavelengthLimits ShamrockSetWavelength 

        Note: Sets wavelength to zero order.

    '''
    cdevice = c_int(device)
    ret = self.dll.ShamrockGotoZeroOrder(cdevice)
    return (ret)

  def ShamrockGratingIsPresent(self, device):
    ''' 
        Description:
          Finds if grating is present.

        Synopsis:
          (ret, present) = ShamrockGratingIsPresent(device)

        Inputs:
          device - Shamrock to interrogate

        Outputs:
          ret - Function Return Code:
            SHAMROCK_SUCCESS - Grating presence flag returned
            SHAMROCK_NOT_INITIALIZED - Shamrock not initialized
            SHAMROCK_P1INVALID - Invalid device
            SHAMROCK_COMMUNICATION_ERROR - Unable to communicate with Shamrock
          present - pointer to flag::
            0 - grating is NOT present
            1 - grating IS present

        C++ Equiv:
          unsigned int ShamrockGratingIsPresent(int device, int * present);

        See Also:
          ShamrockGetTurret ShamrockGetNumberGratings ShamrockGetGrating ShamrockGetGratingInfo ShamrockGetGratingOffset ShamrockGetDetectorOffset ShamrockSetTurret ShamrockSetGrating ShamrockWavelengthReset ShamrockSetGratingOffset ShamrockSetDetectorOffset 

    '''
    cdevice = c_int(device)
    cpresent = c_int()
    ret = self.dll.ShamrockGratingIsPresent(cdevice, byref(cpresent))
    return (ret, cpresent.value)

  def ShamrockInitialize(self, IniPath):
    ''' 
        Description:
          Initializes the Shamrock driver.

        Synopsis:
          ret = ShamrockInitialize(IniPath)

        Inputs:
          IniPath - pointer to the Andor camera DETECTOR.ini file

        Outputs:
          ret - Function Return Code:
            SHAMROCK_SUCCESS - Shamrock driver initialized
            SHAMROCK_NOT_INITIALIZED - Shamrock not initalized
            SHAMROCK_COMMUNICATION_ERROR - Can't read Shamrock EEPROM

        C++ Equiv:
          unsigned int ShamrockInitialize(char * IniPath);

        See Also:
          ShamrockGetNumberDevices ShamrockGetFunctionReturnDescription ShamrockClose 

        Note: Initializes the Shamrock driver.

    '''
    cIniPath = IniPath
    ret = self.dll.ShamrockInitialize(cIniPath)
    return (ret)

  def ShamrockIrisIsPresent(self, device, iris):
    ''' 
        Description:
          Indicates whether or not an input port has an iris.

        Synopsis:
          (ret, present) = ShamrockIrisIsPresent(device, iris)

        Inputs:
          device - Shamrock to interrogate
          iris - Iris to query: Direct=0; Side=1

        Outputs:
          ret - Function Return Code:
            SHAMROCK_SUCCESS - Current focus position returned
            SHAMROCK_NOT_INITIALIZED - Shamrock not initialized
            SHAMROCK_P1INVALID - Invalid device
            SHAMROCK_P2INVALID - Invalid iris specified.
            SHAMROCK_P3INVALID - present pointer is null
            SHAMROCK_COMMUNICATION_ERROR - Unable to communicate with Shamrock
          present - pointer to an int to store the result. not present = 0, present = 1

        C++ Equiv:
          unsigned int ShamrockIrisIsPresent(int device, int iris, int * present);

        See Also:
          ShamrockGetIris ShamrockSetIris 

    '''
    cdevice = c_int(device)
    ciris = c_int(iris)
    cpresent = c_int()
    ret = self.dll.ShamrockIrisIsPresent(cdevice, ciris, byref(cpresent))
    return (ret, cpresent.value)

  def ShamrockIsModePossible(self, device, mode):
    ''' 
        Description:
          Checks if a particular shutter mode is available.

        Synopsis:
          (ret, possible) = ShamrockIsModePossible(device, mode)

        Inputs:
          device - Shamrock to interrogate
          mode - shutter mode to check

        Outputs:
          ret - Function Return Code:
            SHAMROCK_SUCCESS - Shutter mode availability returned
            SHAMROCK_NOT_INITIALIZED - Shamrock not initialized
            SHAMROCK_P1INVALID - Invalid device
            SHAMROCK_P2INVALID - Invalid mode
            SHAMROCK_COMMUNICATION_ERROR - Unable to communicate with Shamrock
          possible - pointer to flag::
            0 - shutter mode is NOT available
            1 - shutter mode IS available

        C++ Equiv:
          unsigned int ShamrockIsModePossible(int device, int mode, int * possible);

        See Also:
          ShamrockShutterIsPresent ShamrockGetShutter ShamrockSetShutter 

    '''
    cdevice = c_int(device)
    cmode = c_int(mode)
    cpossible = c_int()
    ret = self.dll.ShamrockIsModePossible(cdevice, cmode, byref(cpossible))
    return (ret, cpossible.value)

  def ShamrockOutputSlitIsPresent(self, device):
    ''' 
        Description:
          Finds if Output Slit is present

        Synopsis:
          (ret, present) = ShamrockOutputSlitIsPresent(device)

        Inputs:
          device - Shamrock to interrogate

        Outputs:
          ret - Function Return Code:
            SHAMROCK_SUCCESS - Output Slit presence flag returned
            SHAMROCK_NOT_INITIALIZED - Shamrock not initialized
            SHAMROCK_P1INVALID - Invalid device
            SHAMROCK_COMMUNICATION_ERROR - Unable to communicate with Shamrock
          present - pointer to flag::
            0 - Output Slit is NOT present
            1 - Output Slit IS present

        C++ Equiv:
          unsigned int ShamrockOutputSlitIsPresent(int device, int * present);

        See Also:
          ShamrockGetOutputSlit ShamrockSetOutputSlit ShamrockOutputSlitReset 

    '''
    cdevice = c_int(device)
    cpresent = c_int()
    ret = self.dll.ShamrockOutputSlitIsPresent(cdevice, byref(cpresent))
    return (ret, cpresent.value)

  def ShamrockOutputSlitReset(self, device):
    ''' 
        Description:
          Resets the Output Slit to its default (10m).

        Synopsis:
          ret = ShamrockOutputSlitReset(device)

        Inputs:
          device - Select Shamrock to control.

        Outputs:
          ret - Function Return Code:
            SHAMROCK_SUCCESS - Output Slit reset
            SHAMROCK_NOT_INITIALIZED - Shamrock not initialized
            SHAMROCK_P1INVALID - Invalid device
            SHAMROCK_COMMUNICATION_ERROR - Unable to communicate with Shamrock

        C++ Equiv:
          unsigned int ShamrockOutputSlitReset(int device);

        See Also:
          ShamrockOutputSlitIsPresent ShamrockGetOutputSlit ShamrockSetOutputSlit 

    '''
    cdevice = c_int(device)
    ret = self.dll.ShamrockOutputSlitReset(cdevice)
    return (ret)

  def ShamrockSetAccessory(self, device, Accessory, State):
    ''' 
        Description:
          Sets the Accessory state.

        Synopsis:
          ret = ShamrockSetAccessory(device, Accessory, State)

        Inputs:
          device - Select Shamrock to control
          Accessory - line to set::
            1 - line 1
            2 - line 2
          State - Accessory state::
            0 - OFF
            1 - ON

        Outputs:
          ret - Function Return Code:
            SHAMROCK_SUCCESS - Line state set
            SHAMROCK_NOT_INITIALIZED - Shamrock not initialized
            SHAMROCK_P1INVALID - Invalid device
            SHAMROCK_P2INVALID - Invalid line
            SHAMROCK_COMMUNICATION_ERROR - Unable to communicate with Shamrock

        C++ Equiv:
          unsigned int ShamrockSetAccessory(int device, int Accessory, int State);

        See Also:
          ShamrockAccessoryIsPresent ShamrockGetAccessoryState 

        Note: Sets the Accessory state.

    '''
    cdevice = c_int(device)
    cAccessory = c_int(Accessory)
    cState = c_int(State)
    ret = self.dll.ShamrockSetAccessory(cdevice, cAccessory, cState)
    return (ret)

  def ShamrockSetAutoSlitCoefficients(self, device, index, x1, y1, x2, y2):
    ''' 
        Description:
          

        Synopsis:
          ret = ShamrockSetAutoSlitCoefficients(device, index, x1, y1, x2, y2)

        Inputs:
          device - 
          index - 
          x1 - 
          y1 - 
          x2 - 
          y2 - 

        Outputs:
          ret - Function Return Code

        C++ Equiv:
          unsigned int ShamrockSetAutoSlitCoefficients(int device, int index, int x1, int y1, int x2, int y2);

    '''
    cdevice = c_int(device)
    cindex = c_int(index)
    cx1 = c_int(x1)
    cy1 = c_int(y1)
    cx2 = c_int(x2)
    cy2 = c_int(y2)
    ret = self.dll.ShamrockSetAutoSlitCoefficients(cdevice, cindex, cx1, cy1, cx2, cy2)
    return (ret)

  def ShamrockSetAutoSlitWidth(self, device, index, width):
    ''' 
        Description:
          Sets the width of the specified slit.
          

        Synopsis:
          ret = ShamrockSetAutoSlitWidth(device, index, width)

        Inputs:
          device - Select Shamrock to control
          index - Specifies each individual slit on device using  the following values:
            SHAMROCK_INPUT_SLIT_SIDE (1) - 
            SHAMROCK_INPUT_SLIT_DIRECT (2) - 
            SHAMROCK_INPUT_SLIT_SIDE (3) - 
            SHAMROCK_INPUT_SLIT_DIRECT (4) - 
          width - required width of each slot (um)

        Outputs:
          ret - Function Return Code:
            SHAMROCK_SUCCESS - Slit width set
            SHAMROCK_NOT_INITIALIZED - Shamrock not initialized
            SHAMROCK_P1INVALID - Invalid device
            SHAMROCK_P2INVALID - Invalid slit index
            SHAMROCK_P3INVALID - Invalid width
            SHAMROCK_COMMUNICATION_ERROR - Unable to communicate with Shamrock

        C++ Equiv:
          unsigned int ShamrockSetAutoSlitWidth(int device, int index, float width);

        See Also:
          ShamrockAutoSlitIsPresent ShamrockGetAutoSlitWidth ShamrockAutoSlitReset 

    '''
    cdevice = c_int(device)
    cindex = c_int(index)
    cwidth = c_float(width)
    ret = self.dll.ShamrockSetAutoSlitWidth(cdevice, cindex, cwidth)
    return (ret)

  def ShamrockSetDetectorOffset(self, device, offset):
    ''' 
        Description:
          Sets the detector offset.

        Synopsis:
          ret = ShamrockSetDetectorOffset(device, offset)

        Inputs:
          device - Select Shamrock to control
          offset - detector offset (steps)

        Outputs:
          ret - Function Return Code:
            SHAMROCK_SUCCESS - Detector offset set
            SHAMROCK_NOT_INITIALIZED - Shamrock not initialized
            SHAMROCK_P1INVALID - Invalid device
            SHAMROCK_COMMUNICATION_ERROR - Unable to communicate with Shamrock

        C++ Equiv:
          unsigned int ShamrockSetDetectorOffset(int device, int offset);

        See Also:
          ShamrockGratingIsPresent ShamrockGetTurret ShamrockGetNumberGratings ShamrockGetGrating ShamrockGetGratingInfo ShamrockGetGratingOffset ShamrockGetDetectorOffset ShamrockSetTurret ShamrockSetGrating ShamrockWavelengthReset ShamrockSetGratingOffset 

    '''
    cdevice = c_int(device)
    coffset = c_int(offset)
    ret = self.dll.ShamrockSetDetectorOffset(cdevice, coffset)
    return (ret)

  def ShamrockSetDetectorOffsetEx(self, device, entrancePort, exitPort, offset):
    ''' 
        Description:
          Sets the detector offset. Use this function if the system has 4 ports and a detector offset for a specific entrance and exit port combination is to be set.
          DIRECT, DIRECT = 0, 0
          DIRECT, SIDE = 0, 1
          SIDE, DIRECT = 1, 0
          SIDE, SIDE = 1, 1

        Synopsis:
          ret = ShamrockSetDetectorOffsetEx(device, entrancePort, exitPort, offset)

        Inputs:
          device - Select Shamrock to control
            
            
          entrancePort - Select entrance port to use
          exitPort - Select exit port to use
          offset - detector offset (steps)

        Outputs:
          ret - Function Return Code:
            SHAMROCK_SUCCESS - Detector offset set
            SHAMROCK_NOT_INITIALIZED - Shamrock not initialized
            SHAMROCK_P1INVALID - Invalid device
            SHAMROCK_P4INVALID - Value outside of allowed range
            SHAMROCK_COMMUNICATION_ERROR - Unable to communicate with Shamrock

        C++ Equiv:
          unsigned int ShamrockSetDetectorOffsetEx(int device, int entrancePort, int exitPort, int offset);

        See Also:
          ShamrockGratingIsPresent ShamrockGetTurret ShamrockGetNumberGratings ShamrockGetGrating ShamrockGetGratingInfo ShamrockGetGratingOffset ShamrockGetDetectorOffset ShamrockGetDetectorOffsetEx ShamrockSetDetectorOffset ShamrockSetTurret ShamrockSetGrating ShamrockWavelengthReset ShamrockSetGratingOffset 

    '''
    cdevice = c_int(device)
    centrancePort = c_int(entrancePort)
    cexitPort = c_int(exitPort)
    coffset = c_int(offset)
    ret = self.dll.ShamrockSetDetectorOffsetEx(cdevice, centrancePort, cexitPort, coffset)
    return (ret)

  def ShamrockSetDetectorOffsetPort2(self, device, offset):
    ''' 
        Description:
          

        Synopsis:
          ret = ShamrockSetDetectorOffsetPort2(device, offset)

        Inputs:
          device - 
          offset - 

        Outputs:
          ret - Function Return Code

        C++ Equiv:
          unsigned int ShamrockSetDetectorOffsetPort2(int device, int offset);

        See Also:
          ShamrockGetDetectorOffsetPort2 

    '''
    cdevice = c_int(device)
    coffset = c_int(offset)
    ret = self.dll.ShamrockSetDetectorOffsetPort2(cdevice, coffset)
    return (ret)

  def ShamrockSetFilter(self, device, filter):
    ''' 
        Description:
          Sets the required filter.

        Synopsis:
          ret = ShamrockSetFilter(device, filter)

        Inputs:
          device - Select Shamrock to control
          filter - required filter

        Outputs:
          ret - Function Return Code:
            SHAMROCK_SUCCESS - filter set
            SHAMROCK_NOT_INITIALIZED - Shamrock not initialized
            SHAMROCK_P1INVALID - Invalid device
            SHAMROCK_P2INVALID - Invalid filter
            SHAMROCK_COMMUNICATION_ERROR - Unable to communicate with Shamrock

        C++ Equiv:
          unsigned int ShamrockSetFilter(int device, int filter);

        See Also:
          ShamrockFilterIsPresent ShamrockGetFilter ShamrockGetFilterInfo ShamrockSetFilterInfo 

    '''
    cdevice = c_int(device)
    cfilter = c_int(filter)
    ret = self.dll.ShamrockSetFilter(cdevice, cfilter)
    return (ret)

  def ShamrockSetFilterInfo(self, device, Filter, Info):
    ''' 
        Description:
          Sets the filter information.

        Synopsis:
          ret = ShamrockSetFilterInfo(device, Filter, Info)

        Inputs:
          device - Select Shamrock to control
          Filter - filter to which set the information
          Info - pointer to filter information

        Outputs:
          ret - Function Return Code:
            SHAMROCK_SUCCESS - Filter information set
            SHAMROCK_NOT_INITIALIZED - Shamrock not initialized
            SHAMROCK_P1INVALID - Invalid device
            SHAMROCK_P2INVALID - Invalid filter
            SHAMROCK_COMMUNICATION_ERROR - Unable to communicate with Shamrock

        C++ Equiv:
          unsigned int ShamrockSetFilterInfo(int device, int Filter, char * Info);

        See Also:
          ShamrockFilterIsPresent ShamrockGetFilter ShamrockGetFilterInfo ShamrockSetFilter 

    '''
    cdevice = c_int(device)
    cFilter = c_int(Filter)
    cInfo = Info
    ret = self.dll.ShamrockSetFilterInfo(cdevice, cFilter, cInfo)
    return (ret)

  def ShamrockSetFlipperMirror(self, device, flipper, port):
    ''' 
        Description:
          Sets the position of the specified flipper mirror.
          

        Synopsis:
          ret = ShamrockSetFlipperMirror(device, flipper, port)

        Inputs:
          device - Shamrock to interrogate
          flipper - The flipper can have two values which are as follows::
            SHAMROCK_INPUT_FLIPPER - 1
            SHAMROCK_OUTPUT_FLIPPER - 2
          port - The port to set the flipper mirror to.:
            SHAMROCK_DIRECT_PORT - 0
            SHAMROCK_SIDE_PORT - 1

        Outputs:
          ret - Function Return Code:
            SHAMROCK_SUCCESS - port set
            SHAMROCK_NOT_INITIALIZED - Shamrock not initialized
            SHAMROCK_P1INVALID - Invalid device
            SHAMROCK_P2INVALID - Invalid flipper
            SHAMROCK_P3INVALID - Invalid port
            SHAMROCK_COMMUNICATION_ERROR - Unable to communicate with Shamrock

        C++ Equiv:
          unsigned int ShamrockSetFlipperMirror(int device, int flipper, int port);

        See Also:
          ShamrockFlipperMirrorIsPresent ShamrockGetFlipperMirror ShamrockGetCCDLimits ShamrockFlipperMirrorReset 

    '''
    cdevice = c_int(device)
    cflipper = c_int(flipper)
    cport = c_int(port)
    ret = self.dll.ShamrockSetFlipperMirror(cdevice, cflipper, cport)
    return (ret)

  def ShamrockSetFlipperMirrorPosition(self, device, flipper, position):
    ''' 
        Description:
          Sets the current position for the specified flipper mirror.

        Synopsis:
          ret = ShamrockSetFlipperMirrorPosition(device, flipper, position)

        Inputs:
          device - Shamrock to interrogate
          flipper - The flipper can have two values which are as follows:
            SHAMROCK_INPUT_FLIPPER 1
            SHAMROCK_OUTPUT_FLIPPER 2
          position - new position for the current flipper mirror

        Outputs:
          ret - Function Return Code:
            SHAMROCK_SUCCESS - position set
            SHAMROCK_NOT_INITIALIZED - Shamrock not initialized
            SHAMROCK_P1INVALID - Invalid device
            SHAMROCK_COMMUNICATION_ERROR - Unable to communicate with Shamrock

        C++ Equiv:
          unsigned int ShamrockSetFlipperMirrorPosition(int device, int flipper, int position);

        See Also:
          ShamrockFlipperMirrorIsPresent ShamrockGetFlipperMirrorPosition ShamrockSetFlipperMirror ShamrockFlipperMirrorReset 

    '''
    cdevice = c_int(device)
    cflipper = c_int(flipper)
    cposition = c_int(position)
    ret = self.dll.ShamrockSetFlipperMirrorPosition(cdevice, cflipper, cposition)
    return (ret)

  def ShamrockSetFocusMirror(self, device, focus):
    ''' 
        Description:
          Sets the required Focus movement. Focus movement is possible from 0 to max steps, so possible values will be from (0 – current steps) to (max – current steps).

        Synopsis:
          ret = ShamrockSetFocusMirror(device, focus)

        Inputs:
          device - Select Shamrock to control
          focus - required focus movement:
            +steps move focus mirror forward
            -steps move focus mirror backwards

        Outputs:
          ret - Function Return Code:
            SHAMROCK_SUCCESS - Focus movement set
            SHAMROCK_NOT_INITIALIZED - Shamrock not initialized
            SHAMROCK_P1INVALID - Invalid device
            SHAMROCK_P2INVALID - Invalid Focus value
            SHAMROCK_COMMUNICATION_ERROR - Unable to communicate with Shamrock

        C++ Equiv:
          unsigned int ShamrockSetFocusMirror(int device, int focus);

        See Also:
          ShamrockGetFocusMirror ShamrockGetFocusMirrorMaxSteps ShamrockFocusMirrorReset ShamrockFocusMirrorIsPresent 

    '''
    cdevice = c_int(device)
    cfocus = c_int(focus)
    ret = self.dll.ShamrockSetFocusMirror(cdevice, cfocus)
    return (ret)

  def ShamrockSetGrating(self, device, grating):
    ''' 
        Description:
          Sets the required grating.

        Synopsis:
          ret = ShamrockSetGrating(device, grating)

        Inputs:
          device - Select Shamrock to control
          grating - required grating

        Outputs:
          ret - Function Return Code:
            SHAMROCK_SUCCESS - grating set
            SHAMROCK_NOT_INITIALIZED - Shamrock not initialized
            SHAMROCK_P1INVALID - Invalid device
            SHAMROCK_P2INVALID - Invalid grating
            SHAMROCK_COMMUNICATION_ERROR - Unable to communicate with Shamrock

        C++ Equiv:
          unsigned int ShamrockSetGrating(int device, int grating);

        See Also:
          ShamrockGratingIsPresent ShamrockGetTurret ShamrockGetNumberGratings ShamrockGetGrating ShamrockGetGratingInfo ShamrockGetGratingOffset ShamrockGetDetectorOffset ShamrockSetTurret ShamrockWavelengthReset ShamrockSetGratingOffset ShamrockSetDetectorOffset 

    '''
    cdevice = c_int(device)
    cgrating = c_int(grating)
    ret = self.dll.ShamrockSetGrating(cdevice, cgrating)
    return (ret)

  def ShamrockSetGratingOffset(self, device, Grating, offset):
    ''' 
        Description:
          Sets the grating offset

        Synopsis:
          ret = ShamrockSetGratingOffset(device, Grating, offset)

        Inputs:
          device - Select Shamrock to control
          Grating - grating to to which set the offset
          offset - grating offset (steps)

        Outputs:
          ret - Function Return Code:
            SHAMROCK_SUCCESS - grating offset set
            SHAMROCK_NOT_INITIALIZED - Shamrock not initialized
            SHAMROCK_P1INVALID - Invalid device
            SHAMROCK_P2INVALID - Invalid grating
            SHAMROCK_COMMUNICATION_ERROR - Unable to communicate with Shamrock

        C++ Equiv:
          unsigned int ShamrockSetGratingOffset(int device, int Grating, int offset);

        See Also:
          ShamrockGratingIsPresent ShamrockGetTurret ShamrockGetNumberGratings ShamrockGetGrating ShamrockGetGratingInfo ShamrockGetGratingOffset ShamrockGetDetectorOffset ShamrockSetTurret ShamrockSetGrating ShamrockWavelengthReset ShamrockSetDetectorOffset 

    '''
    cdevice = c_int(device)
    cGrating = c_int(Grating)
    coffset = c_int(offset)
    ret = self.dll.ShamrockSetGratingOffset(cdevice, cGrating, coffset)
    return (ret)

  def ShamrockSetIris(self, device, iris, value):
    ''' 
        Description:
          Sets iris position for the specified iris port. Value must be in the range 0 to 100.

        Synopsis:
          ret = ShamrockSetIris(device, iris, value)

        Inputs:
          device - Shamrock to interrogate
          iris - Iris to set: Direct=0; Side=1
          value - Position to set the iris, in the range 0-100

        Outputs:
          ret - Function Return Code:
            SHAMROCK_SUCCESS - Current iris position returned
            SHAMROCK_NOT_INITIALIZED - Shamrock not initialized
            SHAMROCK_P1INVALID - Invalid device
            SHAMROCK_P2INVALID - Invalid iris specified.
            SHAMROCK_P3INVALID - Value is out of range
            SHAMROCK_NOT_AVAILABLE - No iris at specified index
            SHAMROCK_COMMUNICATION_ERROR - Unable to communicate with Shamrock

        C++ Equiv:
          unsigned int ShamrockSetIris(int device, int iris, int value);

        See Also:
          ShamrockGetIris ShamrockIrisIsPresent 

    '''
    cdevice = c_int(device)
    ciris = c_int(iris)
    cvalue = c_int(value)
    ret = self.dll.ShamrockSetIris(cdevice, ciris, cvalue)
    return (ret)

  def ShamrockSetNumberPixels(self, device, NumberPixels):
    ''' 
        Description:
          Sets the number of pixels of the attached sensor.

        Synopsis:
          ret = ShamrockSetNumberPixels(device, NumberPixels)

        Inputs:
          device - Select Shamrock to control
          NumberPixels - number of pixels of attached sensor

        Outputs:
          ret - Function Return Code:
            SHAMROCK_SUCCESS - port set
            SHAMROCK_NOT_INITIALIZED - Shamrock not initialized
            SHAMROCK_P1INVALID - Invalid device
            SHAMROCK_P2INVALID - Invalid number
            SHAMROCK_COMMUNICATION_ERROR - Unable to communicate with Shamrock

        C++ Equiv:
          unsigned int ShamrockSetNumberPixels(int device, int NumberPixels);

        See Also:
          ShamrockGetPixelWidth ShamrockSetPixelWidth ShamrockGetNumberPixels ShamrockGetCalibration 

    '''
    cdevice = c_int(device)
    cNumberPixels = c_int(NumberPixels)
    ret = self.dll.ShamrockSetNumberPixels(cdevice, cNumberPixels)
    return (ret)

  def ShamrockSetOutputSlit(self, device, width):
    ''' 
        Description:
          Sets the Output Slit width.

        Synopsis:
          ret = ShamrockSetOutputSlit(device, width)

        Inputs:
          device - Select Shamrock to control
          width - required Output Slit width (m)

        Outputs:
          ret - Function Return Code:
            SHAMROCK_SUCCESS - Output Slit width set
            SHAMROCK_NOT_INITIALIZED - Shamrock not initialized
            SHAMROCK_P1INVALID - Invalid device
            SHAMROCK_P2INVALID - Invalid slit width
            SHAMROCK_COMMUNICATION_ERROR - Unable to communicate with Shamrock

        C++ Equiv:
          unsigned int ShamrockSetOutputSlit(int device, float width);

        See Also:
          ShamrockOutputSlitIsPresent ShamrockGetOutputSlit ShamrockOutputSlitReset 

    '''
    cdevice = c_int(device)
    cwidth = c_float(width)
    ret = self.dll.ShamrockSetOutputSlit(cdevice, cwidth)
    return (ret)

  def ShamrockSetPixelWidth(self, device, Width):
    ''' 
        Description:
          Sets the pixel width in microns of the attached sensor.

        Synopsis:
          ret = ShamrockSetPixelWidth(device, Width)

        Inputs:
          device - Select Shamrock to control
          Width - pixel width of attached sensor

        Outputs:
          ret - Function Return Code:
            SHAMROCK_SUCCESS - port set
            SHAMROCK_NOT_INITIALIZED - Shamrock not initialized
            SHAMROCK_P1INVALID - Invalid device
            SHAMROCK_P2INVALID - Invalid width
            SHAMROCK_COMMUNICATION_ERROR - Unable to communicate with Shamrock

        C++ Equiv:
          unsigned int ShamrockSetPixelWidth(int device, float Width);

        See Also:
          ShamrockGetPixelWidth ShamrockGetNumberPixels ShamrockSetNumberPixels ShamrockGetCalibration 

    '''
    cdevice = c_int(device)
    cWidth = c_float(Width)
    ret = self.dll.ShamrockSetPixelWidth(cdevice, cWidth)
    return (ret)

  def ShamrockSetPort(self, device, port):
    ''' 
        Description:
          Sets the required port.

        Synopsis:
          ret = ShamrockSetPort(device, port)

        Inputs:
          device - Select Shamrock to control
          port - required port

        Outputs:
          ret - Function Return Code:
            SHAMROCK_SUCCESS - port set
            SHAMROCK_NOT_INITIALIZED - Shamrock not initialized
            SHAMROCK_P1INVALID - Invalid device
            SHAMROCK_P2INVALID - Invalid port
            SHAMROCK_COMMUNICATION_ERROR - Unable to communicate with Shamrock

        C++ Equiv:
          unsigned int ShamrockSetPort(int device, int port);

        See Also:
          ShamrockFlipperIsPresent ShamrockGetPort ShamrockGetCCDLimits ShamrockFlipperReset 

    '''
    cdevice = c_int(device)
    cport = c_int(port)
    ret = self.dll.ShamrockSetPort(cdevice, cport)
    return (ret)

  def ShamrockSetShutter(self, device, mode):
    ''' 
        Description:
          Sets the shutter mode.

        Synopsis:
          ret = ShamrockSetShutter(device, mode)

        Inputs:
          device - Select Shamrock to control
          mode - shutter mode:
            0 - Closed
            1 - Open

        Outputs:
          ret - Function Return Code:
            SHAMROCK_SUCCESS - Shutter mode set
            SHAMROCK_NOT_INITIALIZED - Shamrock not initialized
            SHAMROCK_P1INVALID - Invalid device
            SHAMROCK_P2INVALID - Invalid shutter
            SHAMROCK_COMMUNICATION_ERROR - Unable to communicate with Shamrock

        C++ Equiv:
          unsigned int ShamrockSetShutter(int device, int mode);

        See Also:
          ShamrockShutterIsPresent ShamrockGetShutter ShamrockIsModePossible 

    '''
    cdevice = c_int(device)
    cmode = c_int(mode)
    ret = self.dll.ShamrockSetShutter(cdevice, cmode)
    return (ret)

  def ShamrockSetSlit(self, device, width):
    ''' 
        Description:
          Sets the Input Slit width.

        Synopsis:
          ret = ShamrockSetSlit(device, width)

        Inputs:
          device - Select Shamrock to control
          width - Input Slit width

        Outputs:
          ret - Function Return Code:
            SHAMROCK_SUCCESS - Input Slit width set
            SHAMROCK_NOT_INITIALIZED - Shamrock not initialized
            SHAMROCK_P1INVALID - Invalid device
            SHAMROCK_P2INVALID - Invalid width
            SHAMROCK_COMMUNICATION_ERROR - Unable to communicate with Shamrock

        C++ Equiv:
          unsigned int ShamrockSetSlit(int device, float width);

        See Also:
          ShamrockSlitIsPresent ShamrockGetSlit ShamrockSlitReset 

    '''
    cdevice = c_int(device)
    cwidth = c_float(width)
    ret = self.dll.ShamrockSetSlit(cdevice, cwidth)
    return (ret)

  def ShamrockSetSlitCoefficients(self, device, x1, y1, x2, y2):
    ''' 
        Description:
          

        Synopsis:
          ret = ShamrockSetSlitCoefficients(device, x1, y1, x2, y2)

        Inputs:
          device - 
          x1 - 
          y1 - 
          x2 - 
          y2 - 

        Outputs:
          ret - Function Return Code

        C++ Equiv:
          unsigned int ShamrockSetSlitCoefficients(int device, int x1, int y1, int x2, int y2);

    '''
    cdevice = c_int(device)
    cx1 = c_int(x1)
    cy1 = c_int(y1)
    cx2 = c_int(x2)
    cy2 = c_int(y2)
    ret = self.dll.ShamrockSetSlitCoefficients(cdevice, cx1, cy1, cx2, cy2)
    return (ret)

  def ShamrockSetSlitZeroPosition(self, device, index, offset):
    ''' 
        Description:
          Sets the zero position for the slit at the given index.

        Synopsis:
          ret = ShamrockSetSlitZeroPosition(device, index, offset)

        Inputs:
          device - Select Shamrock to control
          index - index of the slit, must be one of the following,
            SHAMROCK_INPUT_SLIT_SIDE 
            SHAMROCK_INPUT_SLIT_DIRECT 
            SHAMROCK_OUTPUT_SLIT_SIDE 
            SHAMROCK_OUTPUT_SLIT_DIRECT 
          offset - must be in the range (-200 - 0)

        Outputs:
          ret - Function Return Code:
            SHAMROCK_SUCCESS - Slit zero position set
            SHAMROCK_NOT_INITIALIZED - Shamrock not initialized
            SHAMROCK_P1INVALID - Invalid device
            SHAMROCK_P2INVALID - Invalid index
            SHAMROCK_P3INVALID - Invalid offset
            SHAMROCK_COMMUNICATION_ERROR - Unable to communicate with Shamrock

        C++ Equiv:
          unsigned int ShamrockSetSlitZeroPosition(int device, int index, int offset);

        See Also:
          ShamrockGetSlitZeroPosition 

    '''
    cdevice = c_int(device)
    cindex = c_int(index)
    coffset = c_int(offset)
    ret = self.dll.ShamrockSetSlitZeroPosition(cdevice, cindex, coffset)
    return (ret)

  def ShamrockSetTurret(self, device, Turret):
    ''' 
        Description:
          Sets the required Turret.

        Synopsis:
          ret = ShamrockSetTurret(device, Turret)

        Inputs:
          device - Select Shamrock to control
          Turret - required Turret

        Outputs:
          ret - Function Return Code:
            SHAMROCK_SUCCESS - Turret set
            SHAMROCK_NOT_INITIALIZED - Shamrock not initialized
            SHAMROCK_P1INVALID - Invalid device
            SHAMROCK_P2INVALID - Invalid Turret
            SHAMROCK_COMMUNICATION_ERROR - Unable to communicate with Shamrock

        C++ Equiv:
          unsigned int ShamrockSetTurret(int device, int Turret);

        See Also:
          ShamrockGratingIsPresent ShamrockGetTurret ShamrockGetNumberGratings ShamrockGetGrating ShamrockGetGratingInfo ShamrockGetGratingOffset ShamrockGetDetectorOffset ShamrockSetGrating ShamrockWavelengthReset ShamrockSetGratingOffset ShamrockSetDetectorOffset 

    '''
    cdevice = c_int(device)
    cTurret = c_int(Turret)
    ret = self.dll.ShamrockSetTurret(cdevice, cTurret)
    return (ret)

  def ShamrockSetWavelength(self, device, wavelength):
    ''' 
        Description:
          Sets the required wavelength.

        Synopsis:
          ret = ShamrockSetWavelength(device, wavelength)

        Inputs:
          device - Select Shamrock to control
          wavelength - required wavelength

        Outputs:
          ret - Function Return Code:
            SHAMROCK_SUCCESS - Required wavelength set
            SHAMROCK_NOT_INITIALIZED - Shamrock not initialized
            SHAMROCK_P1INVALID - Invalid device
            SHAMROCK_P2INVALID - Invalid wavelength
            SHAMROCK_COMMUNICATION_ERROR - Unable to communicate with Shamrock

        C++ Equiv:
          unsigned int ShamrockSetWavelength(int device, float wavelength);

        See Also:
          ShamrockWavelengthIsPresent 

    '''
    cdevice = c_int(device)
    cwavelength = c_float(wavelength)
    ret = self.dll.ShamrockSetWavelength(cdevice, cwavelength)
    return (ret)

  def ShamrockShutterIsPresent(self, device):
    ''' 
        Description:
          Finds if Shutter is present.

        Synopsis:
          (ret, present) = ShamrockShutterIsPresent(device)

        Inputs:
          device - Shamrock to interrogate

        Outputs:
          ret - Function Return Code:
            SHAMROCK_SUCCESS - Shutter presence flag returned
            SHAMROCK_NOT_INITIALIZED - Shamrock not initialized
            SHAMROCK_P1INVALID - Invalid device
            SHAMROCK_COMMUNICATION_ERROR - Unable to communicate with Shamrock
          present - pointer to flag::
            0 - Shutter is NOT present
            1 - Shutter IS present

        C++ Equiv:
          unsigned int ShamrockShutterIsPresent(int device, int * present);

        See Also:
          ShamrockGetShutter ShamrockSetShutter ShamrockIsModePossible 

    '''
    cdevice = c_int(device)
    cpresent = c_int()
    ret = self.dll.ShamrockShutterIsPresent(cdevice, byref(cpresent))
    return (ret, cpresent.value)

  def ShamrockSlitIsPresent(self, device):
    ''' 
        Description:
          Finds if Input Slit is present.

        Synopsis:
          (ret, present) = ShamrockSlitIsPresent(device)

        Inputs:
          device - Shamrock to interrogate

        Outputs:
          ret - Function Return Code:
            SHAMROCK_SUCCESS - Input Slit presence flag returned
            SHAMROCK_NOT_INITIALIZED - Shamrock not initialized
            SHAMROCK_P1INVALID - Invalid device
            SHAMROCK_COMMUNICATION_ERROR - Unable to communicate with Shamrock
          present - pointer to flag::
            0 - Input Slit is NOT present
            1 - Input Slit IS present

        C++ Equiv:
          unsigned int ShamrockSlitIsPresent(int device, int * present);

        See Also:
          ShamrockGetSlit ShamrockSetSlit ShamrockSlitReset 

    '''
    cdevice = c_int(device)
    cpresent = c_int()
    ret = self.dll.ShamrockSlitIsPresent(cdevice, byref(cpresent))
    return (ret, cpresent.value)

  def ShamrockSlitReset(self, device):
    ''' 
        Description:
          Resets the Input Slit to its default (10m).

        Synopsis:
          ret = ShamrockSlitReset(device)

        Inputs:
          device - Select Shamrock to control.

        Outputs:
          ret - Function Return Code:
            SHAMROCK_SUCCESS - Input Slit reset
            SHAMROCK_NOT_INITIALIZED - Shamrock not initialized
            SHAMROCK_P1INVALID - Invalid device
            SHAMROCK_COMMUNICATION_ERROR - Unable to communicate with Shamrock

        C++ Equiv:
          unsigned int ShamrockSlitReset(int device);

        See Also:
          ShamrockSlitIsPresent ShamrockGetSlit ShamrockSetSlit 

    '''
    cdevice = c_int(device)
    ret = self.dll.ShamrockSlitReset(cdevice)
    return (ret)

  def ShamrockWavelengthIsPresent(self, device):
    ''' 
        Description:
          Finds if the turret motors are installed.

        Synopsis:
          (ret, present) = ShamrockWavelengthIsPresent(device)

        Inputs:
          device - Shamrock to interrogate

        Outputs:
          ret - Function Return Code:
            SHAMROCK_SUCCESS - turret motors presence flag returned
            SHAMROCK_NOT_INITIALIZED - Shamrock not initialized
            SHAMROCK_P1INVALID - Invalid device
            SHAMROCK_COMMUNICATION_ERROR - Unable to communicate with Shamrock
          present - pointer to flag::
            0 - turret motors is NOT present
            1 - turret motors IS present

        C++ Equiv:
          unsigned int ShamrockWavelengthIsPresent(int device, int * present);

        See Also:
          ShamrockGetWavelength ShamrockAtZeroOrder ShamrockGetWavelengthLimits ShamrockSetWavelength ShamrockGotoZeroOrder 

    '''
    cdevice = c_int(device)
    cpresent = c_int()
    ret = self.dll.ShamrockWavelengthIsPresent(cdevice, byref(cpresent))
    return (ret, cpresent.value)

  def ShamrockWavelengthReset(self, device):
    ''' 
        Description:
          Resets the wavelength to 0 nm.

        Synopsis:
          ret = ShamrockWavelengthReset(device)

        Inputs:
          device - Select Shamrock to control.

        Outputs:
          ret - Function Return Code:
            SHAMROCK_SUCCESS - wavelength reset
            SHAMROCK_NOT_INITIALIZED - Shamrock not initialized
            SHAMROCK_P1INVALID - Invalid device
            SHAMROCK_COMMUNICATION_ERROR - Unable to communicate with Shamrock

        C++ Equiv:
          unsigned int ShamrockWavelengthReset(int device);

        See Also:
          ShamrockGratingIsPresent ShamrockGetTurret ShamrockGetNumberGratings ShamrockGetGrating ShamrockGetGratingInfo ShamrockGetGratingOffset ShamrockGetDetectorOffset ShamrockSetTurret ShamrockSetGrating ShamrockSetGratingOffset ShamrockSetDetectorOffset 

        Note: Resets the wavelength to 0 nm.

    '''
    cdevice = c_int(device)
    ret = self.dll.ShamrockWavelengthReset(cdevice)
    return (ret)

