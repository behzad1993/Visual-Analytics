import threading

import single
import multiple
import proxy

def proxy1():
    proxy.run_proxy()

def app1():
    single.run_server()

def app2():
    multiple.run_server()

if __name__=='__main__':
    t1 = threading.Thread(target=app1)
    t1.start()
    
    t2 = threading.Thread(target=app2)
    t2.start()
    
    t3 = threading.Thread(target=proxy1)
    t3.start()