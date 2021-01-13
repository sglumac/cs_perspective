/*****************************************************
************* 10/07/15 Team Paprika ******************
*********** model constants defintions ***************
*****************************************************/

#include <fmi2TypesPlatform.h>
#include <fmi2Functions.h>
#include <fmi2FunctionTypes.h>

#include <stdio.h>
#include <string.h>
#include <math.h>

#define GUID_VALUE "{481bd0fd-3a1a-4530-98e2-685fa567810c}"

typedef struct
{
  fmi2Real output;
  fmi2Real stepFinalValue;
  fmi2Real stepStartValue;
  fmi2Real stepTime;
  fmi2Real stepFinalValueDown;
  fmi2Real stepStartValueDown;
  fmi2Real stepTimeDown;
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
  Component* Alpha = c;
  size_t i;

  for (i = 0; i < nvr; i++)
  {
    switch (vr[i])
    {
    case 0:
      value[i] = Alpha->output;
      break;
    case 1:
      value[i] = Alpha->stepFinalValue;
      break;
    case 2:
      value[i] = Alpha->stepStartValue;
      break;
	case 3:
      value[i] = Alpha->stepTime;
      break;
	case 4:
      value[i] = Alpha->stepFinalValueDown;
      break;
	case 5:
      value[i] = Alpha->stepStartValueDown;
      break;
	case 6:
      value[i] = Alpha->stepTimeDown;
      break;  
	case 7:
      value[i] = Alpha->time;
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
  Component* Alpha = c;
  size_t i;
  for (i = 0; i < nvr; i++)
  {
    switch (vr[i])
    {
    case 1:
      Alpha->stepFinalValue = value[i];
      break;
    case 2:
      Alpha->stepStartValue = value[i];
      break;
	case 3:
      Alpha->stepTime = value[i];
      break;
	case 4:
      Alpha->stepFinalValueDown = value[i];
      break;
	case 5:
      Alpha->stepStartValueDown = value[i];
      break;
	case 6:
      Alpha->stepTimeDown = value[i];
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
    Component* Alpha = malloc(sizeof(Component));
    //initialize time
    
    // model variables initialization

    Alpha->output = 0;
    Alpha->stepFinalValue = 1;
    Alpha->stepStartValue = 0;
    Alpha->stepTime = 1;
    Alpha->stepFinalValueDown = -1;
    Alpha->stepStartValueDown = 0;
    Alpha->stepTimeDown = 2;

    return Alpha;
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
  Component* Alpha = c;

  if (c == NULL) // check component, should not be modified
  {
    return fmi2Error;
  }
  else  if ( abs(Alpha->time - currentCommunicationPoint)>0.000000001) // check time integrity, should not be modified
  
  {
    return fmi2Error;
  }
  else
  {

    // model time update
    Alpha->time += communicationStepSize;

    // model equations should be implemented here
	
	if ((Alpha->time < Alpha->stepTime) && (Alpha->time < Alpha->stepTimeDown))
		Alpha->output = Alpha->stepStartValue + Alpha->stepStartValueDown;
	else if ((Alpha->time >= Alpha->stepTime) && (Alpha->time < Alpha->stepTimeDown))
		Alpha->output = Alpha->stepFinalValue + Alpha->stepStartValueDown;
	else
		Alpha->output = Alpha->stepFinalValue + Alpha->stepFinalValueDown;

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