import re
import sys


class _Pointer(object):
    def __init__(self, data):
        self._data = data
        self._index = 0

    def next(self):
        if self._index == len(self._data):
            raise StopIteration
        element = self._data[self._index]
        self._index += 1
        return element


def getter_factory(name, prefix="_", default_value=None):
    def getter(self):
        return getattr(self, "{}{}".format(prefix, name), default_value)
    return getter


def setter_factory(name, prefix="_"):
    def setter(self, value):
        return setattr(self, "{}{}".format(prefix, name), value)
    return setter


def decorator_factory(
    name,
    properties=None,
    default_value=None
):
    def decorator(cls):
        def set_prefixed_attrs(cls, name, default_value, prefix=True):
            if prefix:
                attr_format = "_{}"
            else:
                attr_format = "{}"
            setattr(cls, attr_format.format(name), default_value)

        getter, setter = None, None
        if 'getter' in properties:
            getter = getter_factory(
                name,
                default_value=default_value
            )
        if 'setter' in properties:
            setter = setter_factory(name)

        prop = property(getter, setter)
        if properties:
            setattr(cls, name, prop)
            set_prefixed_attrs(cls, name, default_value)
        else:
            set_prefixed_attrs(cls, name, default_value)
        return cls
    return decorator


def setshortcode(code):
    decorator = decorator_factory(
        "shortcode",
        default_value=code,
        properties=["getter"]
    )

    return decorator


def guidproperty(cls):
    decorator = decorator_factory(
        "guid",
        properties=["getter", "setter"]
    )

    cls.has_guid = classmethod(lambda cls: True)

    return decorator(cls)


def rarityproperty(cls):
    decorator = decorator_factory(
        "rarity",
        properties=["getter", "setter"]
    )

    cls.has_rarity = classmethod(lambda cls: True)

    def patcher(the_class=cls):
        old_eq = the_class.__eq__

        def new_eq(self, other):
            state = old_eq(self, other)
            try:
                state = state and (self.rarity == other.rarity)
            except AttributeError:
                pass
            return state

        the_class.__eq__ = new_eq

    patcher(cls)
    return decorator(cls)


def levelproperty(cls):
    decorator = decorator_factory(
        "level",
        properties=["getter", "setter"]
    )

    def patcher(the_class=cls):
        old_eq = the_class.__eq__

        def new_eq(self, other):
            state = old_eq(self, other)
            try:
                state = state and (self.level == other.level)
            except AttributeError:
                pass
            return state

        the_class.__eq__ = new_eq

        def has_level(cls):
            return True

        setattr(the_class, "has_level", classmethod(has_level))

    patcher(cls)
    return decorator(cls)


class Item(object):
    """ A virtual class container for all Inventory item types """
    def __init__(self):
        pass

    def itemcount(self):
        return 1

    def invcount(self):
        return 1

    def __eq__(self, other):
        if (self.__class__ == other.__class__):
            return True
        return False

    def __str__(self):
        return "{}{}{}".format(
            self.rarity.shortcode if hasattr(self, "has_rarity") and self.rarity is not None else "",
            self.shortcode,
            self.level if hasattr(self, "has_level") else ""
        )


class Rarity(object):
    """
        Some items have a Rarity value.
        This is a virtual class for all Rarity levels
    """
    def __init__(self):
        pass

    def __eq__(self, other):
        if self.__class__ == other.__class__:
            return True
        return False


@setshortcode("C")
class Common(Rarity):
    """ Very Rare level rarity """
    def __init__(self):
        super(Common, self).__init__()


@setshortcode("VC")
class VeryCommon(Rarity):
    """ Very Common level rarity """
    def __init__(self):
        super(VeryCommon, self).__init__()


@setshortcode("R")
class Rare(Rarity):
    """ Rare level rarity """
    def __init__(self):
        super(Rare, self).__init__()


@setshortcode("VR")
class VeryRare(Rarity):
    """ Very Rare level rarity """
    def __init__(self):
        super(VeryRare, self).__init__()


@guidproperty
@decorator_factory("title", properties=["getter", "setter"])
@decorator_factory("area", properties=["getter", "setter"])
@decorator_factory("note", properties=["getter", "setter"])
@decorator_factory("latlng", properties=["getter", "setter"])
class Portal(object):
    def __init__(self, guid=None, title=None, area=None, note=None, latlng=None):
        self._guid = guid
        self._title = title
        self._area = area
        self._note = note
        self._latlng = latlng


