# Monitor de outliers de facturación

## 1- Descargar archivos desde GITHUB

En la página de GITHUB, descargar el .zip. 

![Descarga GITHUB](assets/0-descargar%20github.png)

## 2- Importar los datos de SAS

Correr los dos códigos de SAS ("item expo completisimo" e "item impo completisimo"). Son archivos pesados, por lo que recomiendo tener paciencia. Los csv se van a guardar en esta ruta "/srv/sas/secex/home/mbasualdo", si quieren, cambienlo a una carpeta que ustedes quieran. 

Con el WINSCP transfieran los dos csv a la carpeta "data". Es importante que sea con el WINSCP, no exporten desde la consola del sas. 

## 3- Crear un ambiente en python

Tienen instalado anaconda. En el buscador de windows busquen "Anaconda Prompt (Anaconda 3)", abranlo y escriba el siguiente código (enter para "proceder"):

`conda create -n outliers`

Crearon un ambiente llamado "outliers", pero le faltan los paquetes. Primero se activa el ambiente, luego se instala.

`conda activate outliers` 

`pip install pandas plotly ipykernel nbformat xlsxwriter` 

## 4- Abrir y correr el códgo

Abrir el programa vs code, luego ir a "Archivo", "Abrir carpeta..."

![](assets/1-abrir%20carpeta.png)

Abrir la carpeta descomprimida (no importa que vean todas las carpetas de la foto)

![](assets/2-ubicacion%20carpeta.png)

Abrir el programa "aplicacion.ipynb
![](assets/3-%20aplicion%20ipynb.png)

Seleccionar el "kernel" a utilizar, que debe tener el nombre del ambiente creado ("outliers")

![](assets/4-ubicacion%20kernel.png)

![](assets/5-%20seleccion%20del%20kernel.png)

Y listo! Ya pueden "Ejecutar todo" el código. Tienen una explicación detallada en el mismo, pero cualquier cosa, no duden en acercarse a Luca o a mí (Martín).

