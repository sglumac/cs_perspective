/*****************************************************
************* 10/07/15 Team Paprika ******************
*********** model constants defintions ***************
*****************************************************/

#include <fmi2TypesPlatform.h>
#include <fmi2Functions.h>
#include <fmi2FunctionTypes.h>

#include <stdio.h>
#include <string.h>

#define GUID_VALUE "{481bd0fd-3a1a-4530-98e2-685fa567810c}"

typedef struct
{
  fmi2Real input;
  fmi2Real gain;
  fmi2Real output;
  fmi2Real time;
} Component;


const char* fmi2GetTypesPlatform(void)
{
  return fmi2TypesPlatform;
}

const char* fmi2GetVersion(void)
{
  return fmi2Version;
}

fmi2Status  fmi2SetDebugLogging(fmi2Component c, fmi2Boolean b1, size_t n, const fmi2String categories[])
{
  return fmi2Warning;
}

fmi2Status fmi2GetReal(fmi2Component c, const fmi2ValueReference vr[], size_t nvr, fmi2Real value[])
{
  Component* gain = c;
  size_t i;

  for (i = 0; i < nvr; i++)
  {
    switch (vr[i])
    {
    case 0:
      value[i] = gain->input;
      break;
    case 1:
      value[i] = gain->output;
      break;
    case 2:
      value[i] = gain->gain;
      break;
    default:
      return fmi2Error;
    }
  }

  return fmi2OK;
}

fmi2Status fmi2GetInteger(fmi2Component c, const fmi2ValueReference vr[], size_t nvr, fmi2Integer value[])
{
  if (nvr != 0)
  {
    return fmi2Error;
  }
  else
  {
    return fmi2OK;
  }
}

fmi2Status fmi2GetBoolean(fmi2Component c, const fmi2ValueReference vr[], size_t nvr, fmi2Boolean value[])
{
  if (nvr != 0)
  {
    return fmi2Error;
  }
  else
  {
    return fmi2OK;
  }
}

fmi2Status fmi2GetString(fmi2Component c, const fmi2ValueReference vr[], size_t nvr, fmi2String value[])
{
  if (nvr != 0)
  {
    return fmi2Error;
  }
  else
  {
    return fmi2OK;
  }
}

fmi2Status fmi2SetReal(fmi2Component c, const fmi2ValueReference vr[], size_t nvr, const fmi2Real value[])
{
  Component* gain = c;
  size_t i;
  for (i = 0; i < nvr; i++)
  {
    switch (vr[i])
    {
    case 0:
      gain->input = value[i];
      break;
    case 2:
      gain->gain = value[i];
      break;
    default:
      return fmi2Error;
    }
  }

  return fmi2OK;
}

fmi2Status fmi2SetInteger(fmi2Component c, const fmi2ValueReference vr[], size_t nvr, const fmi2Integer value[])
{
  if (nvr != 0)
  {
    return fmi2Error;
  }
  else
  {
    return fmi2OK;
  }
}

fmi2Status fmi2SetBoolean(fmi2Component c, const fmi2ValueReference vr[], size_t nvr, const fmi2Boolean value[])
{
  if (nvr != 0)
  {
    return fmi2Error;
  }
  else
  {
    return fmi2OK;
  }
}

fmi2Status fmi2SetString(fmi2Component c, const fmi2ValueReference vr[], size_t nvr, const fmi2String value[])
{
  if (nvr != 0)
  {
    return fmi2Error;
  }
  else
  {
    return fmi2OK;
  }
}

fmi2Component fmi2Instantiate(fmi2String instanceName, fmi2Type fmuType, fmi2String fmuGUID, fmi2String fmuResourceLocation,
  const fmi2CallbackFunctions* functions, fmi2Boolean visible, fmi2Boolean loggingOn)
{

  //check if instance name is valid, should not be modified
  if (instanceName == NULL || !strlen(instanceName))
  {
    return NULL;
  }
  // check if GUID is valid, should not be modified
  else if (strcmp(fmuGUID, GUID_VALUE))
  {
    return NULL;
  }
  else 
  {
    
    // create model instance
    Component* gain = malloc(sizeof(Component));
    //initialize time
    
    // model variables initialization
    gain->input = 0;
    gain->output = 0;
    gain->gain = 2;

    return gain;
  }
}

