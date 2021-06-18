import requests, copy, sys, csv, os
from modelos import Get_payload_to_create, Get_payload_to_modify, Asset_id, Asset_description

def guardar_registro(asset_id, asset, data):
    ASSET_TABLE = 'operaciones.csv'
    OPERATION_SCHEMA = ['asset_tag', 'serial', 'status_id', 'model_id', 'operation_status', 'operation', 'message']
    tmp_table_name = '{}.tmp'.format(ASSET_TABLE)
    registro = {
        'asset_tag' : asset_id['asset_tag'],
        'serial' : asset_id['serial'],
        'status_id' : asset['status_id'],
        'model_id' : asset['model_id'],
        'operation_status' : data['status'],
        'operation' : 'creation',
        'message' : '',
        }
    registros = []

    if data['status'] == 'error':
        registro['message'] = data['messages']['serial'][0]
    else:
        registro['message'] = data['messages']

    registros = cargar_registros()
    registros.append(registro)

    with open(tmp_table_name, mode = 'w') as f:
        writer = csv.DictWriter(f, fieldnames = OPERATION_SCHEMA)
        writer.writerows(registros)
        f.close()
        os.remove(ASSET_TABLE)
        os.rename(tmp_table_name, ASSET_TABLE)


def cargar_registros():
    registros = []
    OPERATION_SCHEMA = ['asset_tag', 'serial', 'status_id', 'model_id', 'operation_status', 'operation', 'message']
    ASSET_TABLE = 'operaciones.csv'

    with open(ASSET_TABLE, mode = 'r') as f:
        reader = csv.DictReader(f, fieldnames = OPERATION_SCHEMA)
        for row in reader:
            registros.append(row)

    return registros


def createasset(asset, serials):
    items = []; dups = 0; serialsdups = []; url = "https://mercadoenvio.snipe-it.io/api/v1/hardware"
    headers = {
        "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImp0aSI6IjQ1ZDZmODVmN2U5Y2U4YmVkZTIzNTU4MTQ5ZWI4ZmUwODg3NTczZWEzMmZiZjFiMWUxMWRhMzdiNjE5NDdkNzM5YzIwMTBiZDlkMWU2NTM3In0.eyJhdWQiOiIxIiwianRpIjoiNDVkNmY4NWY3ZTljZThiZWRlMjM1NTgxNDllYjhmZTA4ODc1NzNlYTMyZmJmMWIxZTExZGEzN2I2MTk0N2Q3MzljMjAxMGJkOWQxZTY1MzciLCJpYXQiOjE1ODkyNzMyODAsIm5iZiI6MTU4OTI3MzI4MCwiZXhwIjoxNjIwODA5MjgwLCJzdWIiOiIyIiwic2NvcGVzIjpbXX0.KqL6QfN6olnzFVE3QnCerkQWX6KFzdMxiJS2VmWcoPjovdVPorfluQ5gkWvDSCUL4VINk8O7eXdwv4w4ORa91AfI4Yx61NvPpvUfiDYKOUo9o4GhOmHv59qus1cFZ_nR9HYz0xZ6GTltYEQs0DgFGFfz63kTy8-CspIUWH-sZtPr8s8vleq1TvAm-OxlStSOCUWb1LK4aubLkZbPeO_1xkcU10KdT1gz3gr8lx8ANScG2DQ3N8TjtT2-LK210ePtvEGsNoq-vC2yRYEJmeFlxQ_Ou4O1azfZcuk_2oc0rwMbCf62cpTT3d8yOBb6AEubyTxpdyDpKmqhww5AOhEqkoXZo7aIijnvVr403BlDLlfxPPHZ7zUgliUbEXCjUtRSBcVSby5YaTbWhnSLJDuimafR2FUW8L9ySzfUXjjE9OKGrUIxFx0-mDUvPu__Vi_oLOErVTZ7gn0KQT4gqCzbMtUz7QUpq7mh0tWSboX4-81xn1Cyvk1xkS65oKtpULpv56jw8DIXHokCUIQEP5W-2v6q-vWABMl_04GfC4UEJfcWeLZHV2n7pGXBS-hKulG-jL-vLZ9Mk0-V5PWJ8fNwlDnaiC14M6Ok7oUPbkgYC8G0w5CSVVvfrDevXW8SbvOcEyLoFDsIbUQfmmGqgfqrz4OrsYT3u5QJ-EOc9t-WO-o",
        "Content-Type": "application/json"
    }

    for serial in serials:
        #Creamos asset por asset, solo cambian sus SN
        asset_id_aux = Asset_id(serial['serial'], serial['serial'], 'Null', serial['MAC']).to_dict()
        payload = Get_payload_to_create(asset_id_aux['asset_tag'], asset['status_id'], asset['model_id'] , asset['name'], asset_id_aux['asset_tag'])
        response = requests.request("POST", url, json=payload.to_dict(), headers=headers)
        data = response.json()
        asset_id = Asset_id(serial['serial'], serial['serial'], get_asset_id(serial['serial']), serial['MAC']).to_dict()
        guardar_registro(asset_id, asset, data)
        items.append(copy.copy(asset_id)) 

        if data['status'] == "error" and data['messages']['serial'][0] == "The serial must be unique.":
            serialsdups.append(serial['serial'])
            dups = 1

    if dups == 1:
        print('\n')
        for serial in serialsdups:
            print ('[{}]'.format(serial))

        option = input('Estos equipos ya existen.\n ¿Desea reemplazarlos?\n[1- SI | 2- NO]\n Selección:')
        while option != '2' and option != '1':
            option = input('\nOpción incorrecta\nSeleccione: [1- SI | 2- NO]\n Selección: ')
        
        if option == '2':
                for serial in serialsdups:
                    for item in items:
                        if item['serial'] == serial:
                            items.remove(item)

    for item in items:
        modify_asset(item, asset)

    print('\n +++¡Carga completa!+++')


