# Networking
# Rabia Mohiuddin
# Winter 2018

import threading
import queue
import time
import pickle
import socket
import platform
import multiprocessing as mp

''' Use 2 queues because 1 queue requires more work (work in synchronizing the parent and the child). 
    One way to synchronize is to use event. 
    Need to synchronize parent and data because 2 processes are not guaranteed to work one after the other 
    as they are working in parallel.
'''

HOST = 'localhost'      
PORT = 5255

def threadWithQueueINT(num):
    ''' Creates child thread to increment integer back and forth with main thread in a loop using a queue
        Returns the ratio:  number of one-way data transfer / time difference.
    '''
    qParent = queue.Queue()    
    qChild = queue.Queue()
    tChild = threading.Thread(target = childThreadINT, args=(qParent, qChild,))    
    try:
        qChild.put(num)
        tChild.start() 
        if qParent.get() != 2:
            raise Exception("Data not expected")
    except Exception as e:
        print(str(e))
        return
    
    #print("Connection good")
    num = 0
    loop = 0
    start = time.time()
    while loop < 10000:
        num += 1
        qChild.put(num)
        num = qParent.get()
        loop += 1    

    end = time.time()
    qChild.put(0)
    tChild.join()
    try:
        if num != (2*loop):
            raise Exception("Data not expected after completion of loop")
    except Exception as e:
        print(str(e))
        return
    
    return loop/float((end-start))


def childThreadINT(qParent, qChild):
    ''' Receives data, increments, and puts back in queue'''
    item = qChild.get()
    while item != 0:
        item += 1
        qParent.put(item)
        item = qChild.get()

    
def threadWithSocketINT(num):      # CLIENT
    ''' Creates child thread to increment integer back and forth with main thread in a loop using a socket
        Returns the ratio:  number of one-way data transfer / time difference.
    '''    
    tChild = threading.Thread(target = serverINT) 
    tChild.start()         
    with socket.socket() as s :     # open socket   
        s.connect((HOST, PORT))     # connect to server with 2 IDs: hostname & port
                                    # connect is blocking as well
        #print("Client connect to:", HOST, "port:", PORT)
        
        try:
            s.send(pickle.dumps(num))
            fromServer = pickle.loads(s.recv(1024))
            if fromServer != 2:
                raise Exception("Data not expected")
        except Exception as e:
            print(str(e))
            return        
        
        #print("Connection good")
        fromServer = 0
        loop = 0
        start = time.time()
        while loop < 10000:
            fromServer += 1
            s.send(pickle.dumps(fromServer))
            fromServer = pickle.loads(s.recv(1024))
            loop += 1    
    
        end = time.time()
        s.send(pickle.dumps(0))
        tChild.join()
        try:
            if fromServer != (2*loop):
                raise Exception("Data not expected after completion of loop")
        except Exception as e:
            print(str(e))
            return
        
        return loop/float((end-start))        
        
        
def serverINT():
    ''' Receives data, increments, and puts back in socket'''    
    with socket.socket() as s : # open socket
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))    # makes socket available at PORT num with hostname "hostname"
        #print("Server hostname:", HOST, "port:", PORT)
    
        s.listen()  # activate the listener at the port
        (conn, addr) = s.accept()       # accept is blocking until it gets request
        # accept will create a new socket called conn. addr is the address of the client
        
        fromClient = pickle.loads(conn.recv(1024))                            
        while True:     # sit there and keep responding to client
            if fromClient == 0:
                break   
            fromClient += 1
            conn.send(pickle.dumps(fromClient))
            fromClient = pickle.loads(conn.recv(1024))     
            

def processWithQueueINT(num):
    ''' Creates child process to increment integer back and forth with main process in a loop using a queue
        Returns the ratio:  number of one-way data transfer / time difference.
    '''    
    qParent = mp.Queue()    
    qChild = mp.Queue()
    psChild = mp.Process(target = childProcessINT, args=(qParent, qChild,))    
    try:
        qChild.put(num)
        psChild.start() 
        if qParent.get() != 2:
            raise Exception("Data not expected")
    except Exception as e:
        print(str(e))
        return
    
    #print("Connection good")
    num = 0
    loop = 0
    start = time.time()
    while loop < 10000:
        num += 1
        qChild.put(num)
        num = qParent.get()
        loop += 1    

    end = time.time()
    qChild.put(0)
    psChild.join()
    try:
        if num != (2*loop):
            raise Exception("Data not expected after completion of loop")
    except Exception as e:
        print(str(e))
        return
    
    return loop/float((end-start))  


