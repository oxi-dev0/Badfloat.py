import math
from decimal import Decimal
import random
from tkinter import *
from tkinter import filedialog
import os
from typing import MappingView

Tk().withdraw()

def SciNot(s):
    t = Decimal(s).normalize().as_tuple()
    return (int(''.join(map(str,t.digits))), t.exponent)


from Classes.Table import FloatTable

#'badfloat1.0' magic header in hex
magicHeader = '626164666c6f6174312e30'

table = FloatTable([])

def HexBytes(a):
    return int(a, 16).to_bytes(len(a) // 2, byteorder='big')

def BinString(b):
    return bin(int.from_bytes(b, byteorder='big'))[2:]

def BinLength(b):
    return len(BinString(b))

def DebugBin(b):
    print()
    #print(BinString(b))
    #print(BinLength(b))
    #print(int(BinString(b), 2)) # - to int
    print(b)
    print(len(b))
    print(int(b, 2))

def FillBin(b, bits, preceding=True):
    d = bits - len(b)
    if preceding:
        return ('0' * d) + b
    else:
        return b + ('0' * d)

def WriteFloat(flt):
    sign = '0'
    mantissa = 0
    exponent = 0
    base = 10
    if flt < 0:
        sign = '1'
    
    data = SciNot(flt)
    ma = (int(abs(data[0])))
    mantissa = bin(ma)[2:]
    #varient: 0 - 8bit, 1 - 16bit, 2 - 32bit, 3 - 64bit
    v = [8, 16, 32, 64]
    maVarient = 0
    maL = len(mantissa)
    if maL > 8:
        maVarient = 1
    if maL > 16:
        maVarient = 2
    if maL > 32:
        maVarient = 3
    if maL > 64:
        mantissa = bin(int(str(abs(data[0]))[:19]))[2:]

    mantissa = FillBin(mantissa, v[maVarient])

    exp = int(abs(data[1]))
    exponent = bin(exp)[2:]
    exVarient = 0
    exL = len(exponent)
    if exL > 8:
        exVarient = 1
    if exL > 16:
        exVarient = 2
    if exL > 32:
        exVarient = 3
    if exL > 64:
        exponent = bin(int(str(abs(data[1]))[:19]))[2:]

    exSign = '0'
    if data[1] < 0:
        exSign = '1'

    exponent = FillBin(exponent, v[exVarient])

    final = sign + exSign + exponent + mantissa

    return (final, maVarient, exVarient)

def WriteFloatTable(table, fp):
    f = open(fp, "wb")

    numFlts = bin(len(table.floats))[2:]
    numVari = 0
    v = [8, 16, 32, 64]
    numL = len(numFlts)
    if numL > 8:
        numVari = 1
    if numL > 16:
        numVari = 2
    if numL > 32:
        numVari = 3
    if numL > 64:
        print("Too many floats")
        return

    numFlts = FillBin(numFlts, v[numVari])
    print(numFlts)
    numVari = bin(numVari)[2:]
    numVari = FillBin(numVari, 2)

    varis = ''
    flts = ''
    for flt in table.floats:
        fltBin, maVarient, exVarient = WriteFloat(flt)
        maVarient = bin(maVarient)[2:]
        maVarient = FillBin(maVarient, 2)
        exVarient = bin(exVarient)[2:]
        exVarient = FillBin(exVarient, 2)
        varis += f"{maVarient}{exVarient}"
        flts += f"{fltBin}"
        print(fltBin)

    final = f"{numVari}{numFlts}{varis}{flts}"
    final = f"{numVari}{numFlts}{varis}"
    fL = len(final)
    mEight = (fL + 7) & (-8)
    final = FillBin(final, mEight, False)
    ba = bytearray(int(final[x:x+8], 2) for x in range(0, len(final), 8))

    f.write(HexBytes(magicHeader))
    f.write(ba)

def ValidateBinary(b):
    nt = int(b[:88], 2)
    h = hex(nt)[2:]
    return h == magicHeader

def ReadFloatTable(fp):
    f = open(fp, "rb")
    data = "".join(f"{n:08b}" for n in f.read())
    print(data) #RAW BINARY

    if data == '':
        print("INVALID FILE")
        return
    if not ValidateBinary(data):
        print("INVALID FILE")
        return

    data = data[89:] #Discard magic word

    print(data)
    
    numVari = data[0:2]
    print(numVari)
    numVari = int(numVari, 2)
    expNum = 8
    if numVari == 1:
        expNum = 16
    if numVari == 2:
        expNum = 32
    if numVari == 3:
        expNum = 64
    print(f"NoF Length: {expNum}b")

    data = data[3:] #Discard num variant

    print(data)

    numFlts = data[:expNum]
    print(numFlts)
    numFlts = int(numFlts, 2)
    print(f"Number of Floats: {numFlts}")

    data = data[expNum:] #Discard NoF

    v = [8, 16, 32, 64]

    varis = []
    varisData = data[:numFlts*4]
    totalFltDataBits = 2 * numFlts # Start with 2 num floats cause sign bits
    for x in range(0, len(varisData), 4):
        variS = varisData[x:x+4]
        maV = variS[0:2]
        expV = variS[2:4]
        maV = int(maV, 2)
        expV = int(expV, 2)
        totalFltDataBits += v[maV] + v[expV] # Add total data bits so can segment floats properly
        varis.append((maV, expV))

    print(f"Float variations: {varis}")

    data = data[numFlts*4:] #Discard float variations

    flts = []
    fltsData = data[:totalFltDataBits]
    
    offset = 0
    index = 0
    while len(flts) < numFlts:
        currentFltData = data[offset:offset + 2+(v[varis[index][0]])+(v[varis[index][1]])]
        sign = currentFltData[0]
        sign = int(sign, 2)
        
        exp = currentFltData[1:2+(v[varis[index][1]])]
        expSign = exp[0]
        expSign = int(expSign, 2)
        exp = exp[1:]
        exp = int(exp, 2)

        mentissa = currentFltData[2+(v[varis[index][1]]):2+(v[varis[index][1]])+(v[varis[index][0]])]
        mentissa = int(mentissa, 2)

        flt = pow(-1, sign) * (mentissa * pow(10, pow(-1, expSign) * exp))
        flts.append(flt)

        offset += 2+(v[varis[index][0]])+(v[varis[index][1]])
        index += 1

    print(f"Floats: {flts}")


    

def ParseAction(inp):
    global table
    if inp.lower() == 'generate':
        floats = []
        amnt = int(input("Amnt: "))
        for i in range(amnt):
            floats.append(1000 - (random.random() * 2000))
        table = FloatTable(floats)
    elif inp.lower() == 'load':
        path = filedialog.askopenfilename(defaultextension='.bf', filetypes=[("BadFloats", '*.bf')],
                initialdir=f"{os.getcwd()}",
                title="Choose table file")
        if path != "":
                ReadFloatTable(path)
        # LOAD
    elif inp.lower() == 'save':
        path = filedialog.asksaveasfilename(defaultextension='.bf', filetypes=[("BadFloats", '*.bf')],
                initialdir=f"{os.getcwd()}",
                title="Choose table file")
        if path != "":
            WriteFloatTable(table, path)
    elif inp.lower() == 'print':
        floats = table.floats
        print(floats)
    elif 'debug' in inp.lower():
        parts = inp.lower().split(" ")
        flt = float(parts[1])
        WriteFloat(flt)

while True:
    print()
    action = input("Action (Generate, Load, Save, Print): ")
    ParseAction(action)
