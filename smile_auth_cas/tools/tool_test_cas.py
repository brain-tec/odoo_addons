import xmlrpc.client
import pprint


url = 'http://localhost:8069'
common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
common.version()
base = 'db'
username = 'admin'
pwd = 'x'


param_object = "{}/xmlrpc/object".format(url)
common_obj = "{}/xmlrpc/common".format(url)
sock_common = xmlrpc.client.ServerProxy(common_obj)
uid = sock_common.login(base, 'admin', pwd)
sock = xmlrpc.client.ServerProxy(param_object)



class CasTest:
    def __init__(self):
        self.menu = """
    ---  Menu --- 

0: Print Menu
1: List users CAS fields('login', 'user_cas_id', 'name', 'active')
2: Update users field user_cas_id
3: Update users login
4: Search users by login
5: toggle CAS (1, 0)

"""

    def start(self):
        loop = True
        while loop:
            self.print_menu()
            entry = str(input('-- > '))
            if entry and entry.split(' '):
                entry = entry.split(' ')
                choice = entry[0]
                params = entry[1:]
            else:
                choice = entry
                params = []

            if choice not in ('1','2','3', '4', '5'):
                self.print_menu()
            elif choice == '1':
                self.list_users(params)
                loop = False
            elif choice == '2':
                self.update_user_cas_id(
                    params[0] if len(params) else False,
                    params[1] if len(params) > 0 else False)
                loop = False
            elif choice == '3':
                self.update_user_login(
                    params[0] if len(params) else False,
                    params[1] if len(params) > 0 else False)
                loop = False
            elif choice == '4':
                self.search_user_login(params[0] if len(params) else False)
                loop = False
            elif choice == '5':
                self.toggle_cas(params[0] if len(params) else False)
                loop = False

    def print_menu(self):
        print(self.menu)
    
    def list_users(self, domain=False):
        if not domain:
            domain = ['user_cas_id', '!=', False]

        cas_user = sock.execute_kw(
            base, uid, pwd, 'res.users', 'search_read', [
                [domain]
                ], {'fields': ['login', 'user_cas_id', 'name', 'active'], 'context' :{'active_test': False}}, )
        pprint.pprint(cas_user)
        self.start()

    def update_user_cas_id(self, user_id=False, new_cas_id=False):
        if not user_id:
            user_id = int(input('User ID ? '))
        if not new_cas_id:
            new_cas_id = input('New user_cas_id ? ')

        sock.execute_kw(
            base, uid, pwd, 'res.users', 'write', [[int(user_id)], {'user_cas_id': new_cas_id}]
            )
        self.list_users(domain=['id', '=', int(user_id)])
        self.start()

    def update_user_login(self, user_id=False, new_login=False):
        if not user_id:
            user_id = int(input('User ID ? '))
        if not new_login:
            new_login = input('New login ? ')

        try:
            sock.execute_kw(
                base, uid, pwd, 'res.users', 'write', [[int(user_id)], {'login': new_login}]
                )
        except Exception as e:
            print(e)
        self.list_users(domain=['id', '=', user_id])
        self.start()

    def search_user_login(self, login=False):
        if not login:
            login = input('Login ? ')
        self.list_users(domain=['login', '=', login])
        self.start()

    def toggle_cas(self, state=False):
        if not state:
            state = input('State (1/0)? ')
        res_id = sock.execute_kw(
            base, uid, pwd, 'ir.config_parameter', 'search_read', [
                [['key', '=', 'auth.cas']]
                ], {'fields': ['id']})
        sock.execute_kw(
                base, uid, pwd, 'ir.config_parameter', 'write', [res_id[0].get('id'), {'value': state}]
                )
        res_id = sock.execute_kw(
            base, uid, pwd, 'ir.config_parameter', 'search_read', [
                [['key', '=', 'auth.cas']]
                ], {'fields': ['value']})
        print(res_id)
        self.start()


CasTest().start()
