import os
from datetime import datetime

import pymongo
from django.shortcuts import render, redirect
from django.conf import settings
# Create your views here.
from pymongo import MongoClient
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.contrib import messages
import pymongo
from django.urls import reverse
from bson import ObjectId

connect_string = "mongodb://localhost:27017/"

from django.conf import settings

my_client = pymongo.MongoClient(connect_string)

# Define the database name
dbname = my_client['CarRent']


# Create your views here.
def home(request):
    return render(request, 'home.html')


# gerer Client page :
def gestionClient(request):
    clients_collection = dbname["clients"]
    clients_list = list(clients_collection.find())
    if len(clients_list) == 0:
        return render(request, 'gestionClient.html', {'clients_list': clients_list, 'no_clients': True})
    else:
        return render(request, 'gestionClient.html', {'clients_list': clients_list})



# delete client
def delete_client(request, id):
    clients_collection = dbname["clients"]
    clients_collection.delete_one({"id": id})
    return redirect('gestionClient')  # Redirect to the 'gestionClient' URL pattern


# add client
def add_client(request):
    if request.method == 'POST':
        # Retrieve form data
        nom = request.POST.get('nom')
        prenom = request.POST.get('prenom')
        email = request.POST.get('email')
        tele = request.POST.get('tele')
        cin = request.POST.get('cin')
        image = request.FILES.get('image')

        # Save the image file
        if image:
            # Assuming you have a specific directory to save the images
            image_path = f'./static/assets/upload/{image.name}'
            with open(image_path, 'wb') as f:
                for chunk in image.chunks():
                    f.write(chunk)

        # Retrieve the maximum client ID
        clients_collection = dbname["clients"]
        clients_list = list(clients_collection.find())
        if len(clients_list) == 0:
            new_id = 1
        else:
            max_id = clients_collection.aggregate([
                {"$group": {"_id": None, "max_id": {"$max": "$id"}}}
            ]).next().get("max_id")
            new_id = max_id + 1 if max_id else 1

        # Save the client data to MongoDB
        client_data = {
            'id': new_id,
            'name': nom,
            'prenom': prenom,
            'email': email,
            'telephone': tele,
            'cin': cin,
            'image_path': image_path if image else None
        }
        clients_collection.insert_one(client_data)

        return redirect('gestionClient')  # Redirect to the gestionClient page


# show client infos
def show_client(request, id):
    clients_collection = dbname["clients"]
    client = clients_collection.find_one({"id": id})

    if client:
        return render(request, 'show_client.html', {'client': client})
    else:
        return HttpResponse("Client not found")


# Update client
def update_client(request, id):
    if request.method == 'POST':
        # Retrieve form data
        nom = request.POST.get('nom')
        prenom = request.POST.get('prenom')
        email = request.POST.get('email')
        tele = request.POST.get('tele')
        cin = request.POST.get('cin')
        image = request.FILES.get('image')

        # Retrieve the client data from MongoDB
        clients_collection = dbname["clients"]
        client = clients_collection.find_one({'id': id})

        # Save the image file
        if image:
            # Assuming you have a specific directory to save the images
            image_path = f'./static/assets/upload/{image.name}'
            with open(image_path, 'wb') as f:
                for chunk in image.chunks():
                    f.write(chunk)
        else:
            # Keep the existing image path
            image_path = client.get('image_path')

        # Update the client data in MongoDB
        client_data = {
            'name': nom,
            'prenom': prenom,
            'email': email,
            'telephone': tele,
            'cin': cin,
            'image_path': image_path
        }
        clients_collection.update_one({'id': id}, {'$set': client_data})

        return redirect('gestionClient')  # Redirect to the gestionClient page or any other desired page
    else:
        # Retrieve the client data from MongoDB
        clients_collection = dbname["clients"]
        client = clients_collection.find_one({'id': id})
        if client:
            return render(request, 'update_client.html', {'client': client})
        else:
            return HttpResponse('Client not found')  # Handle the case when the client is not found


def testpage(request):
    return render(request, "test.html", {})


def loginp(request):
    return render(request, "loginform.html", {})


def success(request, manager_id):
    collection_name = dbname["managers"]
    manager = collection_name.find_one({"id": manager_id})
    return render(request, 'cars.html', {'manager': manager})


