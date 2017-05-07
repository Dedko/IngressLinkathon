# worldsim_parser.py
from pyparsing import ParserElement, oneOf, hexnums, QuotedString
from pyparsing import Optional, Suppress, Keyword, Word, Literal, CaselessKeyword
from pyparsing import Or, OneOrMore, Forward, Group
from pyparsing import pyparsing_common as ppc
identifier = ppc.identifier
integer = ppc.integer
real = ppc.real
numeric = ppc.number

""" BNF:
<pid> ::= <numeric>
<portal-id> ::= ID <portalname> '=' <pid>

<link-request> ::= LINK <portal> [TO] <portal> [AS <id>] [FORWARD]

<field-request> ::= FIELD <portal> <portal> <portal> [AS <id>]

capture-request> ::= CAPTURE <portalname> [AS <id>]

<destroy-link-request> ::= DESTROY <link-id> [AS <id>]
<destroy-portal-request> ::= DESTROY <portalname> [AS <id>]

<deploy-request> ::= DEPLOY <portalname> [<resonator-list>] [AS <id>]
<guid-command> ::= GUID <pid> <portalguid>

<link-ref> ::= <id> | <link-request>
<field-ref> ::= <id> | <field-request>
<capture-ref> ::= <id> | <capture-request>
<destroy-link-ref> ::= <id> | <destroy-link-request>
<destroy-portal-ref> ::= <id> | <destroy-portal-request>
<deploy-ref> ::= <id> | <deploy-request>

<link-sequence> ::= <link-ref> [<link-sequence>]

<portal> ::= <portalname> | <portalguid> | <latlng>

<latlng> ::= <lat>[,] <lng>
<intorfloat> ::= <digit>+ ['.' <digit>+]
<lat> ::= ['-'] <intorfloat | <intorfloat>  ['N' | 'S']
<lng> ::= ['-'] <intorfloat> | <intorfloat> ['E' | 'W']

<portalguid> ::= <hexdigit>+ '.' <hexdigit>+

<id> ::= <hexdigit>+

<command-entry> ::= <field-ref> |
                    <capture-ref> |
                    <destroy-link-ref>
                    <destroy-portal-ref> |
                    <deploy-ref> |
                    <link-sequence>

<command-sequence> ::= SEQ <command-entry> [<command-sequence>]

<locate-command> ::= LOCATE <portal> [AT] <latlng>
"""