def get_serials():
    serials = []; i = 1; item = {}
    print('\nIngrese Serial numbers (0 para terminar): \n')
    item['serial'] = input('S/N ({}) *: '.format(i))
    while item['serial'] == '':
            item['serial'] = input('S/N ({}) *: '.format(i))
    if item['serial'] != '0':
        item['MAC'] = input('MAC ({}) *: '.format(i))
        while item['MAC'] == '':
                item['MAC'] = input('MAC ({}) *: '.format(i))
    else:
        sys.exit()

    serials.append(copy.copy(item)) 

    while item['serial'] != '0' :
        i += 1
        item['serial'] = input('S/N ({}) *: '.format(i))
        while item['serial'] == '':
            item['serial'] = input('S/N ({}) *: '.format(i))
        if item['serial'] != '0':
            item['MAC'] = input('MAC ({}) *: '.format(i))
            while item['MAC'] == '':
                item['MAC'] = input('MAC ({}) *: '.format(i))
        else:
            item['MAC'] = '0'
            serials.append(copy.copy(item)) 
            serials.remove(item)
            break
        serials.append(copy.copy(item)) 
    print('\n')
    for serial in serials:
        print('[Serial: {}\tMAC: {}]'.format(
            serial['serial'],
            serial['MAC']))

    option = input('\nEstos son los equipos a cargar.\n ¿Desea continuar?\n[1- SI | 2- NO]\n Selección:')
    while option != '2' and option != '1':
        option = input('\nOpcion incorrecta\n¿Desea continuar?\n[1- SI | 2- NO]\n Selección:') 
        
    if option == '2':
        sys.exit()

    return serials


