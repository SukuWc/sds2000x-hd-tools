import pyvisa as visa
import pylab as pl
import struct
import math
import gc

SDS_RSC = "TCPIP0::192.168.1.8::inst0::INSTR"
CHANNEL = "C1"
HORI_NUM = 10
tdiv_enum = [100e-12, 200e-12, 500e-12, 1e-9,
    2e-9, 5e-9, 10e-9, 20e-9, 50e-9, 100e-9, 200e-9, 500e-9, \
    1e-6, 2e-6, 5e-6, 10e-6, 20e-6, 50e-6, 100e-6, 200e-6, 500e-6, \
    1e-3, 2e-3, 5e-3, 10e-3, 20e-3, 50e-3, 100e-3, 200e-3, 500e-3, \
    1, 2, 5, 10, 20, 50, 100, 200, 500, 1000]

def get_char_bit(char,n):
    return (char >> n) & 1

def main_desc_analog(recv):
    WAVE_ARRAY_1 = recv[0x3c:0x3f + 1]
    wave_array_count = recv[0x74:0x77 + 1]
    first_point = recv[0x84:0x87 + 1]
    sp = recv[0x88:0x8b + 1]
    v_scale = recv[0x9c:0x9f + 1]
    v_offset = recv[0xa0:0xa3 + 1]
    interval = recv[0xb0:0xb3 + 1]
    code_per_div = recv[0xa4:0Xa7 + 1]
    adc_bit = recv[0xac:0Xad + 1]
    delay = recv[0xb4:0xbb + 1]
    tdiv = recv[0x144:0x145 + 1]
    probe = recv[0x148:0x14b + 1]
    data_bytes = struct.unpack('i', WAVE_ARRAY_1)[0]
    point_num = struct.unpack('i', wave_array_count)[0]
    fp = struct.unpack('i', first_point)[0]
    sp = struct.unpack('i', sp)[0]
    interval = struct.unpack('f', interval)[0]
    delay = struct.unpack('d', delay)[0]
    tdiv_index = struct.unpack('h', tdiv)[0]
    probe = struct.unpack('f', probe)[0]
    vdiv = struct.unpack('f', v_scale)[0] * probe
    offset = struct.unpack('f', v_offset)[0] * probe
    code = struct.unpack('f', code_per_div)[0]
    adc_bit = struct.unpack('h', adc_bit)[0]
    tdiv = tdiv_enum[tdiv_index]
    return vdiv, offset, interval, delay, tdiv, code, adc_bit

def main_read_analog(sds, channel):
    sds.timeout = 30000 # default value is 2000(2s)
    sds.chunk_size = 20 * 1024 * 1024 # default value is 20*1024(20k bytes)
    sds.write(":WAVeform:STARt 0")
    sds.write("WAV:SOUR {}".format(channel))
    sds.write("WAV:PREamble?")
    recv_all = sds.read_raw()
    recv = recv_all[recv_all.find(b'#') + 11:]
    print(len(recv))
    vdiv, ofst, interval, trdl, tdiv, vcode_per, adc_bit = main_desc_analog(recv)
    print(vdiv, ofst, interval, trdl, tdiv,vcode_per,adc_bit)
    points = sds.query(":ACQuire:POINts?").strip()
    points = float(sds.query(":ACQuire:POINts?").strip())
    one_piece_num = float(sds.query(":WAVeform:MAXPoint?").strip())
    if points > one_piece_num:
        sds.write(":WAVeform:POINt {}".format(one_piece_num))
    if adc_bit > 8:
        sds.write(":WAVeform:WIDTh WORD")
    read_times = math.ceil(points / one_piece_num)
    recv_all = []
    for i in range(0, read_times):
        print(f'read: {i}/{read_times}')
        start = i * one_piece_num
        sds.write(":WAVeform:STARt {}".format(start))
        sds.write("WAV:DATA?")
        recv_rtn = sds.read_raw().rstrip()
        block_start = recv_rtn.find(b'#')
        data_digit = int(recv_rtn[block_start + 1:block_start + 2])
        data_start = block_start + 2 + data_digit
        recv = list(recv_rtn[data_start:])
        recv_all += recv
    print('read done')
    convert_data = []
    if adc_bit > 8:
        for i in range(0, int(len(recv_all) / 2)):
            data = recv_all[2 * i + 1] * 256 + recv_all[2 * i]
            convert_data.append(data)
            if i%100 == 0:
                print(f'convert: {i}/{len(recv_all)/2}')
    else:
        convert_data = recv_all
    print('convert done')    
    volt_value = []
    for data in convert_data:
        if data > pow(2, adc_bit - 1) - 1:
            data = data - pow(2, adc_bit)
        else:
            pass
        volt_value.append(data)
    del recv, recv_all, convert_data
    print('pre collect')
    gc.collect()    
    print('post collect')
    time_value = []
    for idx in range(0, len(volt_value)):
        volt_value[idx] = volt_value[idx] / vcode_per * float(vdiv) - float(ofst)
        time_data = - (float(tdiv) * HORI_NUM / 2) + idx * interval + float(trdl)
        time_value.append(time_data)
    print(len(volt_value))
    pl.figure(figsize=(7, 5))
    pl.plot(time_value, volt_value, markersize=2, label=u"Y-T")
    pl.legend()
    pl.grid()



