from json.decoder import JSONDecodeError
from flask import Flask
from flask_restful import Resource, Api, reqparse
import pyshorteners as sh
import os
import json
from pathlib import Path

app = Flask(__name__)
api = Api(app)


class Url(Resource):
    def get(self):
        """Get short url

        Returns:
            string:  The main get api which accepts a long url and provides its shortned url
        """
        parser = reqparse.RequestParser()  # initialize
        parser.add_argument("url", required=True)  # add args
        args = parser.parse_args()  # parse arguments to dictionary

        if args["url"] is not None:
            existing_shortned_url = self.get_url_from_database(args["url"])

            if existing_shortned_url is None:
                # if the url is new, then create its short version
                s = sh.Shortener()
                short_url = s.tinyurl.short(args["url"])
                self.store_url(args["url"], short_url)
                return {"data": short_url}, 200  # return data with 200 OK
            else:
                # if url is not new then return its previously generated short version
                return {"data": existing_shortned_url}, 200  # return data with 200 OK
        else:
            return {"message": f"url is empty"}, 409

    def store_url(self, long_url, short_url):
        """Store the new url and its shortned url into the database file

        Args:
            long_url (string): User given long url
            short_url (string): Program generated short url
        """
        url_mapping_list = self.read_url_database()
        url_mapping_list[long_url] = short_url

        with open(self.get_database_path(), "w") as file_content:
            json.dump(url_mapping_list, file_content, indent=4, sort_keys=False)

    def get_url_from_database(self, long_url):
        """Get the existing stored short_url from database file, if not then return None

        Args:
            long_url (string): User given long url

        Returns:
            (string): Either existing short url or None
        """
        existing_saved_urls = self.read_url_database()
        if (existing_saved_urls is not None) and (long_url in existing_saved_urls):
            return existing_saved_urls[long_url]
        else:
            return None

    def read_url_database(self):
        """Read the existing stored URLs from the database file

        Returns:
            json: Existing stored key value pair of urls
        """
        data_json = {}
        try:
            with open(self.get_database_path(), "r") as j:
                data_json = json.loads(j.read())
        except JSONDecodeError:
            pass

        return data_json

    def get_database_path(self):
        """Get the path of database file in current directory

        Returns:
            string: Local file path of database
        """
        os.chdir(os.path.dirname(__file__))
        path_cwd = os.getcwd()
        file_path = os.path.join(path_cwd, "url_database.txt")
        file = Path(file_path)
        file.touch(exist_ok=True)
        return file_path


api.add_resource(Url, "/geturl")

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, port=5000)  # run our Flask app