def ver_modelos():
    ids = []
    encontrado = 0
    url = "https://mercadoenvio.snipe-it.io/api/v1/models"
    querystring = {"limit":"500","offset":"0","sort":"name","order":"asc"}
    headers = {"Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImp0aSI6IjQ1ZDZmODVmN2U5Y2U4YmVkZTIzNTU4MTQ5ZWI4ZmUwODg3NTczZWEzMmZiZjFiMWUxMWRhMzdiNjE5NDdkNzM5YzIwMTBiZDlkMWU2NTM3In0.eyJhdWQiOiIxIiwianRpIjoiNDVkNmY4NWY3ZTljZThiZWRlMjM1NTgxNDllYjhmZTA4ODc1NzNlYTMyZmJmMWIxZTExZGEzN2I2MTk0N2Q3MzljMjAxMGJkOWQxZTY1MzciLCJpYXQiOjE1ODkyNzMyODAsIm5iZiI6MTU4OTI3MzI4MCwiZXhwIjoxNjIwODA5MjgwLCJzdWIiOiIyIiwic2NvcGVzIjpbXX0.KqL6QfN6olnzFVE3QnCerkQWX6KFzdMxiJS2VmWcoPjovdVPorfluQ5gkWvDSCUL4VINk8O7eXdwv4w4ORa91AfI4Yx61NvPpvUfiDYKOUo9o4GhOmHv59qus1cFZ_nR9HYz0xZ6GTltYEQs0DgFGFfz63kTy8-CspIUWH-sZtPr8s8vleq1TvAm-OxlStSOCUWb1LK4aubLkZbPeO_1xkcU10KdT1gz3gr8lx8ANScG2DQ3N8TjtT2-LK210ePtvEGsNoq-vC2yRYEJmeFlxQ_Ou4O1azfZcuk_2oc0rwMbCf62cpTT3d8yOBb6AEubyTxpdyDpKmqhww5AOhEqkoXZo7aIijnvVr403BlDLlfxPPHZ7zUgliUbEXCjUtRSBcVSby5YaTbWhnSLJDuimafR2FUW8L9ySzfUXjjE9OKGrUIxFx0-mDUvPu__Vi_oLOErVTZ7gn0KQT4gqCzbMtUz7QUpq7mh0tWSboX4-81xn1Cyvk1xkS65oKtpULpv56jw8DIXHokCUIQEP5W-2v6q-vWABMl_04GfC4UEJfcWeLZHV2n7pGXBS-hKulG-jL-vLZ9Mk0-V5PWJ8fNwlDnaiC14M6Ok7oUPbkgYC8G0w5CSVVvfrDevXW8SbvOcEyLoFDsIbUQfmmGqgfqrz4OrsYT3u5QJ-EOc9t-WO-o"}
    response = requests.request("GET", url, headers=headers, params=querystring)
    data = response.json()
    print(data)

    for item in data['rows']:
        ids.append(item['id'])
    while encontrado == 0:
        try:
            option = input(("Model id (""V"" para ver lista de modelos) *: "))
            while encontrado == 0:
                if option.lower() == 'v':
                    for item in data['rows']:
                        print('Id: {idx}\tNombre: {nombre}'.format(
                            idx = item['id'],
                            nombre = item['name']))
                else:
                    for id in ids:
                        if int(option) == int(id):
                            encontrado = 1
                            break
                if encontrado == 0:
                    if option.lower() != 'v':
                        print('No existe el modelo {}'.format(option))
                    option = input(("Model id (""V"" para ver lista de modelos) *: "))
        except ValueError:
            print('Ingrese un numero entero')

    return option


def validar_float(str):
    err = 1
    while err == 1:
        try:
            entero = float(input('{}'.format(str)))
        except ValueError:
            print('Ingresar un número (. para decimales)')
        else:
            err = 0

    return entero


def validar_entero(str):
    err = 1
    while err == 1:
        try:
            entero = int(input('{}'.format(str)))
        except ValueError:
            print('Ingresar un número')
        else:
            err = 0

    return entero