# admin page
def dashboardAdmin(request):
    col1 = dbname['Car']
    col2 = dbname['reservations']
    col3 = dbname['clients']
    col4 = dbname['managers']
    count_cars=col1.count_documents({})
    count_reserv = col2.count_documents({})
    count_client = col3.count_documents({})
    count_managers = col4.count_documents({})

    context = {
        "count_cars" : count_cars,
        "count_reserv" : count_reserv,
        "count_managers" : count_managers,
        "count_client" : count_client,
    }
    return render(request, 'adminDashboard.html',context)


# gerer Managers page :
def gestionManagers(request):
    managers_collection = dbname["managers"]
    managers_list = list(managers_collection.find({"role": "0"}))
    if len(managers_list) == 0:
        return render(request, 'gererManagers.html', {'managers_list': managers_list, 'no_managers': True})
    else:
        return render(request, 'gererManagers.html', {'managers_list': managers_list})


# delete manager
def delete_manager(request, id):
    managers_collection = dbname["managers"]
    managers_collection.delete_one({"id": id})
    return redirect('gestionManagers')  # Redirect to the 'gestionClient' URL pattern


# add manager :
def add_manager(request):
    if request.method == 'POST':
        # Retrieve form data
        nom = request.POST.get('nom')
        prenom = request.POST.get('prenom')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        image = request.FILES.get('image')

        # Check if password and confirm password match
        if password != confirm_password:
            messages.error(request, "Password and confirm password do not match")
            return redirect('gestionManagers')  # Redirect to the gestionManagers page or any other desired page

        # Check if the email is already registered
        managers_collection = dbname["managers"]
        existing_manager = managers_collection.find_one({'email': email})
        if existing_manager:
            messages.error(request, "Email already exists")
            return redirect('gestionManagers')  # Redirect to the gestionManagers page or any other desired page

        # Save the image file
        if image:
            # Assuming you have a specific directory to save the images
            image_path = f'./static/assets/upload/{image.name}'
            with open(image_path, 'wb') as f:
                for chunk in image.chunks():
                    f.write(chunk)

        # Retrieve the maximum manager ID
        managers_list = list(managers_collection.find({"role": "0"}))
        if len(managers_list) == 0:
            new_id = 1
        else:
            max_id = managers_collection.aggregate([
                {"$group": {"_id": None, "max_id": {"$max": "$id"}}}
            ]).next().get("max_id")
            new_id = max_id + 1 if max_id else 1

        # Save the manager data to MongoDB
        manager_data = {
            'id': new_id,
            'name': nom,
            'prenom': prenom,
            'email': email,
            'password':password,
            'role': "0",
            'image_path': image_path if image else None
        }
        managers_collection.insert_one(manager_data)

        return redirect('gestionManagers')  # Redirect to the gestionManagers page


# show manger infos
def show_manager(request, id):
    managers_collection = dbname["managers"]
    manager = managers_collection.find_one({"id": id})

    if manager:
        return render(request, 'show_manager.html', {'manager': manager})
    else:
        return HttpResponse("manager not found")


# update the manager infos
def update_manager(request, manager_id):
    if request.method == 'POST':
        # Retrieve form data
        nom = request.POST.get('nom')
        prenom = request.POST.get('prenom')
        email = request.POST.get('email')
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        image = request.FILES.get('image')
        managers_collection = dbname["managers"]
        manager = managers_collection.find_one({'id': manager_id})
        # Check if the old password is correct
        if old_password:
            if manager['password'] != old_password:
                messages.error(request, 'Invalid old password')
                return redirect('gestionManagers')  # Redirect to the gestionManagers page or any other desired page

            # Check if new password and confirm password match
            if new_password != confirm_password:
                messages.error(request, 'New password and confirm password do not match')
                return redirect('gestionManagers')  # Redirect to the gestionManagers page or any other desired page

        # Save the image file
        if image:
            # Assuming you have a specific directory to save the images
            image_path = f'./static/assets/upload/{image.name}'
            with open(image_path, 'wb') as f:
                for chunk in image.chunks():
                    f.write(chunk)
        else:
            # Keep the existing image path
            image_path = manager.get('image_path')

        # Update the manager data in MongoDB
        if new_password:
            manager_data = {
                'name': nom,
                'prenom': prenom,
                'email': email,
                'password': new_password,
                'image_path': image_path
            }
        else:
            manager_data = {
                'name': nom,
                'prenom': prenom,
                'email': email,
                'image_path': image_path
            }
        managers_collection.update_one({'id': manager_id}, {"$set": manager_data})

        return redirect('gestionManagers')  # Redirect to the gestionManagers page or any other desired page


