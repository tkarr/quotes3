from ldap3 import Server, Connection, SEARCH_SCOPE_WHOLE_SUBTREE


def authenticate(username, pwd):
    '''
    takes username and password and tries to log into dc.
    if fails, returns false, else it searches ad for
    username that is in SBSUsers and in the Internal Web Admins
    Security Group. if it finds it, return a dict with name,
    username, and email, else false
    '''
    
    groups = [{"full_name": "Internal Web Admins", "short_name": "admins"}, 
              {"full_name": "Internal Web Drafters", "short_name": "drafters"},
              {"full_name": "Internal Web Designers","short_name": "designers"},
              {"full_name": "Internal Web Customer Service", "short_name": "customer_service"},
              {"full_name": "Internal Web Warranty", "short_name": "warranty"}]
 
    try:
        username = username.lower()
        s = Server('10.1.1.3')
        c = Connection(s,
                       user='{0}@lti.local'.format(username),
                       password=pwd,
                       auto_bind=True)
        with c:       
            # if connected to server
            if c.bound:
                for group in groups:
                    # query ldap for user by sAMAccountName and if member of group
                    c.search(
                        search_base='''OU=SBSUSers,OU=Users,
                                       OU=MyBusiness,DC=lti,DC=local''',
                        search_filter='''(&(objectClass=user)
                                           (sAmAccountName={0})
                                           (memberOf=CN={1},
                                             OU=Security Groups,
                                             OU=MyBusiness,
                                             DC=lti,
                                             DC=local))'''.format(username, group['full_name']),
                        search_scope=SEARCH_SCOPE_WHOLE_SUBTREE,
                        attributes=['name', 'mail'])
                    if c.response:
                        g = group['short_name']
                        break
                else:
                    # if not in one of the above groups, but valid user: group = read_only
                    c.search(
                        search_base='''OU=SBSUsers,OU=Users,OU=MyBusiness,DC=lti,DC=local''',
                        search_filter='''(&(objectClass=user)
                                           (sAmAccountName={0}))'''.format(username),
                        search_scope=SEARCH_SCOPE_WHOLE_SUBTREE,
                        attributes=['name', 'mail'])
                    if c.response:
                        g = 'read_only'

                # assign attributes
                info = dict()
                info['username'] = username
                info['name'] = c.response[0]['attributes']['name'][0]
                info['email'] = c.response[0]['attributes']['mail'][0]
                info['group'] = g
                return info
            else:
                return False
    except:
        return False


if __name__ == "__main__":
    print(str(authenticate('bblount', 'password')))
