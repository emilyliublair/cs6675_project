# creating virtual envionment
cd backend

if [ ! -d "env" ]; then
    echo "Creating virtual environment..."
    python3 -m venv env

else
    echo "Virtual environment already exists."
fi

# only for mac
source ./env/bin/activate
pip install -r requirements.txt
python app.py