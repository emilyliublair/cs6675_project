# How to run

To run this properly, you must serve both the frontend and backend. 

## To run the frontend:
You can run the frontend by installing dependencies using npm. This can be done by running the command "npm install". After dependencies are installed, you can run "npm run dev" to start the server.

## To run the backend:
You can run the backend by creating a virtual environment. You can do this by running the command "python -m venv env". And correspoding to your OS, you should activate this virtual environment. After the environment is activated, you must run "pip install -r requirements.txt" to install all the dependencies. After all of this is done, you can finally serve the backend by running "python app.py" to start the server.

# How does it work?

The project is split up into different structures: frontend, backend, and data. The frontend folder contains all the frontend code that are applicable to our demo. The backend folder contains the backend routes that should be served to the frontend to properly work. The data folder contains the code to scrape piazza for sample question and answers. All of these question and answers are contained within lab0, lab1, lab2, and lab3. 
