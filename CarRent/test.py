import pymongo

connect_string = "mongodb://localhost:27017/"

from django.conf import settings

my_client = pymongo.MongoClient(connect_string)

# Define the database name
dbname = my_client['CarRent']

# Get/create collection name
collection_name = dbname["managers"]

# Create two documents
manager1 = {
    "_id": "1",
    "name": "Mahir",
    "prenom": "Rochdi",
    "email": "rochdimahir1945@gmail.com",
    "password" : "mahir1234",
    "role": "0"
}
manager2 = {
    "_id": "2",
    "name": "Aitha",
    "prenom": "Asmae",
    "email": "asmae@gmail.com",
    "password" : "asmae1234",
    "role": "0"
}

# Insert the documents
collection_name.insert_many([manager1, manager2])

# Check the count
count = collection_name.count_documents({})
print(count)

# Read the documents
med_details = collection_name.find({})

# Print on the terminal
for r in med_details:
    print(r["name"])

# Update one document
# update_data = collection_name.update_one({'medicine_id': 'RR000123456'}, {'$set': {'common_name': 'Paracetamol 500'}})

# # Delete one document
# delete_data = collection_name.delete_one({'medicine_id': 'RR000123456'})
