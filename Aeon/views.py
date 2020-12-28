from django.shortcuts import render, redirect
from django.http import HttpResponse
from . import Checksum
from .temperatureAPI import *
import datetime as dt
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import never_cache
import random
import time
from .settings import MERCHANT_KEY
# FIREBASE MODELS

from firebase_admin import credentials, firestore, storage
import firebase_admin
import pyrebase

cred = credentials.Certificate(r"FirebaseSDK/aeon-fb9bd-firebase-adminsdk-ywtem-54d8666685.json")
firebase_admin.initialize_app(cred)

Config = {
    'apiKey': "AIzaSyDQa8m9n-rMA9gmVX6bfGKAu6rEyLp7H18",
    'authDomain': "aeon-fb9bd.firebaseapp.com",
    'databaseURL': "https://aeon-fb9bd.firebaseio.com",
    'projectId': "aeon-fb9bd",
    'storageBucket': "aeon-fb9bd.appspot.com",
    'messagingSenderId': "71247634715",
    'appId': "1:71247634715:web:d41e1af98970a62290f3be",
    'measurementId': "G-DZE1VTCK1D"
}

con = pyrebase.initialize_app(Config)
firebase_auth = con.auth()
db = firestore.client()
bucket = storage.bucket('gs://aeon-fb9bd.appspot.com')


def date_extractor(date):
    date = str(date).replace('<span class=', '').replace('</span>', '').replace('day>', '').replace(
        'month>', '').replace('year>', '').replace(' ', '-')
    date_list = date.split('-')
    dic_month = {'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04', 'May': '05', 'Jun': '06', 'Jul': '07', 'Aug': '08',
                 'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'}
    date_list[1] = dic_month[date_list[1]]
    return '-'.join(date_list)


temperature = climaCell_Temperature()


def home_pageshow(request):
    global temperature
    temperature = climaCell_Temperature()
    return render(request, 'home.html', {'temp': temperature})


def aboutUs_pageshow(request):
    return render(request, 'about-us.html', {'temp': temperature})


@csrf_exempt
def booking_pageshow(request):
    if request.method == 'POST':
        fromDate = request.POST['FromDate']
        toDate = request.POST['ToDate']
        guestCount = request.POST['GuestQuantity']
        callFrom = request.POST['postCall']

        fromDate = date_extractor(fromDate)
        toDate = date_extractor(toDate)
        fromDate_obj = fromDate.split('-')
        toDate_obj = toDate.split('-')
        fromDATEOBJ = dt.datetime(int(fromDate_obj[2]), int(fromDate_obj[1]), int(fromDate_obj[0]))
        toDATEOBJ = dt.datetime(int(toDate_obj[2]), int(toDate_obj[1]), int(toDate_obj[0]))
        dayDiff = (toDATEOBJ - fromDATEOBJ).days
        roomAvailable = []
        RoomObj = db.collection('roomRegister').where('roomStatus', '==', True).stream()
        RegisterObj = db.collection('bookingRegister').where('STATUS', '==', 'TXN_SUCCESS').where('checkedOUT', '==',
                                                                                                  False).stream()
        RegisterList = [i.to_dict() for i in RegisterObj]

        roomID_All = []
        for i in RoomObj:
            roomID_All.append(i.id)  # Contains All Room IDs

        for i in roomID_All:
            for j in RegisterList:
                if j['roomID'] == i:
                    # if not (j['fromDate'] <= fromDate <= toDate <= j['toDate']):
                    if not (j['fromDate'] <= fromDate <= j['toDate']):
                        roomAvailable.append(i)

        temp_List = []
        for i in RegisterList:
            temp_List.append(i['roomID'])

        for i in roomID_All:
            if i not in temp_List:
                roomAvailable.append(i)
        roomAvailable = list(set(roomAvailable))
        roomAvailableFinal = []

        for i in roomAvailable:
            priceObj = db.collection('roomRegister').document(i).get().to_dict()['costPerNight']
            roomAvailableFinal.append((i, priceObj))

        data = {
            'roomsAvailable': roomAvailableFinal,
            'fromDate': fromDate,
            'toDate': toDate,
            'guestCount': guestCount,
            'temp': temperature,
            'totalDays': dayDiff
        }
        return render(request, 'bookings.html', data)
    else:
        return render(request, 'bookings.html', {'temp': temperature})


def confirm_pageshow(request):
    return render(request, 'confirm.html', {'temp': temperature})


def contactUs_pageshow(request):
    return render(request, 'contact-us.html', {'temp': temperature})


def facility_pageshow(request):
    return render(request, 'facility.html', {'temp': temperature})


@csrf_exempt
def roomSummary_pageshow(request):
    if request.method == 'POST':
        fromDate = request.POST['form_fromDate']
        toDate = request.POST['form_toDate']
        guestCount = request.POST['form_guestCount']
        roomList = str(request.POST['form_list']).split(',')

        data = {
            'fromDate': fromDate,
            'toDate': toDate,
            'guestCount': guestCount,
            'roomList': roomList,
            'temp': temperature
        }

        return render(request, 'confirm.html', data)
    else:
        return redirect('/bookings')


def homeStay_pageshow(request):
    return render(request, 'HomeStay.html', {'temp': temperature})