fmi2Status fmi2SetupExperiment(fmi2Component c, fmi2Boolean toleranceDefined, fmi2Real tolerance,
  fmi2Real startTime, fmi2Boolean stopTimeDefined, fmi2Real stopTime)
{
  ((Component*)c)->time = startTime;
  return fmi2OK;
}

fmi2Status fmi2EnterInitializationMode(fmi2Component c)
{
  if (c == NULL)
  {
    return fmi2Error;
  }
  else
  {
    return fmi2OK;
  }
}


// fmi2ExitInitializationMode function
fmi2Status fmi2ExitInitializationMode(fmi2Component c)
{
  if (c == NULL)
  {
    return fmi2Error;
  }
  {
    return fmi2OK;
  }
}


// fmi2DoStep function
fmi2Status fmi2DoStep(fmi2Component c, fmi2Real currentCommunicationPoint, fmi2Real communicationStepSize,
  fmi2Boolean noSetFMUStatePriorToCurrentPoint)
{
  Component* gain = c;

  if (c == NULL) // check component, should not be modified
  {
    return fmi2Error;
  }
  else  if (gain->time != currentCommunicationPoint) // check time integrity, should not be modified
  {
    return fmi2Error;
  }
  else
  {
    // model time update
    gain->time += communicationStepSize;

    // model equations should be implemented here
    gain->output = gain->gain * gain->input;

    return fmi2OK;
  }
}


// fmi2Reset dummy function
fmi2Status fmi2Reset(fmi2Component c)
{
  return fmi2OK;
}

fmi2Status fmi2Terminate(fmi2Component c)
{
  return fmi2OK;
}

// frees allocated memory
void fmi2FreeInstance(fmi2Component c)
{
  free((Component*)c);
}

fmi2Status fmi2GetFMUstate(fmi2Component c, fmi2FMUstate* s)
{
  return fmi2Error;
}

fmi2Status fmi2SetFMUstate(fmi2Component c, fmi2FMUstate s)
{
  return fmi2Error;
}

fmi2Status fmi2FreeFMUstate(fmi2Component c, fmi2FMUstate* s)
{
  return fmi2Error;
}

fmi2Status fmi2SerializedFMUstateSize(fmi2Component c, fmi2FMUstate s, size_t* n)
{
  return fmi2Error;
}

fmi2Status fmi2SerializeFMUstate(fmi2Component c, fmi2FMUstate s, fmi2Byte xs[], size_t y)
{
  return fmi2Error;
}

fmi2Status fmi2DeSerializeFMUstate(fmi2Component c, const fmi2Byte xs[], size_t n, fmi2FMUstate* s)
{
  return fmi2Error;
}

fmi2Status fmi2GetDirectionalDerivative(fmi2Component c, const fmi2ValueReference vrs[], size_t nvr,
  const fmi2ValueReference vrs2[], size_t n,
  const fmi2Real someReals1[], fmi2Real someReals2[])
{
  return fmi2Error;
}

/* Simulating the slave */
fmi2Status fmi2SetRealInputDerivatives(fmi2Component c, const fmi2ValueReference vrs[], size_t n, const fmi2Integer sd[], const fmi2Real fdg[])
{
  return fmi2Error;
}

fmi2Status fmi2GetRealOutputDerivatives(fmi2Component c, const fmi2ValueReference vrs[], size_t n, const fmi2Integer as[], fmi2Real gfdg[])
{
  return fmi2Error;
}

fmi2Status fmi2CancelStep(fmi2Component c)
{
  return fmi2Error;
}

/* Inquire slave status */
fmi2Status fmi2GetStatus(fmi2Component c, const fmi2StatusKind k, fmi2Status* s)
{
  return fmi2Error;
}

fmi2Status fmi2GetRealStatus(fmi2Component c, const fmi2StatusKind k, fmi2Real* r)
{
  return fmi2Error;
}

fmi2Status fmi2GetIntegerStatus(fmi2Component c, const fmi2StatusKind k, fmi2Integer* i)
{
  return fmi2Error;
}

fmi2Status fmi2GetBooleanStatus(fmi2Component c, const fmi2StatusKind k, fmi2Boolean* b)
{
  return fmi2Error;
}
fmi2Status fmi2GetStringStatus(fmi2Component c, const fmi2StatusKind k, fmi2String* str)
{
  return fmi2Error;
}