from tinytag import TinyTag
import os
from PIL import Image
import io

class Tag:
    default_image = None

    def __init__(self, song):
        self.song = song
        self.info = TinyTag.get(song, image=True)
        self.duration = self.info.duration
        self.size = self.info.filesize
        self.genre = self.info.genre
        self.year = self.info.year
        self.artist = self.info.artist
        self.album = self.info.album
        self.album_artist = self.info.albumartist
        self.bitrate = self.info.bitrate
        self.composer = self.info.composer

        if Tag.default_image is None:
            with open("./icons/default.jpg", 'rb') as file:
                Tag.default_image = self.reduce_image(file.read())

    def name(self):
        if self.info.title is None:
            base_name = os.path.basename(self.song)
            return os.path.splitext(base_name)[0]
        else:
            return self.info.title

    def cover_image(self):
        image = self.info.get_image()
        if image is not None:
            return self.reduce_image(image)
        else:
            return Tag.default_image

    @staticmethod
    def reduce_image(image):
        image_data = io.BytesIO(image)
        image = Image.open(image_data)

        # Calculate the proportional dimensions based on a maximum width or height
        max_dimension = 50
        width, height = image.size
        aspect_ratio = width / height
        if width > height:
            new_width = max_dimension
            new_height = int(new_width / aspect_ratio)
        else:
            new_height = max_dimension
            new_width = int(new_height * aspect_ratio)

        # Resize the image proportionally using LANCZOS algorithm
        resized_image = image.resize((new_width, new_height), resample=Image.LANCZOS)

        # Adjust the output image quality as needed
        output_data = io.BytesIO()
        resized_image.save(output_data, format='png', quality=70)  # Adjust quality as needed
        return output_data.getvalue()


if __name__ == '__main__':
    a = Tag("/home/vein/Music/Playlists/Vein/A_Million_Dreams.mp3").cover_image()
    # print(a)
