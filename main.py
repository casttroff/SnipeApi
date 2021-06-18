from createasset import createasset, get_serials, borrar_asset, formatoasset

def main():
    while True:
        option = input('\n ++Gestor de carga++\n\n[1] Carga/modificación\n[2] Eliminar\n Selección: ')
        if option == '1':
            print('\n +Carga/modificación+')
            serials = get_serials()
            asset = formatoasset() 
            createasset(asset, serials)
        elif option == '2':
            print('\n +Eliminar+ \n')
            borrar_asset()
        else:
            print('\nOpción incorrecta')


if __name__ == '__main__':
   while True:
      main()