def checklogin(request):
    collection_name = dbname["managers"]
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        count = collection_name.count_documents({"email": email, "password": password})
        if count == 1:
            manager = collection_name.find_one({"email": email, "password": password})
            request.session['email'] = email
            if manager['role'] == "1":
                return redirect('dashboardAdmin')  # Pass manager ID to the admin dashboard
            else:
                return redirect('cars')  # Pass manager ID to the regular user dashboard
        else:
            messages.error(request, 'Invalid email or password')
            return redirect('fail')
    return redirect('home')


# views.py

def carsp(request):
    collection_name = dbname["Car"]   
    # Retrieve all cars by default
    query = {}
    # Check if search parameters are provided in the request
    car_model = request.GET.get('car-model', '')
    car_maker = request.GET.get('car-maker', '')
    price = request.GET.get('monthly-pay', '')
    year = request.GET.get('year', '')

    # Build the query based on the search parameters
    if car_model:
        query['model'] = {'$regex': car_model, '$options': 'i'}
    if car_maker:
        query['maker'] = {'$regex': car_maker, '$options': 'i'}

    if price:
        query['price_per_day'] = price

    if year:
        query['year'] = year
    
    # Perform the search or retrieve all cars
    cars_col = collection_name.find(query) if query else collection_name.find({})
    cars_data = list(cars_col)
    context = {
        "cars": cars_data
    }
    from datetime import date, datetime
    res_col = dbname["reservations"]
    reservations = list(res_col.find({}))
    from datetime import date
    # Step 1: Retrieve the current date
    current_date = date.today()

    # Step 2: Iterate through the reservations
    for reservation in reservations:
        if reservation:
            # Step 3: Check if the reservation end date is smaller than the current date
            end_date_str = reservation['end_date']
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()  # Convert string to date
            if end_date < current_date:
                # Step 4: Update the car's status to "Available"
                carid = reservation['car']['idcar']
                update_data = collection_name.update_one({'idcar': carid}, {'$set': {'status': 'Available'}})
                car = collection_name.find_one({"idcar": carid})
                print(car)
            else:
                # Step 4: Update the car's status to "Unavailable"
                carid = reservation['car']['idcar']
                update_data = collection_name.update_one({'idcar': carid}, {'$set': {'status': 'Unavailable'}})

    ###########################
    return render(request, "cars.html", context)


def addcar(request):
    return render(request, "addcar.html", {})


def caradded(request):
    collection_name = dbname["Car"]
    count = collection_name.count_documents({})
    if request.method == "POST":
        model = request.POST.get("model")
        maker = request.POST.get("maker")
        year = request.POST.get("year")
        status = "Available"
        price_per_day = request.POST.get("price_per_day")
        images = request.FILES.getlist("images")  # Get the list of uploaded images
        image_paths = []  # Create an empty list to store the image paths

        for image in list(images):
            if image:
                # Assuming you have a specific directory to save the images
                image_path = f'./static/assets/upload/{image.name}'
                with open(image_path, 'wb') as f:
                    for chunk in image.chunks():
                        f.write(chunk)
                image_paths.append(image_path)  # Add the image path to the list
        car_list=list(collection_name.find({}))
        print(len(car_list))
        if len(car_list) == 0:
            new_id = 1
        else:
            max_id = collection_name.aggregate([
                {"$group": {"_id": None, "max_id": {"$max": "$idcar"}}}
            ]).next().get("max_id")
            new_id = max_id + 1 if max_id else 1
        NewCar = {
            "idcar": new_id,
            "model": model,
            "maker": maker,
            "year": year,
            "status": status,
            "price_per_day": price_per_day,
            'image_paths': image_paths  # Assign the image paths list to the 'image_paths' key
        }

        collection_name.insert_one(NewCar)

    return redirect("/cars")



def deletecar(request, id):
    collection_name = dbname["Car"]
    delete_data = collection_name.delete_one({'idcar': id})
    return redirect("cars")


from django.conf import settings

from django.shortcuts import render, redirect


def cardetails(request, id):
    collection_name = dbname["Car"]
    car_details = collection_name.find_one({"idcar": id})

    if not car_details:
        return redirect("/carnotfound")

    context = {
        "car": car_details
    }
    return render(request, "cardetails.html", context)

