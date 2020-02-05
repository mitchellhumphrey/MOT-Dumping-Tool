import struct
import sys
import os
import PySimpleGUI as sg


def unpack(path, output):
    mot = open(path, "rb")

    if not os.path.exists(output + "\\"):
        os.mkdir(output + "\\")

    header = struct.unpack(">iiii", mot.read(16))

    list = []
    indexDict = {}

    list.append(header[3])
    indexDict[header[3]] = -1

    for j in range(header[1]):
        off = struct.unpack(">i", mot.read(4))[0]
        if off != 0:
            list.append(off)
            indexDict[off] = j

    print("Extracted " + str(len(list)) + " animations")

    list.sort()

    for i in range(len(list) - 1):
        indexName = '0x{0:0{1}X}'.format(indexDict[list[i]], 4)
        mot.seek(list[i])
        with open(output + "\\" + indexName + ".gnta", 'wb') as f:
            f.write(mot.read(list[i + 1] - list[i]))

    mot.close();


def pack(path, input_folder):
    mot = open(path, "wb")

    mot.write(struct.pack('>L', 0))
    mot.write(struct.pack('>L', 0))
    mot.write(struct.pack('>L', 16))
    mot.write(struct.pack('>L', 0))

    max = 0

    list = []
    indexDict = {}

    for filename in os.listdir(input_folder):
        if filename.endswith(".mota") or filename.endswith(".gnta"):
            index = int(os.path.splitext(os.path.basename(filename))[0], 16)
            list.append(index)
            indexDict[index] = os.path.join(input_folder, filename)
            if index > max:
                max = index;

    for i in range(max):
        mot.write(struct.pack('>L', 0))

    list.sort()
    list.reverse()

    off = (max + 5) * 4

    for i in list:
        mot.seek(0x10 + i * 4)
        mot.write(struct.pack('>L', off))
        mot.seek(off)
        with open(indexDict[i], mode='rb') as file:
            fileContent = file.read()
            mot.write(fileContent)
            off += len(fileContent)

    mot.seek(0x4)
    mot.write(struct.pack('>L', max + 1))
    mot.write(struct.pack('>L', 16))
    mot.write(struct.pack('>L', off))

    mot.close()


layout = [[sg.Text('Would you like to')],
          [sg.Radio('Unpack Mot', 'radio1'), sg.Radio('Pack Mot', 'radio1')],
          [sg.Button('Go'), sg.Button('Quit')]]

window = sg.Window('Mot Editor 2000', layout)



while True:
    event, values = window.Read()
    mot_file = sg.popup_get_file('Select the mot you wish to edit', file_types=(("Mot Files", "*.mot"),), )
    print(event)
    if event in (None, 'Quit'):
        quit()
    elif event == 'Go':
        if values[0]:
            output_path = sg.popup_get_folder('select the output folder for unpacking Mot')
            unpack(mot_file, output_path)
        elif values[1]:
            input_path = sg.popup_get_folder('select the input folder for the Mot')
            pack(mot_file, input_path)
