Business Locator
================

This is a simple web application that allows users to search for businesses in a given location. The application uses the Google Places API to search for businesses near a given location and save the results into an Excel-format spreadsheet. The application is provided as both a command line application and as a web application.

Set-up (both versions)
----------------------

Set-up instructions assume you have a version of Python installed on your system.

1. Install the required Python packages:  
    **Unix/Linux/MacOS:**
    ```bash
    $ pip install -r requirements.txt
    ```
    
    **Windows:**
    ```cmd
    > pip install -r requirements.txt
    ```

2. Create a Google Places API key by following the instructions [here](https://developers.google.com/places/web-service/get-api-key).
3. Create a file named `.env` in the root directory of the project and add the following line to the file:
    ```
    GOOGLE_PLACES_API_KEY=<your-api>
    DEFAULT_SEARCH_TERMS=<your-search-terms>
    ```
    Replace `<your-api>` with your Google Places API key and `<your-search-terms>` with the search terms you want to use as the default search terms. You can enter any number of defaults, separate them using commas. Leave this field empty if you don't want to use any default search terms. 

Run the command-line application:
---------------------------------

**Unix/Linux/MacOS:**
```bash
$ python business_locator.py
```

**Windows:**
```cmd
> python business_locator.py
```

Sample output:
```
Please enter a name for this search (used for the output file): my_search
Please enter the location you want to search: Daytona Beach, FL
Do you want to search by radius, drive time, or both? (r/d/b): b
Please enter the radius (in miles) for the search: 50
Enter the maximum drive time (in minutes) for the search: 60
Current search terms: Dive Shop, Scuba Diving, Snorkeling
Would you like to add additional search terms? (y/n): y
Enter a new search term (or press Enter to finish): whale watching
Enter a new search term (or press Enter to finish):

Current output location: /some/path
Would you like to change the output location? (y/n): y
Enter the new output location: /some/other/path

Searching for 'dive shop' near Daytona International Speedway, Daytona Beach, FL...
...

Searching for ' scuba diving' near Daytona International Speedway, Daytona Beach, FL...
...

Searching for 'snorkeling' near Daytona International Speedway, Daytona Beach, FL...
...

Searching for 'whale watching' near Daytona International Speedway, Daytona Beach, FL...
...

Search complete. Results saved to /some/other/path/my_search.xlsx
```

Running the web application
---------------------------

### Using the Flask development server

For development, you can launch the application using the Flask development server. To do this, run the following command:

**Unix/Linux/MacOS:**
```bash
$ cd ./src
$ export FLASK_APP=wsgi.py
$ export FLASK_ENV=development
$ flask run
```

**Windows:**
```cmd
> cd .\src
> set FLASK_APP=wsgi.py
> set FLASK_ENV=development
> flask run
```

This will start the Flask development server. You can access the web application by navigating to `http://localhost:5000` in your web browser.

### Using Gunicorn

For production, it is recommended to use a production-ready WSGI server like Gunicorn. To run the application using Gunicorn, run the following command:

**Unix/Linux/MacOS:**
```bash
$ cd ./src
$ gunicorn -w 4 -b :5000 wsgi:app
```

**Windows:**
```cmd
> cd .\src
> gunicorn -w 4 -b :5000 wsgi:app
```

You can add the `--reload` flag to enable auto-reloading when the source code changes. Use the `--daemon` flag to run Gunicorn in the background.