def carnotfound(request):
    return render(request,"404car.html",{})


#reservation : 
def addres(request,carid):
    # CLient list:
    collection_name1 = dbname["clients"]
    clients_col = collection_name1.find({})
    clients_data = list(clients_col)
    cars_col = dbname["Car"]
    car = cars_col.find_one({"idcar": carid})
    print(car)
    context = {
        "clients": clients_data,
        "car": car,
    }
    return render(request, "addres.html", context)


from datetime import datetime

def res_conf(request):
    client_id = request.POST.get('client')
    car_id = request.POST.get('car')
    start_date = request.POST.get('start-date')
    end_date = request.POST.get('end-date')

    # Parse start_date and end_date strings to datetime objects
    start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
    end_datetime = datetime.strptime(end_date, "%Y-%m-%d")

    # Calculate the number of days between start_date and end_date
    num_days = (end_datetime - start_datetime).days

    reservations_collection = dbname["reservations"]
    cars_collection = dbname["Car"]
    clients_collection = dbname["clients"]

    car = cars_collection.find_one({"idcar": int(car_id)})
    price = num_days * int(car['price_per_day'])
    client = clients_collection.find_one({"id": int(client_id)})

    if car is None or client is None:
        return HttpResponse("Car or client not found.")

    res_list = list(reservations_collection.find({}))

    if len(res_list) == 0:
        new_id = 1
    else:
        max_id = reservations_collection.aggregate([
            {"$group": {"_id": None, "max_id": {"$max": "$id"}}}
        ]).next().get("max_id")
        new_id = max_id + 1 if max_id else 1

    NewRes = {
        "id": new_id,
        "car": car,
        "client": client,
        "start_date": start_date,
        "end_date": end_date,
        "price": price,  # Add the calculated number of days to the object
    }

    reservations_collection.insert_one(NewRes)
    return redirect("/cars")



def reserv(request):
    collection_name = dbname["reservations"]
    res_col = collection_name.find({})
    res_data = list(res_col)
    cars_collection = dbname["Car"]
    context = {
        "reservations": res_data
    }
    return render(request, "reserv.html", context)

def carupdate(request):
    collection_name = dbname["Car"]
    if request.method == "POST":
        idcar = int(request.POST.get("idcar"))
        model = request.POST.get("model")
        maker = request.POST.get("maker")
        year = request.POST.get("year")
        status = request.POST.get("status")
        price_per_day = request.POST.get("price_per_day")
        images = request.FILES.getlist("images")  # Get the list of uploaded images
        image_paths = []  # Create an empty list to store the image paths

        for image in list(images):
            if image:
                # Assuming you have a specific directory to save the images
                image_path = f'./static/assets/upload/{image.name}'
                with open(image_path, 'wb') as f:
                    for chunk in image.chunks():
                        f.write(chunk)
                image_paths.append(image_path)  # Add the image path to the list

        updated_car = {
            "idcar": idcar,
            "model": model,
            "maker": maker,
            "year": year,
            "status": status,
            "price_per_day": price_per_day,
            "image_paths": image_paths  # Assign the updated image paths list
        }

        collection_name.update_one({"idcar": idcar}, {"$set": updated_car})

    return redirect("/cars")


def accepter_res(request,idres):
    res_col = dbname['reservations']
    res = res_col.find_one({"id":idres})
    print(res['car']['idcar'])
    car_id = res['car']['idcar']
    car_col = dbname['Car']
    update_data = car_col.update_one({'idcar': car_id}, {'$set': {'status': 'Not Available'}})
    update_data2 = res_col.update_one({"id":idres}, {'$set': {'status': 'Accepted'}})
    return redirect("/gestionReservation")

def refuser_res(request,idres):
    res_col = dbname['reservations']
    res = res_col.find_one({"id": idres})
    print(res['car']['idcar'])
    delete_data = res_col.delete_one({'id': idres})

    return redirect("/gestionReservation")


# gerer reservation
def gestionReservation(request):
    reservations_collection=dbname["reservations"]
    reservations_list = list(reservations_collection.find())
    if len(reservations_list) == 0:
        return render(request, 'gestionReservation.html', {'reservations_list': reservations_list, 'no_reservation': True})
    else:
        return render(request, 'gestionReservation.html', {'reservations_list': reservations_list})