@decorator_factory("portal", properties=["getter", "setter"])
@setshortcode("KEY")
class Key(Item):
    """ """
    def __init__(self, portal=None, **kwargs):
        super(Key, self).__init__()
        if portal:
            self._portal = portal
        elif kwargs:
            self._portal = Portal(**kwargs)
        else:
            self._portal = None

    def __str__(self):
        out = "KEY{}"
        additional = []
        if self.title is not None:
            additional.append("{}".format(repr(self.title)))
        if self.guid is not None:
            additional.append("<{}>".format(self.guid))
        return out.format("[" + " ".join(additional) + "]" if additional else "")

    @property
    def guid(self):
        try:
            return self.portal.guid
        except AttributeError:
            return None

    @property
    def title(self):
        try:
            return self.portal.title
        except AttributeError:
            return None

    @property
    def area(self):
        try:
            return self.portal.area
        except AttributeError:
            return None

    @property
    def note(self):
        try:
            return self.portal.note
        except AttributeError:
            return None

    @property
    def latlng(self):
        try:
            return self.portal.latlng
        except AttributeError:
            return None


class Media(Item):
    """ """
    def __init__(self):
        super(Media, self).__init__()


class Powerup(Item):
    """ """
    def __init__(self):
        super(Powerup, self).__init__()


@rarityproperty
class PowerCubeItem(Item):
    """ """
    def __init__(self):
        super(Item, self).__init__()


@levelproperty
@setshortcode("P")
class PowerCube(PowerCubeItem):
    """ """
    def __init__(self):
        super(PowerCube, self).__init__()


@setshortcode("LUBE")
class LawsonPowerCube(PowerCubeItem):
    """ """
    def __init__(self):
        super(LawsonPowerCube, self).__init__()
        self.rarity = VeryRare()

    def __str__(self):
        return "{}".format(
            self.shortcode,
        )


@levelproperty
@rarityproperty
@setshortcode("R")
class Resonator(Item):
    """ """
    def __init__(self):
        super(Resonator, self).__init__()
        self.rarity = VeryCommon()

    def __str__(self):
        return "{}{}".format(
            self.shortcode,
            self.level
        )


@guidproperty
@rarityproperty
class Container(Item):
    """ """
    def __init__(self, guid=None):
        super(Container, self).__init__()
        self._guid = guid or None
        self._contents = []
        # Array of valid items for this container
        self._restricted_items = []
        # Modifier for key count, when actual keys added or deleted are not known. -ve = deleted
        self._key_modifier = 0

    def __iter__(self):
        return _Pointer(self._contents)

    def __len__(self):
        return len(self.contents)

    def __getattr__(self, name):
        property_map_lists = {
            "resonators": Resonator,
            "weapons": Weapon,
            "bursters": Burster,
            "mods": Mod,
            "powercubes": PowerCube,
            "shields": Shield,
            "keys": Key,
        }
        property_map_dicts = {
            "capsules": Capsule,
            "mufgs": MUFG,
            "keycaps": KeyCapsule,
            "containers": Container,
        }
        if name in self.__dict__:
            return self.__dict__[name]
        if name in property_map_lists:
            return [
                x for x in self.contents
                if isinstance(x, property_map_lists[name])
            ]
        if name in property_map_dicts:
            return {
                x.guid: x for x in self.contents
                if isinstance(x, property_map_dicts[name])
            }
        raise AttributeError(
            "No attribute {} on {}".format(name, type(self).__name__)
        )

    @property
    def contents(self):
        return self._contents

    @contents.setter
    def contents(self, val):
        self._contents = val

    def itemcount(self):
        return sum([x.itemcount() for x in self.contents]) + self._key_modifier

    def invcount(self):
        return self.itemcount() + 1

    def add(self, item):
        assert(any([isinstance(item, x) for x in self._restricted_items]))
        self.contents.append(item)

    def delete(self, item):
        try:
            for elem in self.contents:
                if elem == item:
                    self.contents.remove(elem)
                    break

                if False:
                    try:
                        # identify item by guid and remove it.
                        if elem.guid == item.guid:
                            self.contents.remove(elem)
                            break
                    except AttributeError:
                        if (item.__class__ == elem.__class__ and
                           item.level == elem.level and
                           item.rarity == elem.rarity):
                            self.contents.remove(elem)
                            break
            else:
                raise RuntimeError(
                    "Could not find item with guid {} in inventory".format(
                        item.guid
                    )
                )
        except ValueError:
            pass


