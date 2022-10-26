# Monitor de outliers de facturación

## 1- Importar los datos de SAS

Correr los dos códigos de SAS. Son archivos pesados, por lo que recomiendo tener paciencia. Los csv se van a guardar en esta ruta "/srv/sas/secex/home/mbasualdo", si quieren, cambienlo a una carpeta que ustedes quieran. 

Con el WINSCP transfieran los dos csv a la carpeta "data". Es importante que sea con el WINSCP, no exporten desde la consola del sas. 

## 2- Crear un ambiente en python

Tienen instalado anaconda. En el buscador de windows busquen "Anaconda Prompt (Anaconda 3)", abranlo y escriba el siguiente código (enter para "proceder"):

`conda create -n outliers`

Crearon un ambiente llamado "outliers", pero le faltan los paquetes. Primero se activa el ambiente, luego se instala.

`conda activate outliers` 

`pip install pandas plotly ipykernel nbformat xlsxwriter` 

## 3- Abrir y correr el códgo

Abrir con el vscode el programa "aplicacion.ipynb", que es un jupyter notebook que sintetiza todo el código. Es un resultado amigable y sencillo de usar, con explicaciones resumidas de las posibilidades. 

