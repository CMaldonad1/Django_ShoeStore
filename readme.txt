In order to run this project the following steps are required to be followed:
1) Ensure you have python 3 and pip installed
2) Install the virtual enviroment using command "pip install virtualenv"
and create the virutal enviroment "virtualenv venv"
3) Activate the virtual enviroment executing ".\venv\Scripts\activate"
4) Install all the dependencies using command "pip install -r requeriments.txt"
5) create the database on your SGDB and update the file "app/settings.py" on the DataBase section or call the database "bitnami_jasperreports"
6) perform the migrations using command "python manage.py makemigrations"
7) Seed the database using the command "python ./botiga/seed/run_seed.py"