@setshortcode("MUFG")
class MUFG(Container):
    """ """
    def __init__(self, guid=None):
        super(MUFG, self).__init__(guid=guid)
        self._restricted_items = [
            Resonator,
            Key,
            Media,
            PowerCubeItem,
            Mod,
            Weapon,
        ]


@setshortcode("CAP")
class Capsule(Container):
    """ """
    def __init__(self, guid=None):
        super(Capsule, self).__init__(guid=guid)
        self._restricted_items = [
            Resonator,
            Key,
            Media,
            PowerCubeItem,
            Mod,
            Weapon,
        ]


@setshortcode("KCAP")
class KeyCapsule(Container):
    def __init__(self, guid=None):
        super(KeyCapsule, self).__init__(guid=guid)
        self._restricted_items = [
            Key,
        ]

    def invcount(self):
        return 1


@rarityproperty
class Weapon(Item):
    """ """
    def __init__(self):
        super(Weapon, self).__init__()
        self.rarity = VeryCommon()

    def __str__(self):
        return "{}{}".format(
            self.shortcode,
            self.level if hasattr(self, "has_level") else ""
        )


@levelproperty
@setshortcode("X")
class Burster(Weapon):
    """ """
    def __init__(self):
        super(Burster, self).__init__()


@levelproperty
@setshortcode("US")
class Ultrastrike(Weapon):
    """ """
    def __init__(self):
        super(Ultrastrike, self).__init__()


class Virus(Weapon):
    """ """
    def __init__(self):
        super(Virus, self).__init__()
        self.rarity = VeryRare()

    def __str__(self):
        return "{}".format(
            self.shortcode,
        )


@setshortcode("ADA")
class Ada(Virus):
    """ """
    def __init__(self):
        super(Ada, self).__init__()


@setshortcode("JARVIS")
class Jarvis(Virus):
    """ """
    def __init__(self):
        super(Jarvis, self).__init__()


@rarityproperty
class Mod(Item):
    """ """
    def __init__(self):
        super(Mod, self).__init__()


@setshortcode("MH")
class MultiHack(Mod):
    """ """
    def __init__(self):
        super(MultiHack, self).__init__()


@setshortcode("FA")
class ForceAmp(Mod):
    """ """
    def __init__(self):
        super(ForceAmp, self).__init__()
        self.rarity = Rare()


@setshortcode("T")
class Turret(Mod):
    """ """
    def __init__(self):
        super(Turret, self).__init__()
        self.rarity = Rare()


@setshortcode("S")
class Shield(Mod):
    """ """
    def __init__(self):
        super(Shield, self).__init__()


@setshortcode("AXA")
class AxaShield(Shield):
    def __init__(self):
        super(AxaShield, self).__init__()
        self.rarity = VeryRare()

    def __str__(self):
        return "{}".format(
            self.shortcode,
        )


@setshortcode("LA")
class LinkAmp(Mod):
    """ """
    def __init__(self):
        super(LinkAmp, self).__init__()
        self.rarity = Rare()

    def __str__(self):
        return "{}".format(
            self.shortcode,
        )


@setshortcode("SBUL")
class SoftBankUltraLink(LinkAmp):
    def __init__(self):
        super(SoftBankUltraLink, self).__init__()
        self.rarity = VeryRare()


@setshortcode("HS")
class HeatSink(Mod):
    """ """
    def __init__(self):
        super(HeatSink, self).__init__()


class Transaction(object):
    def __init__(self):
        self._transaction = None

    def __call__(self, target):
        pass