def get_asset_id(serial_number):
        url = "https://mercadoenvio.snipe-it.io/api/v1/hardware/bytag/" + serial_number
        headers = {
            'authorization': "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImp0aSI6IjQ1ZDZmODVmN2U5Y2U4YmVkZTIzNTU4MTQ5ZWI4ZmUwODg3NTczZWEzMmZiZjFiMWUxMWRhMzdiNjE5NDdkNzM5YzIwMTBiZDlkMWU2NTM3In0.eyJhdWQiOiIxIiwianRpIjoiNDVkNmY4NWY3ZTljZThiZWRlMjM1NTgxNDllYjhmZTA4ODc1NzNlYTMyZmJmMWIxZTExZGEzN2I2MTk0N2Q3MzljMjAxMGJkOWQxZTY1MzciLCJpYXQiOjE1ODkyNzMyODAsIm5iZiI6MTU4OTI3MzI4MCwiZXhwIjoxNjIwODA5MjgwLCJzdWIiOiIyIiwic2NvcGVzIjpbXX0.KqL6QfN6olnzFVE3QnCerkQWX6KFzdMxiJS2VmWcoPjovdVPorfluQ5gkWvDSCUL4VINk8O7eXdwv4w4ORa91AfI4Yx61NvPpvUfiDYKOUo9o4GhOmHv59qus1cFZ_nR9HYz0xZ6GTltYEQs0DgFGFfz63kTy8-CspIUWH-sZtPr8s8vleq1TvAm-OxlStSOCUWb1LK4aubLkZbPeO_1xkcU10KdT1gz3gr8lx8ANScG2DQ3N8TjtT2-LK210ePtvEGsNoq-vC2yRYEJmeFlxQ_Ou4O1azfZcuk_2oc0rwMbCf62cpTT3d8yOBb6AEubyTxpdyDpKmqhww5AOhEqkoXZo7aIijnvVr403BlDLlfxPPHZ7zUgliUbEXCjUtRSBcVSby5YaTbWhnSLJDuimafR2FUW8L9ySzfUXjjE9OKGrUIxFx0-mDUvPu__Vi_oLOErVTZ7gn0KQT4gqCzbMtUz7QUpq7mh0tWSboX4-81xn1Cyvk1xkS65oKtpULpv56jw8DIXHokCUIQEP5W-2v6q-vWABMl_04GfC4UEJfcWeLZHV2n7pGXBS-hKulG-jL-vLZ9Mk0-V5PWJ8fNwlDnaiC14M6Ok7oUPbkgYC8G0w5CSVVvfrDevXW8SbvOcEyLoFDsIbUQfmmGqgfqrz4OrsYT3u5QJ-EOc9t-WO-o",
            'accept': "application/json",
            'content-type': "application/json"
            }
        response = requests.request("GET", url, headers=headers)
        data = response.json()
        try:
            if data['status'] == "error":
                print('No se encontró el asset {}'.format(serial_number))
        except KeyError: 
            #Si no existe data['status'] (KeyError) entonces encontró el id
            return (data['id'])


def modify_asset(asset_id, asset):
    url = "https://mercadoenvio.snipe-it.io/api/v1/hardware/" + str(asset_id['id'])
    headers = {
        "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImp0aSI6IjQ1ZDZmODVmN2U5Y2U4YmVkZTIzNTU4MTQ5ZWI4ZmUwODg3NTczZWEzMmZiZjFiMWUxMWRhMzdiNjE5NDdkNzM5YzIwMTBiZDlkMWU2NTM3In0.eyJhdWQiOiIxIiwianRpIjoiNDVkNmY4NWY3ZTljZThiZWRlMjM1NTgxNDllYjhmZTA4ODc1NzNlYTMyZmJmMWIxZTExZGEzN2I2MTk0N2Q3MzljMjAxMGJkOWQxZTY1MzciLCJpYXQiOjE1ODkyNzMyODAsIm5iZiI6MTU4OTI3MzI4MCwiZXhwIjoxNjIwODA5MjgwLCJzdWIiOiIyIiwic2NvcGVzIjpbXX0.KqL6QfN6olnzFVE3QnCerkQWX6KFzdMxiJS2VmWcoPjovdVPorfluQ5gkWvDSCUL4VINk8O7eXdwv4w4ORa91AfI4Yx61NvPpvUfiDYKOUo9o4GhOmHv59qus1cFZ_nR9HYz0xZ6GTltYEQs0DgFGFfz63kTy8-CspIUWH-sZtPr8s8vleq1TvAm-OxlStSOCUWb1LK4aubLkZbPeO_1xkcU10KdT1gz3gr8lx8ANScG2DQ3N8TjtT2-LK210ePtvEGsNoq-vC2yRYEJmeFlxQ_Ou4O1azfZcuk_2oc0rwMbCf62cpTT3d8yOBb6AEubyTxpdyDpKmqhww5AOhEqkoXZo7aIijnvVr403BlDLlfxPPHZ7zUgliUbEXCjUtRSBcVSby5YaTbWhnSLJDuimafR2FUW8L9ySzfUXjjE9OKGrUIxFx0-mDUvPu__Vi_oLOErVTZ7gn0KQT4gqCzbMtUz7QUpq7mh0tWSboX4-81xn1Cyvk1xkS65oKtpULpv56jw8DIXHokCUIQEP5W-2v6q-vWABMl_04GfC4UEJfcWeLZHV2n7pGXBS-hKulG-jL-vLZ9Mk0-V5PWJ8fNwlDnaiC14M6Ok7oUPbkgYC8G0w5CSVVvfrDevXW8SbvOcEyLoFDsIbUQfmmGqgfqrz4OrsYT3u5QJ-EOc9t-WO-o",
        "Content-Type": "application/json"
    }
    payload = Get_payload_to_modify(asset_id['asset_tag'], asset['notes'], asset['status_id'], asset['model_id'], asset['warranty_months'], asset['purchase_cost'], asset['order_number'], asset['name'], asset_id['mac'], 1)
    response = requests.request("PUT", url, json=payload.to_dict(), headers=headers)
    data = response.json()
    print(data)


