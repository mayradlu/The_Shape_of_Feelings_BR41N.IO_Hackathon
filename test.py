import socket
import matplotlib.pyplot as plt
import numpy as np
import struct
import time
from scipy.signal import periodogram
from scipy import stats, signal
import random
import math
import pygame



t0 = time.time()

time_window = 2

ref_channel = ["Cz"]
ref_channel_ind = 2

name_channels = ["Fz","C3","C4","Pz","POz","Oz","PO8"]
channels_interested = [0,1,3,4,5,6,7]
name_channels = ["Fz","C3","C4","Oz"]
channels_interested = [0,1,3,6]
sample_freq = 250

bands = ["teta","alfa","beta","gamma"]
bands = ["t","a","b","g"]

bands_values = [[4,7],[8,12],[13,30],[30,50]]

bands = ["b","c"]
bands_values = [[4,7],[8,12]]

max_values = np.zeros([len(bands)])

num_channels_interested = len(channels_interested)
data = np.empty([num_channels_interested],dtype=object)
data_minus = np.empty([2],dtype=object)
fig, axes = plt.subplots(num_channels_interested+2, 1, figsize=(18, 10), sharex=True)  # Adjust the figsize as needed

UDP_IP = "127.0.0.1"
UDP_PORT = 1000 
sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM) 
sock.bind((UDP_IP, UDP_PORT))

pygame.init()
width, height = 1000, 1000
screen = pygame.display.set_mode((width, height))
background_color = (1, 1, 1)

def getColor(alfa,a): 
    if (0< alfa < 30 ):
        G = 2*a
        R = 0
        B = 200
    elif ( 31< alfa < 70):
        G = 200
        R = 2*a
        B = 0
    else:
        R = 230
        G = 0
        B = 2*a  
    #print(R,G,B)
    # Obtener los componentes RGB
    return(R,G,B)

