from pyparsing import *

basic_type = Word(nums) | quotedString

conditional = Word(alphas) + Literal("=") + basic_type
where = Literal("where") + delimitedList(conditional, "or")
select = Literal("select") + Literal("*") + Literal("from") + Word(alphas) + Optional(where)
column_type = Literal("varchar")
column = Word(alphas) + column_type
typeList = delimitedList(column, delim=",")
create = Literal("create table") + Word(alphas) + Literal('(') + typeList + Literal(')')
drop = Literal("drop table") + Word(alphas)
insert = Literal("insert into") + Word(alphas) + Literal('(') + delimitedList(Word(alphas), delim=",") + Literal(")") + Literal('values') + Literal("(") + delimitedList(basic_type, delim=",") + Literal(")")

set_action = Word(alphas) + Literal("=") + basic_type
update_action = delimitedList(set_action, ",")

def update_action_action(s, l, t):
    it = iter(t)
    actions = zip(it, it, it)
    return [actions]
update_action.setParseAction(update_action_action)

def where_action(s, l, t):
    it = iter(t[1:])
    conditionals = zip(it, it, it)
    return [conditionals]
where.setParseAction(where_action)

update = Literal("update") + Word(alphas) + Literal('set') + update_action + where

query_stmt = (create | select | insert| update| drop) + Optional(Literal(";"))

def quotedString_action(s, l, t):
    return t[0][1:-1]
quotedString.setParseAction(quotedString_action)

