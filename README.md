External System Functionality Plugins
=====================================

What is the Problem?

If a ticket in UDo is created by an external system, UDo may need to notify the external system of certain events upon the ticket. 
UDo should normally also record the notification result in the ticket history.

The integration with each external system may imply different degree of notification events, for example: 
* an external system may not need to be notified of all possible UDo events.
* an external system may need to be notified of an event only under certain conditions

The solution should work in a generic way for all possible external systems

# Chosen implementation: Using a decorator 

external_systems_creator_with_decorator.py

A base class is defined that will be extended for any particular implementation that might be needed for a connectivity with a third party. 

On this base class all possible events are defined (action_*) and the specific class for connecting with an external system X only defines the needed methods as _action_*.

We use a decorator to check if from the name of the function passed as argument (action_*) the implementing class defines that method (_action_*). If it's the case, it's executed and stored in a historic

# An alternative: Use a metaclass

external_systems_creator_with_metaclass.py

A base class is defined that will be extended for any particular implementation that might be needed for a connectivity with a third party. 

On this base class all possible events are defined (action_*) and the specific class for connecting with an external system X only redefines the needed action_* methods.

We use a metaclass to decorate all methods from base class (and the classes that inherit from them) that start with "action_". 

The decorator calls the method (action_*) passed as argument. If the method raises NotImplementedError exception, do nothing. Otherwise store the result of the operation in a historic.