def childProcessINT(qParent, qChild):
    ''' Receives data, increments, and puts back in queue'''    
    item = qChild.get()
    while item != 0:
        item += 1
        qParent.put(item)
        item = qChild.get()


def processWithSocketINT(num):
    ''' Creates child process to increment integer back and forth with main process in a loop using a socket
        Returns the ratio:  number of one-way data transfer / time difference.
    '''       
    psChild = mp.Process(target = serverINT) 
    psChild.start()  
    time.sleep(1)
    with socket.socket() as s :     # open socket   
        s.connect((HOST, PORT))     # connect to server with 2 IDs: hostname & port
                                    # connect is blocking as well
        #print("Client connect to:", HOST, "port:", PORT)
        
        try:
            s.send(pickle.dumps(num))
            fromServer = pickle.loads(s.recv(1024))
            if fromServer != 2:
                raise Exception("Data not expected")
        except Exception as e:
            print(str(e))
            return        
        
        #print("Connection good")
        fromServer = 0
        loop = 0
        start = time.time()
        while loop < 10000:
            fromServer += 1
            s.send(pickle.dumps(fromServer))
            fromServer = pickle.loads(s.recv(1024))
            loop += 1    
    
        end = time.time()
        s.send(pickle.dumps(0))
        psChild.join()
        try:
            if fromServer != (2*loop):
                raise Exception("Data not expected after completion of loop")
        except Exception as e:
            print(str(e))
            return
        return loop/float((end-start))        
    

def threadWithQueueLIST(myList):
    ''' Creates child thread to append list back and forth with main thread in a loop using a queue
        Returns the ratio:  number of one-way data transfer / time difference.
    '''    
    qParent = queue.Queue()    
    qChild = queue.Queue()
    tChild = threading.Thread(target = childThreadLIST, args=(qParent, qChild,))    
    try:
        myList.append(0)        
        qChild.put(myList)
        tChild.start() 
        if qParent.get() != [0,1]:
            raise Exception("Data not expected")
    except Exception as e:
        print(str(e))
        return
    
    #print("Connection good")
    myList = []
    loop = 0
    start = time.time()
    while loop < 300:
        myList.append(0)
        qChild.put(myList)
        myList = qParent.get()
        loop += 1    

    end = time.time()
    qChild.put([])
    tChild.join()
    try:
        if len(myList) != (2*loop):
            raise Exception("Data not expected after completion of loop")
    except Exception as e:
        print(str(e))
        return
    
    return loop/float((end-start))    

def childThreadLIST(qParent, qChild):
    ''' Receives data, appends, and puts back in queue'''    
    item = qChild.get()
    while item != []:
        item.append(1)
        qParent.put(item)
        item = qChild.get()
def threadWithSocketLIST(myList):      # CLIENT
    ''' Creates child thread to append list back and forth with main thread in a loop using a queue
        Returns the ratio:  number of one-way data transfer / time difference.
    '''    
    tChild = threading.Thread(target = serverLIST) 
    tChild.start() 
    time.sleep(1)
    with socket.socket() as s :     # open socket   
        s.connect((HOST, PORT))     # connect to server with 2 IDs: hostname & port
                                    # connect is blocking as well
        #print("Client connect to:", HOST, "port:", PORT)
        
        try:
            myList.append(0)
            s.send(pickle.dumps(myList))
            fromServer = pickle.loads(s.recv(4096))
            if fromServer != [0,1]:
                raise Exception("Data not expected")
        except Exception as e:
            print(str(e))
            return        
        
        #print("Connection good")
        fromServer = []
        loop = 0
        start = time.time()
        while loop < 300:
            fromServer.append(0)
            s.send(pickle.dumps(fromServer))
            fromServer = pickle.loads(s.recv(4096))
            loop += 1               
    
        end = time.time()
        s.send(pickle.dumps([]))
        tChild.join()
        try:
            if len(fromServer) != (2*loop):
                raise Exception("Data not expected after completion of loop")
        except Exception as e:
            print(str(e))
            return
        
        return loop/float((end-start))        

        
def serverLIST():
    ''' Receives data, appends, and puts back in socket'''    
    
    with socket.socket() as s : # open socket
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))    # makes socket available at PORT num with hostname "hostname"
        #print("Server hostname:", HOST, "port:", PORT)
    
        s.listen()  # activate the listener at the port
        (conn, addr) = s.accept()       # accept is blocking until it gets request
        # accept will create a new socket called conn. addr is the address of the client
        
        fromClient = pickle.loads(conn.recv(4096))                            
        while True:     # sit there and keep responding to client
            if fromClient == []:
                break   
            fromClient.append(1)
            conn.send(pickle.dumps(fromClient))
            fromClient = pickle.loads(conn.recv(4096))     
            

