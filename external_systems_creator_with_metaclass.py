# -*- coding: utf-8 -*-
'''
External systems plugin
Implementation with a metaclass

@author: Raquel Toribio
'''

import types

#===============================================================================
# Use decorator to that does the following:
#    1.- calls the function given as a parameter
#    2.- If the function raises NotImplementedError exception do nothing. 
#    3.- Otherwise, record the result of the call (if it was successful or not)
#===============================================================================
def _common_process(func):
    '''
    Decorator method to execute always the same functionality upon invoking
    an action on the external system creator.
    The function passed in the argument should contain as the first argument
    (after self) the incidence entity. 
    Example: func = action_first_assignment(self, incidence, external_tt_id)
    '''
    def inner(self, *args, **kwargs):
        # Extract the incidence id from the first argument (which should be
        # the incidence
        if 'incidence' in kwargs:
            incidence_id = kwargs['incidence']['_id']
        elif args != None:
            incidence_id = args[0]['_id']
        else:
            print "Incidence id not passed as argument"
            return
        common_method = func.__name__
        print "INCIDENCE_ID=%s: External System=%s, Common " \
              "functionality for action %s: args: %s, kwargs: %s" % (
                                            incidence_id,
                                            self.external_system_code,
                                            common_method,
                                            args,
                                            kwargs)

        try:
            # Execute the action
            result = func(self, *args, **kwargs)
            
            print "INCIDENCE_ID=%s: External System %s notified Ok of %s" % (
                    incidence_id, self.external_system_code, common_method)

            # TODO: Record in history event ok
        
        except NotImplementedError:
            print "Action %s (external_system %s.) NOT IMPLEMENTED" \
                    % (common_method, self.external_system_code)
            
        except Exception, exc:
            # Error notifying action. Record it in incidence history and send 
            # e-mail notification
            error_detail = exc
            print "INCIDENCE_ID=%s: External System %s error on action %s. Detail: %s %s" \
                        % (incidence_id, self.external_system_code, common_method,
                           type(exc).__name__, error_detail)

            # TODO: Record in history event nok
            # TODO: Send error notification (not specified yet)
    return inner

#===============================================================================
# Define a metaclass to decorate all methods of a class that start by action_
#===============================================================================
class ExternalSystemCreatorMetaclass(type):
    """
    Metaclass
    """
    def __new__(meta, classname, bases, classDict):
        print "Entering net of meta"
        print "meta", meta
        print "classname", classname
        print "bases", bases
        newClassDict = {}
        
        for attributeName, attribute in classDict.items():
            if isinstance(attribute, types.FunctionType) and attributeName.startswith('action_'):
                print "decorate method", attributeName
                attribute = _common_process(attribute)
            newClassDict[attributeName] = attribute
        return type.__new__(meta, classname, bases, newClassDict)


#===============================================================================
# Use base class ExternalSystemCreator to:
# - define all possible event methods and their parameters
# - Its metaclass is ExternalSystemCreatorMetaclass to decorate all event methods
# with common defined behaviour.
#===============================================================================
class ExternalSystemCreator(object):
    """Base class for external systems' integration.
    Scenario: ExternalSystem creates UDO Incidence.
    Implements common functionality.
    This class is NOT meant to be instanced, but to be subclassed.
    To create new external systems:
     1. Extend this class and implement '__init__(self, external_system_code)'.
     2. Implement concrete functionality on 'action_<name>' methods if there
     is something to do with that event.
     3. OPTIONAL: If we need to override common action functionality return
     "Not implemented"
    """
    __metaclass__ = ExternalSystemCreatorMetaclass
    
    def __init__(self, external_system_code):
        self.external_system_code = external_system_code

    def action_first_assignment(self, incidence, external_tt_id):
        raise NotImplementedError()

    def action_active(self, incidence, external_tt_id, causeStatus):
        raise NotImplementedError()

    def action_delayed(self, incidence, external_tt_id, causeStatus, delayedReason):
        raise NotImplementedError()
    
    def action_restored(self, incidence, external_tt_id, causeStatus):
        raise NotImplementedError()
    
    def action_solved(self, incidence, external_tt_id, causeStatus):
        raise NotImplementedError()
    
    def action_active_after_solved(self, incidence, external_tt_id, causeStatus):
        raise NotImplementedError()

    def action_added_note(self, incidence, external_tt_id, annotation):
        raise NotImplementedError()
    
    def action_added_attachment(self, incidence, external_tt_id, uri, name):
        raise NotImplementedError()