class WorldsimParser(ParserElement):
    def __init__(self):
        super(WorldsimParser, self).__init__()
        pid = Word(hexnums)
        portalname = (QuotedString('"') ^ QuotedString("'"))
        portalguid = Word(hexnums + '.' + hexnums, exact=35)
        as_id = Optional(Suppress(CaselessKeyword('AS')) + pid)
        link_id = pid
        portal_id = (
            Suppress(Keyword('ID')) +
            portalname +
            Suppress(Literal('=') | CaselessKeyword('AS')) +
            pid
        ).setParseAction(self.id_command_action)
        guid_command = (
            Suppress(Keyword('GUID')) +
            pid +
            portalguid
        ).setParseAction(self.guid_command_action)
        # <lat> ::= ['-'] <intorfloat | <intorfloat>  ['N' | 'S']
        lat = real + (Literal('N') ^ Literal('S'))
        # <lng> ::= ['-'] <intorfloat> | <intorfloat> ['E' | 'W']
        lng = real + (Literal('E') ^ Literal('W'))
        # <latlng> ::= <lat>[,] <lng>
        latlng = lat + Suppress(Optional(Literal(','))) + lng
        # <portal> ::= <portalname> | <portalguid> | <latlng>
        portal = portalname | portalguid | latlng | pid
        link_request = (
            Suppress(Keyword('LINK')) +
            portal +
            Optional(Suppress(Literal('TO'))) +
            portal +
            as_id +
            Optional(Keyword('FORWARD'))
        ).setParseAction(self.link_request_action)
        field_request = (
            Suppress(Keyword('FIELD')) +
            portal + portal + portal +
            as_id
        ).setParseAction(self.field_request_action)
        capture_request = (
            Suppress(Keyword('CAPTURE')) +
            portalname +
            as_id
        ).setParseAction(self.capture_request_action)
        destroy_link_request = (
            Suppress(Keyword('DESTROY')) +
            link_id +
            as_id
        ).setParseAction(self.destroy_link_request_action)
        resonator_list = (
            OneOrMore(
                Literal('R') +
                oneOf(['1', '2', '3', '4', '5', '6', '7', '8'])
            )
        )
        deploy_request = (
            Suppress(Keyword('DEPLOY')) +
            portalname +
            resonator_list +
            as_id
        ).setParseAction(self.deploy_request_action)
        link_ref = pid | link_request
        field_ref = (
            pid | field_request
        )
    # <capture-ref> ::= <id> | <capture-request>
        capture_ref = Forward()
        capture_ref <<= (
            pid | capture_request
        )
    # <destroy-link-ref> ::= <id> | <destroy-link-request>
        destroy_link_ref = Forward()
        destroy_link_ref <<= (
            pid | destroy_link_ref
        )
    # <destroy-portal-ref> ::= <id> | <destroy-portal-request>
        destroy_portal_ref = Forward()
        destroy_portal_ref = (
            pid | destroy_portal_ref
        )
    # <deploy-ref> ::= <id> | <deploy-request>
        deploy_ref = (pid | deploy_request)
    # <link-sequence> ::= <link-ref> [<link-sequence>]
        link_sequence = Forward()
        link_sequence <<= (
            link_ref + Optional(link_sequence)
        ).setParseAction(self.link_sequence_action)

    # <intorfloat> ::= <digit>+ ['.' <digit>+]
    # <portalguid> ::= <id>
    # <id> ::= <hexdigit>+

    # <command-entry> ::= <field-ref> |
    #                     <capture-ref> |
    #                     <destroy-link-ref>
    #                     <destroy-portal-ref> |
    #                     <deploy-ref> |
    #                     <link-sequence>
        command_entry = (
            field_ref |
            capture_ref |
            destroy_link_ref |
            destroy_portal_ref |
            deploy_ref |
            link_sequence
        ).setParseAction(self.command_entry_action)
    # <command-sequence> ::= SEQ <command-entry> [<command-sequence>]
        command_sequence = Forward()
        command_sequence <<= (
            Suppress(Keyword("SEQ")) +
            command_entry +
            Optional(command_sequence)
        ).setParseAction(self.command_sequence_action)
    # <locate-command> ::= LOCATE <portal> [AT] <latlng>
        locate_command = (
            Suppress(Keyword('LOCATE')) +
            portal +
            Suppress(Optional(Keyword('AT'))) +
            latlng
        ).setParseAction(self.locate_command_action)
        # <move-command> ::= MOVE <latlng>
        move_command = (
            Suppress(Keyword('MOVE')) + latlng
        ).setParseAction(self.move_command_action)
        # self.parser = OneOrMore(
        #     command_entry ^
        #     portal_id ^
        #     guid_command
        # )
        self.parser = OneOrMore(
            Group(
                portal_id ^
                field_request ^
                link_request ^
                destroy_link_request ^
                locate_command ^
                guid_command ^
                move_command
            )
        )

    def parseString(self, instring):
        return self.parser.parseString(instring)

    # command hooks - subclass and override
    def id_command_action(self, toks):
        pass

    def guid_command_action(self, toks):
        pass

    def link_request_action(self, toks):
        pass

    def field_request_action(self, toks):
        pass

    def capture_request_action(self, toks):
        pass

    def destroy_link_request_action(self, toks):
        pass

    def deploy_request_action(self, toks):
        pass

    def link_sequence_action(self, toks):
        pass

    def command_entry_action(self, toks):
        pass

    def command_sequence_action(self, toks):
        pass

    def locate_command_action(self, toks):
        pass

    def move_command_action(self, toks):
        pass