def ver_estados():
    encontrado = 0
    estados = []
    items = {
        "id" : "",
        "name" : "",
        }
    url = "https://mercadoenvio.snipe-it.io/api/v1/statuslabels"
    querystring = {"limit":"50","offset":"0","sort":"created_at","order":"asc"}
    headers = {"Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImp0aSI6IjQ1ZDZmODVmN2U5Y2U4YmVkZTIzNTU4MTQ5ZWI4ZmUwODg3NTczZWEzMmZiZjFiMWUxMWRhMzdiNjE5NDdkNzM5YzIwMTBiZDlkMWU2NTM3In0.eyJhdWQiOiIxIiwianRpIjoiNDVkNmY4NWY3ZTljZThiZWRlMjM1NTgxNDllYjhmZTA4ODc1NzNlYTMyZmJmMWIxZTExZGEzN2I2MTk0N2Q3MzljMjAxMGJkOWQxZTY1MzciLCJpYXQiOjE1ODkyNzMyODAsIm5iZiI6MTU4OTI3MzI4MCwiZXhwIjoxNjIwODA5MjgwLCJzdWIiOiIyIiwic2NvcGVzIjpbXX0.KqL6QfN6olnzFVE3QnCerkQWX6KFzdMxiJS2VmWcoPjovdVPorfluQ5gkWvDSCUL4VINk8O7eXdwv4w4ORa91AfI4Yx61NvPpvUfiDYKOUo9o4GhOmHv59qus1cFZ_nR9HYz0xZ6GTltYEQs0DgFGFfz63kTy8-CspIUWH-sZtPr8s8vleq1TvAm-OxlStSOCUWb1LK4aubLkZbPeO_1xkcU10KdT1gz3gr8lx8ANScG2DQ3N8TjtT2-LK210ePtvEGsNoq-vC2yRYEJmeFlxQ_Ou4O1azfZcuk_2oc0rwMbCf62cpTT3d8yOBb6AEubyTxpdyDpKmqhww5AOhEqkoXZo7aIijnvVr403BlDLlfxPPHZ7zUgliUbEXCjUtRSBcVSby5YaTbWhnSLJDuimafR2FUW8L9ySzfUXjjE9OKGrUIxFx0-mDUvPu__Vi_oLOErVTZ7gn0KQT4gqCzbMtUz7QUpq7mh0tWSboX4-81xn1Cyvk1xkS65oKtpULpv56jw8DIXHokCUIQEP5W-2v6q-vWABMl_04GfC4UEJfcWeLZHV2n7pGXBS-hKulG-jL-vLZ9Mk0-V5PWJ8fNwlDnaiC14M6Ok7oUPbkgYC8G0w5CSVVvfrDevXW8SbvOcEyLoFDsIbUQfmmGqgfqrz4OrsYT3u5QJ-EOc9t-WO-o"}
    response = requests.request("GET", url, headers=headers, params=querystring)
    data = response.json()

    for item in data['rows']:
        items['id'] = item['id']
        items['name'] = item['name']
        estados.append(copy.copy(items))
         
    while encontrado == 0:
        try:
            option = input(("Status id (""V"" para ver lista de estados) *: "))
            while encontrado == 0:
                if option.lower() == 'v':
                    for item in data['rows']:
                        print('Id: {idx}\tEstado: {nombre}'.format(
                            idx = item['id'],
                            nombre = item['name']))
                else:
                    for estado in estados:
                        if int(option) == int(estado['id']):
                            encontrado = 1
                            break
                if encontrado == 0:
                    if option.lower() != 'v':
                        print('No existe el estado {}'.format(option))
                    option = input(("Status id (""V"" para ver lista de estados) *: "))
        except ValueError:
            print('Ingrese un numero entero')

    return option


