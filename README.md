# volteras
Volteras


Maybe locally you will need to do this :

export PYTHONPATH="${PYTHONPATH}:$(pwd)"

docker build -t volteras_image .
docker run --rm -p 8000:8000 --name volteras-container volteras_image

# To add data in the database run the script:

docker exec volteras-container python scripts/import_data.py


# In another terminal :
docker exec volteras-container pytest --color=yes tests/
