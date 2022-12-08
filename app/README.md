# App

This where our backend API files are located. Each Python file runs the Flask API, and builds the endpoints. Each endpoint also renders and HTML
page, which allows the website to display itself. These endpoints also call our static SQL methods, allowing for access and modification of the Database. Our project starts at index.py with / endpoint, which renders index.html and each method redirects to a given endpoint, where different functionality takes place. 