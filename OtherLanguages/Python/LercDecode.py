#-------------------------------------------------------------------------------
#   Copyright 2016 Esri
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
#   A copy of the license and additional notices are located with the
#   source distribution at:
#
#   http://github.com/Esri/lerc/
#
#   Contributors:  Thomas Maurer
#
#-------------------------------------------------------------------------------

import array
import sys
from timeit import default_timer as timer
from ctypes import *

lercDll = CDLL ("D:/GitHub/LercOpenSource/bin/Windows/Lerc64.dll")  # windows
#lercDll = CDLL ("../../bin/Linux/Lerc64.so")  # linux

#-------------------------------------------------------------------------------
#
# from include/Lerc_c_api.h :
#
# typedef unsigned int lerc_status;
#
# // Call this to get info about the compressed Lerc blob. Optional. 
# // Info returned in infoArray is { version, dataType, nDim, nCols, nRows, nBands, nValidPixels, blobSize },
# // Info returned in dataRangeArray is { zMin, zMax, maxZErrorUsed }, see Lerc_types.h .
#
# lerc_status lerc_getBlobInfo( const unsigned char* pLercBlob,
#                               unsigned int blobSize, 
#                               unsigned int* infoArray,
#                               double* dataRangeArray,
#                               int infoArraySize,
#                               int dataRangeArraySize);
#
#-------------------------------------------------------------------------------

lercDll.lerc_getBlobInfo.restype = c_uint
lercDll.lerc_getBlobInfo.argtypes = (c_char_p, c_uint, POINTER(c_uint), POINTER(c_double), c_int, c_int)

def lercGetBlobInfo(compressedBytes, infoArr, dataRangeArr):
    global lercDll
    
    nBytes = len(compressedBytes)
    len0 = min(8, len(infoArr))
    len1 = min(3, len(dataRangeArr))
    
    ptr0 = cast((c_uint * len0)(), POINTER(c_uint))
    ptr1 = cast((c_double * len1)(), POINTER(c_double))
    
    result = lercDll.lerc_getBlobInfo(c_char_p(compressedBytes), nBytes, ptr0, ptr1, len0, len1)
    if result > 0:
        return result
    
    for i in range(len0):
        infoArr[i] = ptr0[i]
    for i in range(len1):
        dataRangeArr[i] = ptr1[i]

    return result

#-------------------------------------------------------------------------------
#
# // Decode the compressed Lerc blob into a raw data array.
# // The data array must have been allocated to size (nDim * nCols * nRows * nBands * sizeof(dataType)).
# // The valid bytes array, if not 0, must have been allocated to size (nCols * nRows).
#
# lerc_status lerc_decode(  const unsigned char* pLercBlob,
#                           unsigned int blobSize,
#                           unsigned char* pValidBytes,
#                           int nDim,
#                           int nCols,
#                           int nRows,
#                           int nBands,
#                           unsigned int dataType,    // data type of outgoing array
#                           void* pData);             // outgoing data array
#
#-------------------------------------------------------------------------------

lercDll.lerc_decode.restype = c_uint
lercDll.lerc_decode.argtypes = (c_char_p, c_uint, c_char_p, c_int, c_int, c_int, c_int, c_uint, c_void_p)

def lercDecode(lercBlob, cpValidBytes, nDim, nCols, nRows, nBands, dataType, dataStr):
    global lercDll
    start = timer()
    cpData = cast(dataStr, c_void_p)
    result = lercDll.lerc_decode(c_char_p(lercBlob), c_uint(len(lercBlob)), cpValidBytes, nDim, nCols, nRows, nBands, dataType, cpData)
    end = timer()
    print('time lerc_decode() = ', (end - start))
    return result

#-------------------------------------------------------------------------------
#
# // Decode the compressed Lerc blob into a double data array (independent of compressed data type). 
# // The data array must have been allocated to size (nDim * nCols * nRows * nBands * sizeof(double)).
# // The valid bytes array, if not 0, must have been allocated to size (nCols * nRows).
# // Wasteful in memory, but convenient if a caller from C# or Python does not want to deal with 
# // data type conversion, templating, or casting.
#
# lerc_status lerc_decodeToDouble(  const unsigned char* pLercBlob,
#                                   unsigned int blobSize,
#                                   unsigned char* pValidBytes,
#                                   int nDim,
#                                   int nCols,
#                                   int nRows,
#                                   int nBands,
#                                   double* pData);    // outgoing data array
#
#-------------------------------------------------------------------------------

lercDll.lerc_decodeToDouble.restype = c_uint
lercDll.lerc_decodeToDouble.argtypes = (c_char_p, c_uint, c_char_p, c_int, c_int, c_int, c_int, POINTER(c_double))

def lercDecodeToDouble(lercBlob, cpValidBytes, nDim, nCols, nRows, nBands, dataStr):
    global lercDll
    start = timer()
    cpData = cast(dataStr, POINTER(c_double))
    result = lercDll.lerc_decodeToDouble(c_char_p(lercBlob), c_uint(len(lercBlob)), cpValidBytes, nDim, nCols, nRows, nBands, cpData)
    end = timer()
    print('time lerc_decodeToDouble() = ', (end - start))
    return result