#===============================================================================
# How to Define the external system plugin:
# - Define a class that inherits from ExternalSystemCreator
# - If we need to process an event, define the method action_*
# - If we need to process an event, but with a different behaviour to the one
#   defined in the common process, define the method action_* and return 
#   "NotImplemented"
#===============================================================================
class ExampleExternalSystemPlugin(ExternalSystemCreator):
    '''
    Test Plugin to check behaviour Ok and not OK of each possible
    defined action with External System (Scenario: Transfer to UDo)
    '''
    EXTERNAL_TT_ID = "EXTERNAL_ID_OK"
    EXTERNAL_TT_ID_NOT_IMPLEMENT = "EXTERNAL_ID_NOT_IMPLEMENT"
    EXTERNAL_TT_ID_NOK = "EXTERNAL_ID_NOK"

    def __init__(self, external_system_name):
        super(ExampleExternalSystemPlugin, self).__init__(external_system_name)

    def action_first_assignment(self, incidence, external_tt_id):
        if external_tt_id == self.EXTERNAL_TT_ID:
            #TODO: Call specific ws api...
            pass
        else:
            raise Exception("Error invoking first assignment")

    def action_delayed(self, incidence, external_tt_id, causeStatus, delayedReason):
        if external_tt_id == self.EXTERNAL_TT_ID_NOT_IMPLEMENT:
            print "Special case of delayed where external system must not be notified. Do nothing"
            raise NotImplementedError()  
        elif external_tt_id == self.EXTERNAL_TT_ID:
            #TODO: Call specific ws api...
            pass
        else:
            raise Exception("Error invoking delayed")

    def action_restored(self, incidence, external_tt_id, causeStatus):
        if external_tt_id == self.EXTERNAL_TT_ID:
            #TODO: Call specific ws api...
            pass
        else:
            raise Exception("Error invoking restored")

    def action_solved(self, incidence, external_tt_id, causeStatus):
        if external_tt_id == self.EXTERNAL_TT_ID:
            #TODO: Call specific ws api...
            pass
        else:
            raise ExternalError("Error invoking solved")

    def action_added_note(self, incidence, external_tt_id, annotation):
        if external_tt_id == self.EXTERNAL_TT_ID:
            #TODO: Call specific ws api...
            pass
        else:
            raise Exception("Error invoking added note")

    def action_added_attachment(self, incidence, external_tt_id, uri, name):
        if external_tt_id == self.EXTERNAL_TT_ID:
            #TODO: Call specific ws api...
            pass
        else:
            raise Exception("Error invoking added attachment")
        
        

#===============================================================================
# Let's do some tests:
#
#===============================================================================
incidence_data = {"_id": "5141cefd97fbe51310000001"}

ex_sys = ExampleExternalSystemPlugin(external_system_name='EXAMPLE')

#===============================================================================
# Plugin implements this event. Simulate no error communicating with external system
#===============================================================================
ex_sys.action_first_assignment(incidence=incidence_data, external_tt_id='EXTERNAL_ID_OK')

#===============================================================================
# Plugin implements this event. Simulate error communicating with external system
#===============================================================================
ex_sys.action_first_assignment(incidence=incidence_data, external_tt_id='EXTERNAL_ID_NOK')

#===============================================================================
# Plugin does not implement this event.
#===============================================================================
ex_sys.action_active(incidence=incidence_data, external_tt_id='EXTERNAL_ID_OK', causeStatus="This is a test")

#===============================================================================
# Plugin implements this event but only for certain data
# Check implementation
#===============================================================================
ex_sys.action_delayed(incidence=incidence_data, external_tt_id='EXTERNAL_ID_OK',
                      causeStatus="This is a test", delayedReason='REJECTION')

#===============================================================================
# Check no implementation
#===============================================================================
ex_sys.action_delayed(incidence=incidence_data, external_tt_id='EXTERNAL_ID_NOT_IMPLEMENT',
                      causeStatus="This is a test", delayedReason='REJECTION')