def main_desc(recv):
    print(f'recv length: {len(recv)}')
    first_point = recv[0x84:0x87+1]
    sp = recv[0x88:0x8b+1]
    interval = recv[0xb0:0xb3+1]
    delay = recv[0xb4:0xbb+1]
    tdiv = recv[0x144:0x145+1]
    tdiv_enum=[200e-12,500e-12,\
            1e-9,2e-9,5e-9,10e-9,20e-9,50e-9,100e-9,200e-9,500e-9,\
            1e-6,2e-6,5e-6,10e-6,20e-6,50e-6,100e-6,200e-6,500e-6,\
            1e-3,2e-3,5e-3,10e-3,20e-3,50e-3,100e-3,200e-3,500e-3,\
            1,2,5,10,20,50,100,200,500,1000]
    fp = struct.unpack('i',first_point)[0]
    sp = struct.unpack('i',sp)[0]
    interval = struct.unpack('f',interval)[0]
    delay = struct.unpack('d',delay)[0]
    tdiv_index = struct.unpack('h',tdiv)[0]
    tdiv = tdiv_enum[tdiv_index]
    return interval,delay,tdiv


def main_read_digital(sds, channel):

    sds.write(f"WAV:SOUR {channel}")
    #sds.write("WAV:SOUR D1")
    sds.write("WAV:PREamble?")
    recv_all = sds.read_raw()
    print(recv_all)
    recv = recv_all[recv_all.find(b'#')+11:]
    interval,trdl,tdiv = main_desc(recv)
    sds.write("WAV:DATA?")
    recv_rtn = sds.read_raw().rstrip()
    print(recv_rtn)
    block_start = recv_rtn.find(b'#')
    print("block start")
    print(block_start)
    data_digit = int(recv_rtn[block_start + 1:block_start + 2])
    data_start = block_start + 2 + data_digit
    recv = list(recv_rtn[data_start:])
    volt_value = []
    data =bytearray(recv)
    for char in data:
        for i in range(0,8):
            volt_value.append(get_char_bit(char,i))
    print(len(volt_value))
    time_value = []
    for idx in range(0,len(volt_value)):
        time_data = -(float(tdiv)*10/2)+idx*interval + float(trdl)
        time_value.append(time_data)
    pl.figure(figsize=(7,5))
    pl.ylim(-1,2)
    pl.plot(time_value,volt_value,markersize=2,label=u"Y-T")
    pl.legend()
    pl.grid()

if __name__=='__main__':
        
    _rm = visa.ResourceManager()
    sds = _rm.open_resource("TCPIP0::192.168.1.8::inst0::INSTR")
    #main_read_digital(sds, "D0")
    #main_read_digital(sds, "D1")
    main_read_analog(sds, CHANNEL)


    pl.show()
        