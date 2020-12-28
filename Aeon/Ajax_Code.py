from django.http import JsonResponse
from .views import db, firestore
from time import gmtime, strftime
import time
import datetime as dt
import json


def ajax_login_credentialsCheck(request):
    try:
        mailID = request.GET.get('mailID', None)
        pwd = request.GET.get('pwd', None)

        obj = db.collection('clientRegister').where('mailID', '==', mailID).where('type', '==', 'ACCOUNT').stream()
        for i in obj:
            password_obj = db.collection('clientRegister').document(i.id).get().to_dict()
            password = password_obj['password']
            if password == pwd:
                return JsonResponse({'state': True, 'login': True, 'clientID': password_obj['clientID']}, safe=False)
            else:
                return JsonResponse({'state': True, 'reason': 'Incorrect Password'})

        return JsonResponse({'state': True, 'reason': 'Mail ID not found.'})
    except Exception as e:
        print(e)
        return JsonResponse({'state': False})


def ajax_login_accountCreate(request):
    try:
        mailID = request.GET.get('mailID', None)
        pwd = request.GET.get('pwd', None)
        firstName = request.GET.get('firstName', None)
        lastName = request.GET.get('lastName', None)
        address = request.GET.get('address', None)
        zipCode = request.GET.get('zipCode', None)
        city = request.GET.get('city', None)
        number = request.GET.get('number', None)

        # CHECK MAIL ID

        obj = db.collection('clientRegister').where('mailID', '==', mailID).where('type', '==', 'ACCOUNT').stream()
        for i in obj:
            return JsonResponse({'state': True, 'reason': 'Mail ID Is Taken,Try With Another Mail ID.'})

        # CHECK PHONE NUMBER
        if not str(number).isdigit():
            return JsonResponse({'state': True, 'reason': 'Invalid Format Of Mobile Number.'})

        conData = {
            'address': address,
            'mailID': mailID,
            'firstName': firstName,
            'lastName': lastName,
            'city': city,
            'phoneNumber': '+91' + str(number),
            'createdTime': firestore.firestore.SERVER_TIMESTAMP,
            'password': pwd,
            'zipCode': zipCode,
            'clientID': '',
            'type': 'ACCOUNT'
        }
        db.collection('clientRegister').document().set(conData)
        obj = db.collection('clientRegister').where('mailID', '==', mailID).where('type', '==', 'ACCOUNT').stream()
        client_id = 0
        for i in obj:
            db.collection('clientRegister').document(i.id).update({
                'clientID': i.id
            })
            client_id = i.id
            break

        return JsonResponse({'state': True, 'account': True, 'clientID': client_id}, safe=False)

    except Exception as e:
        print(e)
        return JsonResponse({'state': False})


def ajax_login_guestCreate(request):
    try:
        mailID = request.GET.get('mailID', None)
        address = request.GET.get('address', None)
        zipCode = request.GET.get('zipCode', None)
        firstName = request.GET.get('firstName', None)
        lastName = request.GET.get('lastName', None)
        number = request.GET.get('number', None)
        city = request.GET.get('city', None)
        time_Of_creration = time.time()

        # CHECK PHONE NUMBER
        if not str(number).isdigit():
            return JsonResponse({'state': True, 'reason': 'Invalid Format Of Mobile Number.'})

        conData = {
            'address': address,
            'mailID': mailID,
            'firstName': firstName,
            'lastName': lastName,
            'city': city,
            'phoneNumber': '+91' + str(number),
            'createdTime': firestore.firestore.SERVER_TIMESTAMP,
            'zipCode': zipCode,
            'clientID': '',
            'type': 'GUEST',
            'refTime': time_Of_creration
        }

        db.collection('clientRegister').document().set(conData)
        obj = db.collection('clientRegister').where('mailID', '==', mailID).where('type', '==', 'GUEST').where(
            'refTime', '==', time_Of_creration).stream()
        client_id = 0
        for i in obj:
            db.collection('clientRegister').document(i.id).update({
                'clientID': i.id
            })
            client_id = i.id
            break

        return JsonResponse({'state': True, 'account': True, 'clientID': client_id}, safe=False)

    except Exception as e:
        print(e)
        return JsonResponse({'state': False})
