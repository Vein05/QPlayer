import os, json
import sqlite3
from utils.tag import Tag

class Api:
    def __init__(self):
        user = os.environ.get('USER')
        self.PATH = f"/home/{user}/Music"
        data_folder = "./data"
        file_path = os.path.join(data_folder, "info.json")

        if not os.path.exists(data_folder):
            os.makedirs(data_folder)

        with open(file_path, "w") as w:
            json.dump({"DEFAULT_PATH": self.PATH}, w, indent=4)
            
        self.get_songs(self.PATH)

    def get_songs(self, path):
        self.MINIMAL_DURATION = 10
        self.music_extensions = [".mp3", ".ogg", ".wav", ".flac", ".m4a", ".m3u", ".mpa", ".aiff", ".wma"]
        entries = os.scandir(self.PATH)
        songs = []
        for root, dirs, files in os.walk(path):
            for val in files:
                extension = os.path.splitext(val)[1]
                if extension in self.music_extensions:
                    songs.append(os.path.join(root, val))
        self.insert_songs(songs)

    def insert_songs(self, songs):
        self.conn = sqlite3.connect("./data/music.db")
        self.c = self.conn.cursor()
        self.c.execute('''
            CREATE TABLE IF NOT EXISTS music_files (
            path TEXT PRIMARY KEY,
            name TEXT,
            artist TEXT,
            album TEXT,
            album_artist TEXT,
            composer TEXT,
            genre TEXT,
            duration INTEGER,
            size INTEGER,
            year INTEGER,
            bitrate INTEGER
        );'''
                       )
        query = 'INSERT INTO music_files VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
        song_data_list = []
        for path in songs:
            tag = Tag(path)
            if not tag.duration:
                pass
            try:
                if tag.duration < self.MINIMAL_DURATION:
                    pass
            except TypeError:
                pass
            # add path too
            name = tag.name()
            artist = tag.artist
            album = tag.album
            album_artist = tag.album_artist
            composer = tag.composer
            genre = tag.genre
            duration = tag.duration
            size = tag.size
            year = tag.year
            bitrate = tag.bitrate
            song_data_list.append((path, name, artist, album, album_artist, composer, genre, duration, size, year, bitrate))

        try:
            self.c.executemany(query, song_data_list)
            self.conn.commit()
        except sqlite3.IntegrityError:
            pass
        self.conn.close()

    def user_songs(self):
        self.conn = sqlite3.connect("./data/music.db")
        self.c = self.conn.cursor()
        self.c.execute(
            'SELECT path, name, artist, album, album_artist, composer, genre, duration, size, year, bitrate FROM music_files')
        rows = self.c.fetchall()

        songs = []
        
        for row in rows:
            tag = Tag(row[0])
            song = {
                'path': row[0],
                'name': row[1],
                'artist': row[2],
                'album': row[3],
                'album_artist': row[4],
                'composer': row[5],
                'genre': row[6],
                'duration': row[7],
                'size': row[8],
                'year': row[9],
                'bitrate': row[10],
                'cover_image': tag.cover_image(),

            }
            songs.append(song)
        self.conn.close()
        return songs
