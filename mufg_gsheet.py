import gspread
from oauth2client.service_account import ServiceAccountCredentials
from collections import namedtuple


class MUFG_Gsheet(object):
    def __init__(self, creds_file=None):
        scope = ["https://spreadsheets.google.com/feeds"]
        if creds_file is None:
            self.creds = ServiceAccountCredentials.from_json_keyfile_name(
                '/cygdrive/c/Users/michael.noel_jones/Downloads/IngressLinkathon-a70381e6ff09.json',
                scope
            )
        else:
            self.creds = ServiceAccountCredentials.from_json_keyfile_name(creds_file, scope)
        self.gc = None
        self.sht = None
        self.mufg = None
        self.keys = None
        self.keycap_cols_start_end = ("G", "K")
        self.mufg_cols_start_end = ("L", "X")
        self.cap_cols_start_end = ("Z", "AV")
        self.data_rows_start_end = (5, 56)
        self.init()

    def init(self):
        self.gc = gspread.authorize(self.creds)
        self.sht = self.gc.open("MUFG Contents")
        self.mufg = self.sht.worksheet('Sheet1')
        self.keys = self.sht.worksheet('Sheet7')
        MUFG_Gsheet.MufgTuple = namedtuple(
            "MufgTuple",
            self._data_values(1)
        )

    def _data_values(self, col_num):
        return self.mufg.col_values(col_num)[self.data_rows_start_end[0]:self.data_rows_start_end[1]]

    def get_colnum_data(self, col_number):
        return MUFG_Gsheet.MufgTuple._make(self._data_values(col_number))

    def get_colname_data(self, col_name):
        return MUFG_Gsheet.MufgTuple._make(self._data_values(self.mufg.get_int_addr(col_name + "1")[1]))

    def get_mufg_guids(self):
        return [(x.col, x.value) for x in self.mufg.range("{}2:{}2".format(*self.mufg_cols_start_end))]

    def get_keycap_guids(self):
        rng = self.mufg.range("{}2:{}2".format(*self.keycap_cols_start_end))
        guids = [(x.col, x.value.split(" ")[1]) for x in rng]
        return guids

    def get_capsule_guids(self):
        rng = self.mufg.range("{}2:{}2".format(*self.cap_cols_start_end))
        return [(x.col, x.value) for x in rng]

    def get_init_transaction_from_column(self, col_number, target="INV"):
        col_vals = self.get_colnum_data(col_number)
        tx = (
            "CR {} ".format(target) +
            " ".join([
                "{} {}".format(count, name)
                for name, count in col_vals._asdict().iteritems()
                if count not in ('', '0', None) and name not in "Keys"
            ])
        )
        return tx


# "CR INV " + " ".join(["{} {}".format(x[1], x[0]) for x in mufg_sht.get_zipped_col('F')[4:] if x[1] not in ('', '0', None)])


def main():
    from Inventory import Inventory, MUFG, Capsule

    inv = Inventory()
    mufg_sht = MUFG_Gsheet()
    inv_colnum = mufg_sht.mufg.get_int_addr("F1")[1]
    tx = mufg_sht.get_init_transaction_from_column(inv_colnum)
    inv.apply_transaction(tx)

    mufgs = mufg_sht.get_mufg_guids()
    for colnum, guid in mufgs:
        tx = mufg_sht.get_init_transaction_from_column(colnum, target=guid)
        inv.add(MUFG(guid))
        inv.apply_transaction(tx)
    for guid in inv.mufgs:
        print ", ".join(
            "{}{}".format(
                x.shortcode,
                x.level if hasattr(x, "has_level") else ""
            )
            for x in inv.mufgs[guid].contents
        )
    caps = mufg_sht.get_capsule_guids()
    for colnum, guid in caps:
        tx = mufg_sht.get_init_transaction_from_column(colnum, target=guid)
        inv.add(Capsule(guid))
        inv.apply_transaction(tx)
    for guid in inv.capsules:
        print ", ".join(
            "{}{}{}".format(
                x.rarity if hasattr(x, "has_rarity") else "",
                x.shortcode,
                x.level if hasattr(x, "has_level") else ""
            )
            for x in inv.capsules[guid].contents
        )


# r = wks.range('L2:X2')
# [x.value for x in r]
# wks.col_values('L')
# wks.col_values(12)
# wks.col_values(1)[:57]