class Inventory(object):
    def __init__(self):
        self._inventory = []
        self._staged_transactions = []
        this_module = sys.modules[__name__]
        self._shortcodes = {
            plevel: {
                cls._shortcode: cls
                for cls in this_module.__dict__.values()
                if hasattr(cls, "_shortcode") and
                (
                    hasattr(cls, "has_level")
                    if plevel == "level_items"
                    else
                    not hasattr(cls, "has_level")
                )
            }
            for plevel in ("level_items", "nolevel_items")
        }
        self._raritycodes = {
            cls._shortcode: cls
            for cls in this_module.__dict__.values()
            if isinstance(cls, type) and
            issubclass(cls, Rarity) and
            "_shortcode" in cls.__dict__
        }

    def __setattr__(self, name, val):
        if name in ("_staged_transactions",
                    "_inventory",
                    "_shortcodes",
                    "_raritycodes"):
            self.__dict__[name] = val
        if name in ("staged_transactions", "inventory"):
            realname = "_{}".format(name)
            self.__dict__[realname] = val

    def __getattr__(self, name):
        property_map_lists = {
            "resonators": Resonator,
            "weapons": Weapon,
            "bursters": Burster,
            "mods": Mod,
            "powercubes": PowerCube,
            "shields": Shield,
            "keys": Key,
        }
        property_map_dicts = {
            "capsules": Capsule,
            "mufgs": MUFG,
            "keycaps": KeyCapsule,
            "containers": Container,
        }
        if name in self.__dict__:
            return self.__dict__[name]
        if name in ("staged_transactions", "inventory"):
            try:
                realname = "_{}".format(name)
                return self.__dict__[realname]
            except KeyError:
                raise AttributeError(
                    "Could not find attribute {} ({}) on {}".format(
                        name,
                        realname,
                        type(self).__name__
                    )
                )
        if name in property_map_lists:
            return [
                x for x in self.inventory
                if isinstance(x, property_map_lists[name])
            ]
        if name in property_map_dicts:
            return {
                x.guid: x for x in self.inventory
                if isinstance(x, property_map_dicts[name])
            }
        raise AttributeError(
            "No attribute {} on {}".format(name, type(self).__name__)
        )

    def itemcount(self):
        return sum([x.itemcount() for x in self.inventory])

    def invcount(self):
        return sum([x.invcount() for x in self.inventory])

    def add(self, item):
        self.inventory.append(item)

    def delete(self, item):
        print "DELETE {}".format(item)
        try:
            for elem in self.inventory:
                if item == elem:
                    self.inventory.remove(elem)
                    break

                if False:
                    try:
                        # identify item by guid and remove it.
                        if elem.guid == item.guid:
                            self.inventory.remove(elem)
                            break
                    except AttributeError:
                        if (item.__class__ == elem.__class__ and
                           item.level == elem.level and
                           item.rarity == elem.rarity):
                            break
            else:
                raise RuntimeError(
                    "Could not find item {} in inventory".format(item)
                )
        except ValueError:
            pass

    def find_item(self, guid=None):
        for item in self.inventory:
            try:
                if item.guid == guid:
                    return item
            except AttributeError:
                pass
        return None

    def stage_transaction(self, transaction):
        self.staged_transactions.append(transaction)

    def apply_staged_transactions(self):
        for transaction in self.staged_transactions:
            self.apply_transaction(transaction)

    @property
    def apply_re(self):
        return re.compile(
            r'(?P<crdr>CR|DR)\s+(?P<target>\w+)\s+'
            r'(?P<transaction>(?:(\d+\s+\w+\d?|KEY\s*\[.*?\])\s*)+)'
        )

    def apply_transaction(self, transaction):
        tx_re = self.apply_re
        operations = {
            "CR": "add",
            "DR": "delete"
        }
        for match in tx_re.finditer(transaction):
            target = self
            if match.group("target") != "INV":
                target = self.find_item(guid=match.group("target"))
            self._apply_individual_transaction(
                operations[match.group("crdr")],
                target,
                match.group("transaction")
            )

    @property
    def apply_individual_re(self):
        return re.compile(
            (
                r'(?:(?P<amount>\d+)\s+)?'
                r'(?:'
                r'(?P<key>KEY\s*\[(.*?)\])|'
                r'(?P<lshortcode>(?:{}))(?P<level>\d)|'
                r'(?P<rarity>{})?(?P<nlshortcode>(?:{}))'
                r')\s*'
            ).format(
                '|'.join(x for x in self._shortcodes["level_items"]),
                '|'.join(x for x in self._raritycodes),
                '|'.join(x for x in self._shortcodes["nolevel_items"])
            )
        )

    def _apply_individual_transaction(self, operation, target, transaction):
        tx_re = self.apply_individual_re
        for match in tx_re.finditer(transaction):
            item = self._get_transaction_item(match)
            if "amount" in match.groupdict() and match.group("amount"):
                for _ in xrange(0, int(match.group("amount"))):
                    getattr(target, operation)(item)
            else:
                getattr(target, operation)(item)

    def _get_transaction_item(self, match):
        if match.group("key"):
            item = Key()

        elif match.group("nlshortcode"):
            shortcode = match.group("nlshortcode")
            klass = self._shortcodes["nolevel_items"][shortcode]
            item = klass()

        elif match.group("lshortcode"):
            shortcode = match.group("lshortcode")
            klass = self._shortcodes["level_items"][shortcode]
            item = klass()
            item.level = int(match.group("level"))

        try:
            item.rarity = self._raritycodes[match.group("rarity")]()
        except KeyError:
            pass
        return item