#-------------------------------------------------------------------------------

def lercDecodeFunction():
    bytesRead = open("D:/GitHub/LercOpenSource/testData/california_400_400_1_float.lerc2", "rb").read()
    #bytesRead = open("D:/GitHub/LercOpenSource/testData/bluemarble_256_256_3_byte.lerc2", "rb").read()
    #bytesRead = open("D:/GitHub/LercOpenSource/testData/landsat_512_512_6_byte.lerc2", "rb").read()
    #bytesRead = open("D:/GitHub/LercOpenSource/testData/world.lerc1", "rb").read()

    infoArr = array.array('L', (0,) * 8)
    dataRangeArr = array.array('d', (0,) * 3)

    result = lercGetBlobInfo(bytesRead, infoArr, dataRangeArr)
    if result > 0:
        print('Error in lercGetBlobInfo(): error code = ', result)
        return result

    info = ['version', 'data type', 'nDim', 'nCols', 'nRows', 'nBands', 'nValidPixels', 'blob size']
    for i in range(len(infoArr)):
        print(info[i], infoArr[i])

    dataRange = ['zMin', 'zMax', 'maxZErrorUsed']
    for i in range(len(dataRangeArr)):
        print(dataRange[i], dataRangeArr[i])

    version = infoArr[0]
    dataType = infoArr[1]
    nDim = infoArr[2]
    nCols = infoArr[3]
    nRows = infoArr[4]
    nBands = infoArr[5]
    nValidPixels = infoArr[6]

    cpValidMask = None
    c00 = b'\x00'
    
    if nValidPixels != nCols * nRows:  # not all pixels are valid, need mask
        cpValidMask = create_string_buffer(nCols * nRows)


    # Here we show 2 options for Lerc decode, lercDecode() and lercDecodeToDouble().
    # We use the first for the integer types, the second for the floating point types.
    # This is for illustration only. You can use each decode function on all data types.
    # lercDecode() is closer to the native data types, uses less memory, but you need
    # to cast the pointers around.
    # lercDecodeToDouble() is more convenient to call, but a waste of memory esp if
    # the compressed data type is only byte or char. 

    if dataType < 6:    # integer types  [char, uchar, short, ushort, int, uint]

        elemSize = [1, 1, 2, 2, 4, 4, 4, 8]
        dataStr = create_string_buffer(nDim * nCols * nRows * nBands * elemSize[dataType])

        result = lercDecode(bytesRead, cpValidMask, nDim, nCols, nRows, nBands, dataType, dataStr)
        if result > 0:
            print('Error in lercDecode(): error code = ', result)
            return result

        # cast to proper pointer type
        
        if dataType == 0:
            cpData = cast(dataStr, c_char_p)
        elif dataType == 1:
            cpData = cast(dataStr, POINTER(c_ubyte))
        elif dataType == 2:
            cpData = cast(dataStr, POINTER(c_short))
        elif dataType == 3:
            cpData = cast(dataStr, POINTER(c_ushort))
        elif dataType == 4:
            cpData = cast(dataStr, POINTER(c_int))
        elif dataType == 5:
            cpData = cast(dataStr, POINTER(c_uint))

        zMin = sys.maxint
        zMax = -zMin


    else:    # floating point types  [float, double]
        
        dataStr = create_string_buffer(nDim * nCols * nRows * nBands * sizeof(c_double))

        result = lercDecodeToDouble(bytesRead, cpValidMask, nDim, nCols, nRows, nBands, dataStr)
        if result > 0:
            print('Error in lercDecodeToDouble(): error code = ', result)
            return result

        cpData = array.array('d')
        cpData.fromstring(dataStr)

        zMin = float("inf")
        zMax = -zMin


    # access the pixels: find the range [zMin, zMax] and compare to the above

    start = timer()
    
    for m in range(nBands):
        i0 = m * nRows * nCols
        for i in range(nRows):
            j0 = i * nCols
            if cpValidMask != None:    # not all pixels are valid, use the mask
                for j in range(nCols):
                    if cpValidMask[j0 + j] != c00:
                        k0 = (i0 + j0 + j) * nDim
                        for k in range(nDim):
                            z = cpData[k0 + k]
                            zMin = min(zMin, z)
                            zMax = max(zMax, z)
            else:                      # all pixels are valid, no mask needed
                for j in range(nCols):
                    k0 = (i0 + j0 + j) * nDim
                    for k in range(nDim):
                        z = cpData[k0 + k]
                        zMin = min(zMin, z)
                        zMax = max(zMax, z)

    end = timer()
    
    print('data range found = ', zMin, zMax)
    print('time pixel loop in python = ', (end - start))
    
    return result

#-------------------------------------------------------------------------------

#>>> import sys
#>>> sys.path.append('D:/GitHub/LercOpenSource/OtherLanguages/Python')
#>>> import LercDecode
#>>> LercDecode.lercDecodeFunction()
