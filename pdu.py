#!/usr/bin/python3
""" 
* APC Orchestrator
' Date: 7/11/2018
"""

import os
import sys
import readline
import subprocess
import time
import argparse

class Printer(object):

    def __init__(self, port=1):
        self.port = port
        self.colorg = '\033[92m'
        self.colorr = '\033[91m'
        self.colorend = '\033[0m'

    def menu(self):
        ans = '0'
        os.system('clear')
        print('*'* 64)
        print('1). Status of all outlets')
        print('2). Status of an outlet')
        print('3). Change outlet state')
        print('4). Exit')
        print('-'*64)
        print('')
        ans = input('Please make a selection: ')
        return ans

    def outlet_status(self, pstatus,name):
        _status = 'on' if pstatus == '1' else 'off' 
        _color = self.colorg if pstatus == '1' else self.colorr
        print('\nOutlet {}: {}   ---> {}{}{}'.format(self.port,name,_color,_status,self.colorend))

            
class Outlet_tasks(object):

    def __init__(self,ip_addr,outlet_num=0,user='apc',version='v3'):
        self.ip_addr = ip_addr
        self.version = '-{}'.format(version)
        self.user = user
        self.outlet = outlet_num
        self.oid =  '1.3.6.1.4.1.318.1.1.4.4.2.1.3.'
        self.oid_name = '1.3.6.1.4.1.318.1.1.4.4.2.1.4.'
    def outlet_check(self,port):
        _oid_port = self.oid + str(port)
        _result = subprocess.Popen(['snmpwalk', self.version, '-l', 'noauthnopriv',  '-u', self.user, self.ip_addr, _oid_port], stdout=subprocess.PIPE )
        _result = _result.stdout.read()
        _result = _result.decode().strip(' ').split(' ')
        result = _result[3].strip('\n')
        return result


    def outlet_control(self, port, on_off):
        _power = '1' if on_off == 'on' else '2'
        _oid_port = self.oid + str(port) 
        _result = subprocess.Popen(['snmpset', self.version, '-l', 'noauthnopriv',  '-u', self.user, self.ip_addr, _oid_port, 'i',  _power], stdout=subprocess.PIPE )
        _result = _result.stdout.read()
        _result = _result.decode().strip(' ').split(' ')
        result = _result[3].strip('\n')
        return result

    def get_name(self, port):
        _oid_name = self.oid_name + str(port)
        _result = subprocess.Popen(['snmpwalk', self.version, '-l', 'noauthnopriv',  '-u', self.user, self.ip_addr, _oid_name], stdout=subprocess.PIPE )
        _result = _result.stdout.read()
        _result = _result.decode().strip(' ').split(' ')
        try:
            result = _result[3]
            return result
        except IndexError:
            pass
        #return result

def main():
    _ans = '0'
    if os.name == 'nt': print('This tool is only supported in linux/bsd variant operating systems'), sys.exit(1)
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument('--interactive', help='run the tool in interactive mode', required=False, action='store_true')
        parser.add_argument('--device', help='define the hostname or IP address', required=True)
        parser.add_argument('--community', help='community string for snmp', required=False)
        parser.add_argument('--port', help='community string for snmp', required=False)
        parser.add_argument('--state', help='community string for snmp', required=False)
        args = parser.parse_args()
        if args.interactive: _ans = Printer().menu()
        while True:
            port = 1
            if _ans == '1':
                while port != 17:
                    all_result = Outlet_tasks(args.device).outlet_check(port)
                    name = Outlet_tasks(args.device).get_name(port)
                    Printer(port).outlet_status(all_result,name)
                    port += 1
            elif _ans == '2' or args.port is not None: 
                if args.port: specific_port = args.port
                else: specific_port = input('Which outlet?: ' )
                specific_result = Outlet_tasks(args.device).outlet_check(specific_port)
                name = Outlet_tasks(args.device).get_name(specific_port)
                Printer(specific_port).outlet_status(specific_result,name)
            elif _ans == '3' or args.state is not None:
                if args.state: on_off = args.state
                else:
                    specific_port = input('Which outlet?: ' )
                    specific_result = Outlet_tasks(args.device).outlet_check(specific_port)
                    on_off = input('Power On/Off: ')
                _pstatus = 'on' if specific_result == '1' else 'off'
                if on_off.lower() == _pstatus:
                    print('port is already powered {}{}{}. Please try again'.format(Printer().colorr,_pstatus, Printer().colorend))
                else:
                    result = Outlet_tasks(args.device).outlet_control(specific_port, on_off)
                    print('\nport {} has been successfully powered {}!! Confirmation below: '.format(specific_port, on_off.lower()))
                    Printer(specific_port).outlet_status(result)
            elif _ans == '4':
                print('Exising tool. Goodbye!')
                sys.exit(1)
            elif args.port: break
            _con = input('Please press enter to continue...')
            _ans = Printer().menu()
    except(KeyboardInterrupt):
        print('')
        print('Existing script')
        exit()

if __name__ == '__main__':
    main()