def draw_animation(perc_psd_bands):

    print(perc_psd_bands)

    theta = perc_psd_bands[0]
    alfa = perc_psd_bands[1]
    beta = perc_psd_bands[0]
    gamma = perc_psd_bands[1]
    n_lines = np.linspace(0,360,int(beta))

    screen.fill(background_color)
    pygame.draw.rect(screen, (255, 255, 255), (width//2 - 10, height//2 - 10, 20, 20))

    
    for a in range(len(n_lines)):
        color = getColor(alfa,a)
        x = 50
        xx = random.uniform(150, 350)
        angle = math.radians(n_lines[a])

        x1 = width // 2 + x * math.cos(angle)
        y1 = height // 2 + x * math.sin(angle)
        x2 = width // 2 + xx * math.cos(angle)
        y2 = height // 2 + xx * math.sin(angle)
        pygame.draw.line(screen, color, (x1, y1), (x2, y2), int(gamma/5))


cum = []
count = 0
count2 = 0
first_time = True

while True:

    data_t, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
    data_t = struct.unpack('<17f', data_t)
    
    if count == 0:
        for i in range(num_channels_interested):
            data[i] = [data_t[channels_interested[i]]-data_t[ref_channel_ind]]
        data_minus[0] = [data_t[channels_interested[1]]-data_t[channels_interested[0]]]
        data_minus[1] = [data_t[channels_interested[2]]-data_t[channels_interested[0]]]
        count = 1
    else:
        for i in range(num_channels_interested):
            data[i].append(data_t[channels_interested[i]]-data_t[ref_channel_ind])
        data_minus[0].append(data_t[channels_interested[1]]-data_t[channels_interested[0]])
        data_minus[1].append(data_t[channels_interested[2]]-data_t[channels_interested[0]])

    if len(data[0]) == 250*time_window:

        count2 += 1

        plt.close()
        fig, axes = plt.subplots(num_channels_interested+2, 1, figsize=(18, 10),sharex=True)  # Adjust the figsize as needed

        b, a = signal.butter(8, [2, 52], btype='band', fs=sample_freq)

        for i in range(num_channels_interested):
            data_to_plot = signal.filtfilt(b, a, data[i])
            axes[i].plot(data_to_plot)
            axes[i].set_title(name_channels[i])
            axes[i].grid()

        for i in range(2):
            axes[i+num_channels_interested].plot(data_minus[i]-np.ones([len(data_minus[i])])*np.average(data_minus[i]))
            axes[i+num_channels_interested].set_title("diff: " + str(i))
            axes[i+num_channels_interested].grid()

        plt.show(block=False)
        plt.pause(1)
        all_psd = []
        for i in range(num_channels_interested):
            frequencies, psd = periodogram(([data[i]]), fs=sample_freq)
            psd = psd/np.max(psd)
            all_psd.append(psd)

        frequencies, psd0 = periodogram(([data_minus[0]]), fs=sample_freq)
        psd0 = psd0/np.max(psd0)
        all_psd.append(psd0)
        frequencies, psd1 = periodogram(([data_minus[1]]), fs=sample_freq)
        psd1 = psd1/np.max(psd1)
        all_psd.append(psd1)

        if first_time == True:
            first_time = False
            bands_inds = []
            for i in range(len(bands)):
                min_ind = np.where(frequencies == bands_values[i][0])
                max_ind = np.where(frequencies == bands_values[i][1])
                bands_inds.append([min_ind[0][0], max_ind[0][0]])

        perc_psd_bands = []

        avg_psd = np.average(np.squeeze(np.array(all_psd)),axis=0)

        if count2 == 30:
            print("ffff")
        
        cum.append(avg_psd)

        # print(count2)
        cum_t = np.average(cum, axis=0)
        for i in range(len(bands)):
            avg_psd_t = cum_t[bands_inds[i][0]:bands_inds[i][1]]
            sum_psd = sum(avg_psd_t)
            if sum_psd > max_values[i] and count2 < 30:
                max_values[i] = sum_psd
            perc_psd_bands.append(sum_psd*100/max_values[i])
            # perc_psd_bands.append(sum_psd)
            print(bands[i] + ": " + str(round(perc_psd_bands[i])) + "%, ",end="")
        draw_animation(perc_psd_bands)
        pygame.display.flip()

            
        if len(cum) > 3:
            # print(cum.shape)
            cum.pop(0)
            # print(bands[i] + ": " + str(round(perc_psd_bands[i])) + "%, ",end="")
        print("")

        
        count = 0
        data = np.empty([num_channels_interested],dtype=object)
        data_minus = np.empty([2],dtype=object)

        print("battery at: " + str(round(data_t[-3])) + "%")
        t1 = time.time()
        print("ce fini with ", round(t1-t0,2) , " seconds run time")

        # print(perc_psd_bands)

        # print(frequencies[bands_inds[0][0]])
        # print(frequencies[bands_inds[0][1]])

        # print(frequencies[bands_inds[1][0]])
        # print(frequencies[bands_inds[1][1]])

        # print(frequencies[bands_inds[2][0]])
        # print(frequencies[bands_inds[2][1]])

        # print(bands_inds)
        # print(bands_inds[0])

        # psd_t = np.squeeze(np.array([psd0,psd1]))
        # avg_psd = np.average(psd_t,axis=0)

        # bands_vals = []
        # for i in range(len(bands)):
            
            

        # print(len(data_minus[i]))
        # frequencies, psd = periodogram(np.zeros([len(data_minus[i])]), fs=sample_freq)
        # print(frequencies)
        # frequencies, psd = periodogram(np.zeros([len(data_minus[i])+50]), fs=sample_freq)
        # print(frequencies)
        # for i in range(2):
        #     frequencies, psd = periodogram(data_minus[i], fs=sample_freq)
        #     for i in range(len(bands)):



            # print(frequencies)
        #     axes[i,0].plot(frequencies,psd)
        #     axes[i,0].set_title("psd")
        #     axes[i,0].grid()

        # for i in range(2):
        #     frequencies, psd = periodogram(data[i], fs=sample_freq)
        #     axes[i+num_channels_interested,0].plot(frequencies,psd)
        #     axes[i+num_channels_interested,0].set_title("psd")
        #     axes[i+num_channels_interested,0].grid()



# while True:

#     data_t, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
#     data_t = struct.unpack('<17f', data_t)
    
#     if count == 0:
#         for i in range(8):
#             data[i] = [data_t[i]]
#         count = 1
#     else:
#         for i in range(8):
#             data[i].append(data_t[i])

#     plt.close()
#     fig, axes = plt.subplots(8, 1, figsize=(12, 12))  # Adjust the figsize as needed
    
#     for i in range(8):
#         axes[i].scatter(count,data[i][count])
    
#     count += 1
#     plt.show(block=False)
#     plt.pause(.001)

#     if len(data[0]) == 250*time_window:
#         count = 0
#         data = np.empty([8],dtype=object)

#     print("len data: " + str(len(data[0])),end="")
#     print("count: " + str(count))

#     if len(data[0]) == 250*time_window:

#         plt.clf()
#         for i in range(8):
#             data[i].pop(0)

#         plt.close()
#         fig, axes = plt.subplots(8, 1, figsize=(12, 12))  # Adjust the figsize as needed

#         for i in range(8):
#             axes[i].plot(data[i])
        
#         plt.show(block=False)
#         plt.pause(1)
#         count = 0
#         data = np.empty([8],dtype=object)

#         all_data = []

#         t1 = time.time()
#         print("ce fini with ", round(t1-t0,2) , " seconds run time")

    # if len(all_data) > 1000:
    #     data_plot = np.array(all_data)
    #     # plt.clf()
    #     for i in range(8):
        
    #         axes[i].plot(data_plot[-500:,i])  # Replace this with your data for each subplot
    #         # axes[i].set_title(f'Subplot {i+1}')

    #     print(data_plot.shape)
    #     # plt.plot(data_plot[-500:,-3])
    #     plt.show(block=False)
    #     plt.pause(5)

    # print(float_array[-3])

    # for i in range(len(data_t)):
    #     t.append(float(data_t[i]))
    # data.append(t)

    # if len(data) > 1000:
    #     data = np.array(data)
    #     print(data.shape)
    #     plt.plot(data[33][-1000:])
    #     plt.show(block=False)
    #     plt.pause(10)
    # # print("received message: %s" % data)]