"""Inventory BDD Tests."""
from unittest import TestCase
from nose2.tools import params
import Inventory


class TestAddItem(TestCase):
    """It should allow you to add any Item to it."""

    def setUp(self):
        self.inventory = Inventory.Inventory()

    def test_newinventory_is_empty(self):
        """A newly created Inventory should be an_empty_inventory."""
        self.assertEqual(self.inventory.invcount(), 0)

    def test_addamod(self):
        """After adding a mod the_size_should_be_one."""
        item = Inventory.Mod()
        self.inventory.add(item)
        self.assertEqual(self.inventory.invcount(), 1)


class TestPopulatedInventory(TestCase):
    def setUp(self):
        self.inventory = Inventory.Inventory()
        counts = {
            "Resonator": 10,
            "Mod": 5
        }
        for item, num in counts.iteritems():
            for _ in range(0, num):
                self.inventory.add(getattr(Inventory, item)())

    def test_item_count(self):
        """ With the above initialisation, invenetory count must be 15."""
        self.assertEqual(self.inventory.itemcount(), 15)

    def test_resonator_count(self):
        """ ...and the resonator count should be 10."""
        count = reduce(
            lambda a, b: a + b.invcount(),
            self.inventory.resonators,
            0
        )
        self.assertEqual(count, 10)

    def test_mod_count(self):
        """ ...and the mod count should be 5."""
        count = reduce(lambda a, b: a + b.invcount(), self.inventory.mods, 0)
        self.assertEqual(count, 5)

    def test_immediate_count(self):
        self.assertEqual(self.inventory.invcount(), 15)

    def test_capsule_addition(self):
        """
        Adding a capsule with 5 items.

        Should make both item and inventory counts equal 6.
        """
        capsule = Inventory.Capsule()
        for _ in range(0, 5):
            capsule.add(Inventory.Resonator())
        self.inventory.add(capsule)

        self.assertEqual(self.inventory.itemcount(), 21)
        self.assertEqual(self.inventory.invcount(), 21)

    def test_keylocker_addition(self):
        """
        When adding_a_keylocker_with_5_keys,
        item and inventory counts should differ.
        """
        locker = Inventory.KeyCapsule()
        for _ in range(0, 5):
            locker.add(Inventory.Key())
        self.inventory.add(locker)

        self.assertEqual(self.inventory.itemcount(), 21)
        self.assertEqual(self.inventory.invcount(), 16)


class TestProcessTransaction(TestCase):
    def setUp(self):
        self.inventory = Inventory.Inventory()

    @params(
        (
            "individual item",
            "CR INV 5 X8",
            {
                "bursters": (8, 5)
            }
        ),
        (
            "multiple items",
            "CR INV 5 X8 3 R6",
            {
                "bursters": (8, 5),
                "resonators": (6, 3)
            }
        )
    )
    def test_credit_transaction(self, name, transaction, conditions):
        self.inventory.apply_transaction(transaction)
        for prop, condition in conditions.iteritems():
            self.assertEqual(len(getattr(self.inventory, prop)), condition[1])
            self.assertTrue(all(x.level == condition[0] for x in getattr(self.inventory, prop)))

    def test_debit_transation(self):
        self.inventory.apply_transaction("CR INV 5 X8")
        self.assertEqual(len(self.inventory.bursters), 5)

        transaction = "DR INV 3 X8"
        self.inventory.apply_transaction(transaction)
        self.assertEqual(len(self.inventory.bursters), 2)
        self.assertTrue(all(x.level == 8 for x in self.inventory.bursters))

    def test_debit_guid_transaction(self):
        for guid in ("AABBAABB", "9FD860A1"):
            # Add a Capsule with a GUID
            capsule = Inventory.Capsule()
            capsule.guid = guid
            self.inventory.add(capsule)
        transaction = "CR 9FD860A1 5 X8"
        self.inventory.apply_transaction(transaction)
        self.assertTrue(all(x.level == 8 for x in self.inventory.capsules["9FD860A1"]))
        self.assertEqual(len(self.inventory.capsules["9FD860A1"].bursters), 5)

        transaction = "DR 9FD860A1 3 X8"
        self.inventory.apply_transaction(transaction)
        self.assertTrue(all(x.level == 8 for x in self.inventory.capsules["9FD860A1"]))
        self.assertEqual(len(self.inventory.capsules["9FD860A1"].bursters), 2)
        self.assertEqual(len(self.inventory.capsules["AABBAABB"].bursters), 0)

    def test_stored_transaction(self):
        self.fail()