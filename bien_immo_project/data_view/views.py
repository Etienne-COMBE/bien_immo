import pandas as pd
from django.shortcuts import render
import psycopg2
from dotenv import load_dotenv
import io
import os

PATH = os.path.dirname(os.getcwd())
SQL_PATH = PATH + "/promoteur_immo_V2.sql"
load_dotenv()
user = os.getenv("POSTGRES_USER")
password = os.getenv("POSTGRES_PASSWORD")
database = os.getenv("POSTGRES_DATABASE")

def connect_db():
    try:
        connection = psycopg2.connect(user=user,
                                    password=password,
                                    host="127.0.0.1",
                                    port="5432",
                                    database=database)
    except:
        print("No connection\n")
    return connection

def import_to_sql(df: pd.Series, connection):
    cursor = connection.cursor()
    cursor.execute(open(SQL_PATH).read())
    output = io.BytesIO()
    df = df[df.balcony == False]
    df.to_csv(output, sep = '\t', header = False, index = False)
    output.seek(0)
    cursor.copy_from(output, 'bien', sep='\t', null='')
    connection.commit()
    cursor.close()
    return connection

def sql_query(connection):
    cursor = connection.cursor()
    query = """
    SELECT ville,
           ROUND(AVG(prix_HT), 2) as prix_moyen,
           ROUND(STDDEV(prix_HT), 2) as ecart_type
    FROM bien
    WHERE etage IS NOT NULL
    GROUP BY ville
    ORDER BY ville;
    """
    cursor.execute(query)
    result = cursor.fetchall()
    cursor.execute("SELECT COUNT(*), ROUND(STDDEV(prix_HT), 2) as ecart_type FROM bien")
    number_std = cursor.fetchone()
    cursor.close()
    return result, number_std, connection

# Create your views here.
def stats(request):
    connection = connect_db()
    message = request.GET.get('message')
    if request.method == 'POST':
        file = request.FILES["csv_file"]
        df_og = pd.read_csv(file, sep = ",").iloc[:, 1:]
        df_og.parking = df_og.parking.map({1.0: 'true', 0.0: 'false'})
        connection = import_to_sql(df_og, connection)
    result, number_std, connection = sql_query(connection)
    connection.close()
    return render(request, "data_view/stats.html", {"columns": ['Ville', "Prix moyen", "Ecart type"], "data": result, "number": number_std[0], "std": number_std[1], "message": message})