# -*- coding: utf-8 -*-
'''
External systems plugin

@author: Raquel Toribio
'''

#===============================================================================
# Use base class ExternalSystemCreator to:
# - define all possible event methods and their parameters
# - all event methods (action_*) are decorated with a decorator that does the 
# following:
#    1.- checks if real plugin implements the event method by having the method
#        (_action_*)
#    2.- If the real plugin has the implementation method, calls it and records
#         the result
#    3.- If the real plugin does not have the method, does nothing. 
#===============================================================================

class ExternalSystemCreator(object):
    """Base class for external systems' integration.
    It defines possible events the plugins can implement
    This class is NOT meant to be instanced, but to be subclassed.
    To create new external systems:
     1. Extend this class with a class called CreatorHandler
     and implement '__init__(self, external_system_code)'.
     2. Implement concrete functionality on '_action_<name>' methods if there
     is something to do with that event.
     3. OPTIONAL: Override common action functionality (action_<name> methods)
    """
    def __init__(self, external_system_code):
        self.external_system_code = external_system_code

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
                return False         
            common_method = func.__name__
            print "INCIDENCE_ID=%s: External System=%s, Common " \
                  "functionality for action %s: args: %s, kwargs: %s" % (
                                            incidence_id,
                                            self.external_system_code,
                                            common_method,
                                            args,
                                            kwargs)
            plugin_method = self._get_plugin_method_name(common_method)
            # Check if External Plugin implements the plugin_method for the action.
            if not hasattr(self, plugin_method):
                print "Action %s (external_system %s.) NOT IMPLEMENTED" % \
                    (common_method, self.external_system_code)              
                # Not record anything in history
                return False
            else:
                try:
                    # Execute the plugin method
                    getattr(self, plugin_method)(*args, **kwargs)

                    print "INCIDENCE_ID=%s: External System %s notified Ok of %s" % (
                          str(incidence_id), self.external_system_code, common_method)

                    # Record in history event ok
                    return True
                except Exception, exc:
                    # Error notifying action. Record it in incidence history and send 
                    # e-mail notification
                    print "INCIDENCE_ID=%s: External System %s error on action %s. Detail: %s %s" \
                        % (incidence_id, self.external_system_code, common_method,
                           type(exc).__name__, exc)
                    # Record in history event nok 
        return inner

    def _get_plugin_method_name(self, common_method):
        return "_" + common_method

    @_common_process
    def action_first_assignment(self, incidence, external_tt_id):
        pass
        
    @_common_process
    def action_active(self, incidence, external_tt_id, causeStatus):
        pass

    @_common_process
    def action_delayed(self, incidence, external_tt_id, causeStatus, delayedReason):
        pass

    @_common_process
    def action_restored(self, incidence, external_tt_id, causeStatus):
        pass

    @_common_process
    def action_solved(self, incidence, external_tt_id, causeStatus):
        pass

    @_common_process
    def action_added_note(self, incidence, external_tt_id, annotation):
        pass

    @_common_process
    def action_added_attachment(self, incidence, external_tt_id, uri, name):
        pass


#===============================================================================
# How to Define the external system plugin:
# - Define a class that inherits from ExternalSystemCreator
# - If we need to process an event, define the corresponding method _action_*
# - If we need to process an event, but with a different behaviour to the one
#   defined in the common process, redefine the method action_*.
#===============================================================================
class ExampleExternalSystemPlugin(ExternalSystemCreator):
    '''
    Test Plugin to check behaviour Ok and not OK of each possible
    defined action with External System (Scenario: Transfer to UDo)
    '''
    
    EXTERNAL_TT_ID = "EXTERNAL_ID_OK"
    EXTERNAL_TT_ID_NOT_IMPLEMENT = "EXTERNAL_ID_NOT_IMPLEMENT"
    EXTERNAL_TT_ID_FOR_ERROR = "EXTERNAL_ID_NOK"
    
    def __init__(self, external_system_name):
        super(ExampleExternalSystemPlugin, self).__init__(external_system_name)

    def _action_first_assignment(self, incidence, external_tt_id):
        if external_tt_id == self.EXTERNAL_TT_ID:
            return True
        else:
            raise Exception("Error invoking first assignment")

    def action_delayed(self, incidence, external_tt_id, causeStatus, delayedReason):
        if external_tt_id == self.EXTERNAL_TT_ID_NOT_IMPLEMENT:
            print "Delayed action for case where we do not need to inform external system. Do nothing"
            return True
        else:
            return super(ExampleExternalSystemPlugin, self).action_delayed(incidence, external_tt_id, causeStatus, delayedReason)
        
    def _action_delayed(self, incidence, external_tt_id, causeStatus, delayedReason):
        if external_tt_id == self.EXTERNAL_TT_ID:
            return True
        else:
            raise Exception("Error invoking delayed")

    def _action_restored(self, incidence, external_tt_id, causeStatus):
        if external_tt_id == self.EXTERNAL_TT_ID:
            return True
        else:
            raise Exception("Error invoking restored")

    def _action_solved(self, incidence, external_tt_id, causeStatus):
        if external_tt_id == self.EXTERNAL_TT_ID:
            return True
        else:
            raise Exception("Error invoking solved")

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
# Plugin implements this event but only for certain data
# Check no implementation
#===============================================================================
ex_sys.action_delayed(incidence=incidence_data, external_tt_id='EXTERNAL_ID_NOT_IMPLEMENT',
                      causeStatus="This is a test", delayedReason='REJECTION')