def borrar_asset():
    option = input('Borrar dispositivo por: \n[1]Serial number \n[2]Id\n Selección: ')
    while (option != '1' and option != '2'):
        option = input('Borrar dispositivo por: \n[1]Serial number \n[2]Id\n Selección: ')

    if option == '1':
        asset_sn = input('Ingrese Serial number del dispositivo: ')
        asset_id = get_asset_id(asset_sn)
    if option == '2':
        asset_id = input('Ingrese ID del dispositivo: ')

    url = "https://mercadoenvio.snipe-it.io/api/v1/hardware/" + str(asset_id)
    headers = {"Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImp0aSI6IjQ1ZDZmODVmN2U5Y2U4YmVkZTIzNTU4MTQ5ZWI4ZmUwODg3NTczZWEzMmZiZjFiMWUxMWRhMzdiNjE5NDdkNzM5YzIwMTBiZDlkMWU2NTM3In0.eyJhdWQiOiIxIiwianRpIjoiNDVkNmY4NWY3ZTljZThiZWRlMjM1NTgxNDllYjhmZTA4ODc1NzNlYTMyZmJmMWIxZTExZGEzN2I2MTk0N2Q3MzljMjAxMGJkOWQxZTY1MzciLCJpYXQiOjE1ODkyNzMyODAsIm5iZiI6MTU4OTI3MzI4MCwiZXhwIjoxNjIwODA5MjgwLCJzdWIiOiIyIiwic2NvcGVzIjpbXX0.KqL6QfN6olnzFVE3QnCerkQWX6KFzdMxiJS2VmWcoPjovdVPorfluQ5gkWvDSCUL4VINk8O7eXdwv4w4ORa91AfI4Yx61NvPpvUfiDYKOUo9o4GhOmHv59qus1cFZ_nR9HYz0xZ6GTltYEQs0DgFGFfz63kTy8-CspIUWH-sZtPr8s8vleq1TvAm-OxlStSOCUWb1LK4aubLkZbPeO_1xkcU10KdT1gz3gr8lx8ANScG2DQ3N8TjtT2-LK210ePtvEGsNoq-vC2yRYEJmeFlxQ_Ou4O1azfZcuk_2oc0rwMbCf62cpTT3d8yOBb6AEubyTxpdyDpKmqhww5AOhEqkoXZo7aIijnvVr403BlDLlfxPPHZ7zUgliUbEXCjUtRSBcVSby5YaTbWhnSLJDuimafR2FUW8L9ySzfUXjjE9OKGrUIxFx0-mDUvPu__Vi_oLOErVTZ7gn0KQT4gqCzbMtUz7QUpq7mh0tWSboX4-81xn1Cyvk1xkS65oKtpULpv56jw8DIXHokCUIQEP5W-2v6q-vWABMl_04GfC4UEJfcWeLZHV2n7pGXBS-hKulG-jL-vLZ9Mk0-V5PWJ8fNwlDnaiC14M6Ok7oUPbkgYC8G0w5CSVVvfrDevXW8SbvOcEyLoFDsIbUQfmmGqgfqrz4OrsYT3u5QJ-EOc9t-WO-o"}
    response = requests.request("DELETE", url, headers=headers)
    data = response.json()

    if option == '1':
        if data['status'] == "success":
            print("El dispositivo {} se ha eliminado".format(asset_sn.upper()))
        elif data['status'] == "error":
            print('No se ha encontrado el dispositivo {}'.format(asset_sn.upper()))
    if option == '2':
        if data['status'] == "success":
            print("El dispositivo {} se ha eliminado".format(asset_id.upper()))
        elif data['status'] == "error":
            print('No se ha encontrado el dispositivo {}'.format(asset_id.upper()))


def formatoasset():
    asset = Asset_description(str(input("\nNombre del dispositivo: ")), int(ver_estados()), int(ver_modelos()), str(input("Notas: ")), 
                  validar_entero('Meses de garantía: '), validar_float('Costo (U$D): '), validar_entero('Número de orden: ')).to_dict()

    return asset