def deluxeRoom_pageshow(request):
    return render(request, 'DeluxeRoom.html', {'temp': temperature})


def premiumRoom_pageshow(request):
    return render(request, 'PremiumRoom.html', {'temp': temperature})


def error_404(request, exception):
    print(exception)
    return HttpResponse('404')


@csrf_exempt
def payment_check(request):
    if request.method == 'POST':
        fromDate = request.POST['fromDate']
        toDate = request.POST['toDate']
        guestCount = request.POST['guestCount']
        roomList = request.POST['roomList']
        clientID = request.POST['clientID']
        total = 0
        roomList = str(roomList).lstrip('["').rstrip('"]').split(',')
        roomList_final = []

        fromDate_obj = fromDate.split('-')
        toDate_obj = toDate.split('-')
        fromDATEOBJ = dt.datetime(int(fromDate_obj[2]), int(fromDate_obj[1]), int(fromDate_obj[0]))
        toDATEOBJ = dt.datetime(int(toDate_obj[2]), int(toDate_obj[1]), int(toDate_obj[0]))
        dayDiff = (toDATEOBJ - fromDATEOBJ).days

        for i in roomList:
            roomList_final.append(str(i).strip().lstrip('"').lstrip("'").rstrip("'").rstrip('"'))
        for i in roomList_final:
            obj = db.collection('roomRegister').document(i).get().to_dict()
            costPerNight = int(obj['costPerNight'])
            discount = int(obj['discountPercentage'])
            if discount != 0:
                price = ((dayDiff * costPerNight) * discount / 100)
                total += price
            else:
                total += (dayDiff * costPerNight)
        mailID = db.collection('clientRegister').document(clientID).get().to_dict()['mailID']
        order_id = clientID + '__' + str(time.time())

        totalMoney = ("%.2f" % total)
        param_dict = {
            'MID': 'Aqbtun06070993189675',
            'ORDER_ID': order_id,
            'TXN_AMOUNT': str(totalMoney),
            'CUST_ID': mailID,
            'INDUSTRY_TYPE_ID': 'Retail',
            'WEBSITE': 'WEBSTAGING',
            'CHANNEL_ID': 'WEB',
            'CALLBACK_URL': 'http://127.0.0.1:8000/handlerequest/',
        }
        param_dict['CHECKSUMHASH'] = Checksum.generate_checksum(param_dict, MERCHANT_KEY)

        for i in roomList_final:
            booking_data = {
                'checkedIN': False,
                'checkedOUT': False,
                'forDisplay': True,
                'fromDate': fromDate,
                'toDate': toDate,
                'guestCount': guestCount,
                'orderID': order_id,
                'roomID': i,
                'clientID': clientID
            }
            db.collection('bookingRegister').document().set(booking_data)
        return render(request, 'paytm.html', {'param_dict': param_dict})
    else:
        return render(request, 'bookings.html', {'temp': temperature})


@csrf_exempt
def handlerequest(request):
    if request.method == 'POST':
        checksum = ''
        form = request.POST
        response_dict = {}
        for i in form.keys():
            response_dict[i] = form[i]
            if i == 'CHECKSUMHASH':
                checksum = form[i]

        verify = Checksum.verify_checksum(response_dict, MERCHANT_KEY, checksum)
        if verify:
            if response_dict['RESPCODE'] == '01':
                obj = db.collection('bookingRegister').where('orderID', '==', response_dict['ORDERID']).stream()
                for i in obj:
                    data_Update = {
                        'GATEWAYNAME': response_dict['GATEWAYNAME'],
                        'CURRENCY': response_dict['CURRENCY'],
                        'BANKNAME': response_dict['BANKNAME'],
                        'PAYMENTMODE': response_dict['PAYMENTMODE'],
                        'TXNID': response_dict['TXNID'],
                        'TXNAMOUNT': response_dict['TXNAMOUNT'],
                        'BANKTXNID': response_dict['BANKTXNID'],
                        'TXNDATE': response_dict['TXNDATE'],
                        'STATUS': response_dict['STATUS']
                    }
                    db.collection('bookingRegister').document(i.id).update(data_Update)

                return redirect('/receipt/OrderID%3D' + response_dict['ORDERID'])
            else:
                obj = db.collection('bookingRegister').where('orderID', '==', response_dict['ORDERID']).stream()
                for i in obj:
                    db.collection('bookingRegister').document(i.id).delete()
        return render(request, 'paymentstatus.html', {'response': response_dict, 'temp': temperature})
    else:
        return redirect('/')


def print_pageshow(request, orderID):
    try:
        obj = db.collection('bookingRegister').where('orderID', '==', orderID).stream()
        userID = {}
        order_data = {}
        roomID = []
        for i in obj:
            order_data = i.to_dict()
            userID = order_data['clientID']
            roomID.append(order_data['roomID'])
        roomName = []
        for i in roomID:
            roomName.append(db.collection('roomRegister').document(i).get().to_dict()['roomName'])
        user_data = db.collection('clientRegister').document(userID).get().to_dict()
        data = {
            'orderID': orderID,
            'user': user_data,
            'order': order_data,
            'roomName': roomName,
            'temp': temperature
        }
        return render(request, 'print.html', data)
    except Exception as e:
        print(e)
        return redirect('/')
