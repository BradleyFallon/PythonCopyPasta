
class ControlledObject(object):
    """
    This is a base class used to create objects that will use setter and getter methods
    for the attributes, rather than directly overwriting attributes with new objects.
    """

    def __getattribute__(self, key):
        # see https://docs.python.org/3/howto/descriptor.html#id5
        "Emulate type_getattro() in Objects/typeobject.c"
        attrib = object.__getattribute__(self, key)
        if hasattr(attrib, '__get__'):
            try:
                val = attrib.__get__(None, self)
                return val
            except TypeError:
                pass 
        return attrib

    def __setattr__(self, key, val):
        """
        If the attribute does not exist, create it.
        If the attribute exists and has a setter method, use it.
        Otherwise, set value with normal overwrite.
        """
        try:
            attrib = object.__getattribute__(self, key)
        except AttributeError:
            self.__dict__[key] = val
            return
        if hasattr(attrib, '__set__'):
            attrib.__set__(None, val)
            return
        self.__dict__[key] = val

    def __str__(self):
        ret_str = ""
        for key in self.__dict__:
            attrib = object.__getattribute__(self, key)
            if hasattr(attrib, 'name'):
                ret_str += attrib.name + ": \"" + str(attrib.__get__(None, self)) + '\"\n'
            elif isinstance(attrib, ControlledObject):
                ret_str += attrib.__str__()
        return ret_str


# https://docs.python.org/3/howto/descriptor.html
class PropertyAbstract(ControlledObject):
    """
    This stands as a definition of what the minimum requirements are for a property in this system.
    All properties should have custom written getter and setter methods to type control.
    Each property needs a name, which will be the key used when assigning values in ANSA.
    """
    def __init__(self, val=None, name='var_str'):
        self.__set__(self, val)
        self.name = name

    def __get__(self, obj, objtype):
        raise NotImplementedError()

    def __set__(self, obj, val):
        raise NotImplementedError()


class StrInt(int):
    """
    This class creates an int-like object that can be added with strings.
    """
    def __add__(self, val):
        return StrInt(super().__add__(int(val)))
    __radd__ = __add__


class StrFloat(float):
    """
    This class creates a float-like object that can be added with strings.
    """
    def __add__(self, val):
        return StrFloat(super().__add__(float(val)))
    __radd__ = __add__


class StrBool(object):
    """
    This class creates a bool-like object becomes yes/no for string.
    """
    def __get__(self, obj, objtype):
        return self

    def __set__(self, obj, val):
        self.val = val.__bool__()

    def __str__(self):
        return "yes" if self.val else "no"

    def __init__(self, val=None, name=None):
        PropertyAbstract.__init__(self, val, name)


class PropText(PropertyAbstract):
    """
    This is a text property, which is named.
    """
    def __get__(self, obj, objtype):
        return str(self.val)

    def __set__(self, obj, val):
        self.val = str(val)

    def __init__(self, val=None, name='var_str'):
        PropertyAbstract.__init__(self, val, name)


class PropStrInt(PropertyAbstract):
    """
    This is a whole-number property, which is named.
    """
    def __init__(self, val=None, name='var_name'):
        PropertyAbstract.__init__(self, val, name)

    def __get__(self, obj, objtype):
        return int(self.val)

    def __set__(self, obj, val):
        self.val = StrInt(val)


class PropStrFloat(PropertyAbstract):
    """
    This is a decimal number property, which is named.
    """
    def __get__(self, obj, objtype):
        try:
            return float(self.val)
        except:
            return None

    def __set__(self, obj, val):
        self.val = StrFloat(val)

    def __init__(self, val=None, name='var_name'):
        PropertyAbstract.__init__(self, val, name)


class PropStrBool(PropertyAbstract):
    """
    Bool that stores yes/no as True/False. Value is bool, but str method prints as yes/no
    """
    def __init__(self, val=None, name='var_name'):
        PropertyAbstract.__init__(self, val, name)

    def __get__(self, obj, objtype):
        return self.val

    def __set__(self, obj, val):
        # If input is literally True/False/None use that
        # Otherwise, try to determine based on value
        if val is None:
            self.val = StrBool(False)
        elif val is True:
            self.val = StrBool(True)
        elif val is False:
            self.val = StrBool(False)
        elif isinstance(val, str):
            if val.lower()[0] in ('y', 't'):
                self.val = StrBool(True)
            elif val.lower()[0] in ('n', 'f'):
                self.val = StrBool(False)
            else:
                raise ValueError("String not clearly yes or no.")
        elif isinstance(val, int):
            if val == 0:
                self.val = StrBool(False)
            else:
                self.val = StrBool(True)
        else:
            raise ValueError("Ambiguous input.")

