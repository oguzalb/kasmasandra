from parsesql import query_stmt
from StringIO import StringIO

class QueryError(Exception):
    pass


class Keyspace(dict):
    def get_table(self, name):
        if name not in self:
            raise QueryError("Table does not exist!")
        return self[name]

    def create_table(self, name, columns):
        if name in self:
            raise QueryError("Table already exists!")
        table = Table(columns)
        self[name] = table

    def drop_table(self, name):
        self.get_table(name)
        del self[name]

    def __repr__(self):
        s = StringIO()
        for name, table in self.iteritems():
            s.write("=== Table %s ===\n%s" % (name, table))
        return s.getvalue()


class Table(list):
    def __init__(self, columns):
        self.columns = dict(columns)

    def select(self, conditionals):
        if not conditionals:
            return self
        results = []
        for r in self:
            for c in conditionals:
                where_column = c[0]
                where_value = c[2]
                if where_column in r and r[where_column] == where_value:
                    results.append(r)
                    break
 
        return results

    def insert(self, columns, values):
        if set(self.columns) != set(columns):
            raise QueryError("columns don't match")
        if len(columns) != len(values):
            raise QueryError("values length and columns lengt don't match")
        self.append(dict(zip(columns, values)))

    def update(self, actions, conditionals):
        count = 0
        for r in self:
            for c in conditionals:
                where_column = c[0]
                where_value = c[2]
                if where_column in r and r[where_column] == where_value:
                    count += 1
                    for action in actions:
                        column_name = action[0]
                        column_value = action[2]
                        r[column_name] = column_value
        return count

    def __repr__(self):
        return "columns:\n%s\nrows:\n%s" % (self.columns, list.__repr__(self))


def get_parenthesis(lst):
    next(lst)
    for i in lst:
        if i == ')':
            break
        yield i


keyspace = Keyspace()


def query(s):
    print "query: %s" % s
    t = query_stmt.parseString(s)
    if t[0] == "create table":
        it = iter(t[3:-1])
        keyspace.create_table(t[1], zip(it, it))
    elif t[0] == "drop table":
        keyspace.drop_table(t[1])
    elif t[0] == "select":
        table = keyspace.get_table(t[3])
        # not a nice way of checking
        print "select result: %s" % table.select(t[4] if len(t) > 5 else [])
    elif t[0] == "insert into":
        it = iter(t[2:])
        column_names = list(get_parenthesis(it))
        next(it)
        values = list(get_parenthesis(it))
        table = keyspace.get_table(t[1])
        table.insert(column_names, values)
    elif t[0] == "update":
        table = keyspace.get_table(t[1])
        count = table.update(t[3], t[4])
        print "updated %s" % count
    else:
        raise ValueError("")

query("create table users (name varchar, surname varchar)")
query("insert into users (name, surname) values (\"oguz\", \"albayrak\");")
query("insert into users (name, surname) values (\"oguz2\", \"albayrak2\");")
query("select * from users;")
query("select * from users where name = \"oguz\" or surname = \"albayrak\";")
query("update users set name = \"someone\", surname = \"somesurname\" where name = \"oguz\", surname = \"albayrak\";")
#query("drop table users;")
print keyspace
