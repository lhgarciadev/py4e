import sqlite3
import csv

# Conexión a la base de datos
conn = sqlite3.connect('tracksdb.sqlite')
cur = conn.cursor()

# Crear tablas utilizando executescript para crear todas de una vez
cur.executescript('''
DROP TABLE IF EXISTS Artist;
DROP TABLE IF EXISTS Album;
DROP TABLE IF EXISTS Genre;
DROP TABLE IF EXISTS Track;

CREATE TABLE Artist (
    id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    name    TEXT UNIQUE
);

CREATE TABLE Album (
    id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    artist_id  INTEGER,
    title   TEXT UNIQUE
);

CREATE TABLE Genre (
    id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    name   TEXT UNIQUE
);

CREATE TABLE Track (
    id  INTEGER NOT NULL PRIMARY KEY 
        AUTOINCREMENT UNIQUE,
    title TEXT  UNIQUE,
    album_id  INTEGER,
    genre_id  INTEGER,
    len INTEGER, rating INTEGER, count INTEGER
);
''')

# Leer el archivo CSV
fname = input('Enter file name: ')
if len(fname) < 1:
    fname = 'tracks.csv'

# Abrir y procesar el archivo CSV
with open(fname, newline='', encoding='utf-8') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        # Ejemplo de fila: Another One Bites The Dust,Queen,Greatest Hits,217103,100,55,Rock
        title = row[0]
        artist = row[1]
        album = row[2]
        length = int(row[3]) if row[3] else None
        rating = int(row[4]) if row[4] else None
        count = int(row[5]) if row[5] else None
        genre = row[6]

        if title is None or artist is None or genre is None or album is None:
            continue

        print(title, artist, album, genre, count, rating, length)

        # Insertar o ignorar al artista
        cur.execute('''INSERT OR IGNORE INTO Artist (name) 
            VALUES ( ? )''', (artist,))
        cur.execute('SELECT id FROM Artist WHERE name = ?', (artist,))
        artist_id = cur.fetchone()[0]

        # Insertar o ignorar al álbum
        cur.execute('''INSERT OR IGNORE INTO Album (title, artist_id) 
            VALUES ( ?, ? )''', (album, artist_id))
        cur.execute('SELECT id FROM Album WHERE title = ?', (album,))
        album_id = cur.fetchone()[0]

        # Insertar o ignorar al género
        cur.execute('''INSERT OR IGNORE INTO Genre (name) 
            VALUES ( ? )''', (genre,))
        cur.execute('SELECT id FROM Genre WHERE name = ?', (genre,))
        genre_id = cur.fetchone()[0]

        # Insertar o reemplazar la pista
        cur.execute('''INSERT OR REPLACE INTO Track
            (title, album_id, genre_id, len, rating, count) 
            VALUES ( ?, ?, ?, ?, ?, ? )''', 
            (title, album_id, genre_id, length, rating, count))

    # Guardar los cambios
    conn.commit()

# Consulta para verificar los datos
sqlstr = '''
SELECT Track.title, Artist.name, Album.title, Genre.name 
FROM Track 
JOIN Genre ON Track.genre_id = Genre.id
JOIN Album ON Track.album_id = Album.id
JOIN Artist ON Album.artist_id = Artist.id
ORDER BY Artist.name LIMIT 3
'''

for row in cur.execute(sqlstr):
    print(str(row[0]), row[1], row[2], row[3])

# Cerrar la conexión a la base de datos
cur.close()