def processWithQueueLIST(myList):
    ''' Creates child process to append list back and forth with main process in a loop using a queue
        Returns the ratio:  number of one-way data transfer / time difference.
    '''       
    qParent = mp.Queue()    
    qChild = mp.Queue()
    psChild = mp.Process(target = childProcessLIST, args=(qParent, qChild,))    
    try:
        myList.append(0)
        qChild.put(myList)
        psChild.start() 
        if qParent.get() != [0,1]:
            raise Exception("Data not expected")
    except Exception as e:
        print(str(e))
        return
    
    #print("Connection good")
    myList = []
    loop = 0
    start = time.time()
    while loop < 300:
        myList.append(0)
        qChild.put(myList)
        myList = qParent.get()
        loop += 1    

    end = time.time()
    qChild.put([])
    psChild.join()
    try:
        if len(myList) != (2*loop):
            raise Exception("Data not expected after completion of loop")
    except Exception as e:
        print(str(e))
        return
    
    return loop/float((end-start))

def childProcessLIST(qParent, qChild):
    ''' Receives data, appends, and puts back in queue'''    
    item = qChild.get()
    while item != []:
        item.append(1)
        qParent.put(item)
        item = qChild.get()



def processWithSocketLIST(myList):
    ''' Creates child process to append list back and forth with main process in a loop using a socket
        Returns the ratio:  number of one-way data transfer / time difference.
    '''       
    psChild = mp.Process(target = serverLIST) 
    psChild.start()  
    time.sleep(1)
    with socket.socket() as s :     # open socket   
        s.connect((HOST, PORT))     # connect to server with 2 IDs: hostname & port
                                    # connect is blocking as well
        #print("Client connect to:", HOST, "port:", PORT)
        
        try:
            myList.append(0)
            s.send(pickle.dumps(myList))
            fromServer = pickle.loads(s.recv(4096))
            if fromServer != [0,1]:
                raise Exception("Data not expected")
        except Exception as e:
            print(str(e))
            return        
        
        #print("Connection good")
        fromServer = []
        loop = 0
        start = time.time()
        while loop < 300:
            fromServer.append(0)
            s.send(pickle.dumps(fromServer))
            fromServer = pickle.loads(s.recv(4096))
            loop += 1    
    
        end = time.time()
        s.send(pickle.dumps([]))
        psChild.join()
        try:
            if len(fromServer) != (2*loop):
                raise Exception("Data not expected after completion of loop")
        except Exception as e:
            print(str(e))
            return
        return loop/float((end-start))        

def main():
    if __name__ == '__main__' :
        print("OS:", platform.system())
        print("Platform:", platform.processor())
        print("Cores:", mp.cpu_count())
        
        tQint = threadWithQueueINT(1)        
        tSint = threadWithSocketINT(1)        
        pQint = processWithQueueINT(1)
        pSint = processWithSocketINT(1)        
        tQlist = threadWithQueueLIST([])        
        tSlist = threadWithSocketLIST([])        
        pQlist = processWithQueueLIST([])        
        pSlist = processWithSocketLIST([])
        
        print("%16s %10s %10s" % ("", "Thread", "Process"))
        print("%-8s %-8s %10.2f %10.2f" % ("Queue", "Integer", tQint, pQint))
        print("%-8s %-8s %10.2f %10.2f" % ("Queue", "List", tQlist, pQlist))
        print("%-8s %-8s %10.2f %10.2f" % ("Socket", "Integer", tSint, pSint))
        print("%-8s %-8s %10.2f %10.2f" % ("Socket", "List", tSlist, pSlist))
        
main()

''' Results
                     Thread    Process
Queue    Integer    22056.94    9491.75
Queue    List       28818.25    7489.16
Socket   Integer    30602.47   35952.34
Socket   List       12091.40   13097.51

                     Thread    Process
Queue    Integer    27929.37    8837.23
Queue    List       28601.43    7468.27
Socket   Integer    36269.20   34745.28
Socket   List       10535.19   12358.85

                     Thread    Process
Queue    Integer    27446.67    8927.15
Queue    List       28620.94    7589.94
Socket   Integer    35884.73   32382.27
Socket   List       10102.78   13870.97

---------------------------------------------------------------------
Conclusion

Processes are significantly slower with Queues but faster when using sockets. When using sockets, integers took about 1/3 of the time as lists, expectedly as they are a smaller data size. Socket processes are slightly faster, however not all the time. Overall, when looking at all the data as a whole, threads are faster due to not having to go back and forth between cores. Sockets are better for small data types while queues are better for larger data types.  

'''
