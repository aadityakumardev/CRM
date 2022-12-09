import json
from django.views.decorators.csrf import csrf_exempt

from django.shortcuts import render,redirect
from django.http import JsonResponse ,HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate, login ,logout
from rest_framework.parsers import JSONParser


from .mainapi import Log
from main.forms import NewServiceForm

from .models import (Customer, Engineer, EngineerBag, Inventory, Product, Service,
ComingStockLog,PendingForOutbound,StockPayment,OutboundStockHandler,StockPaymentHandler,ClosedLog,OutboundStock)
from .serializers import ComingStockSerializer,ComingStockLogSerializer


def userlogin(request):
    if request.method == "POST" and "login" in request.POST:
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request,user)
            return redirect('/main/index/')
        else:
            return render(request,"login.html")
    return render(request,"login.html")

def userlogout(request):
    logout(request)
    return redirect('/main/userlogin/')

@login_required(login_url='/main/userlogin/')
def index(request):
    return render (request,"index.html")

@login_required(login_url='/main/userlogin/')
def tbclist(request):
    servicelist = Service.objects.all().filter(status="TBC")
    return render(request,'main/tbclist.html',{'services':servicelist})

@login_required(login_url='/main/userlogin/')
def tbblist(request):
    servicelist = Service.objects.all().filter(status="TBB")
    return render(request,'main/tbblist.html',{'services':servicelist})

@login_required(login_url='/main/userlogin/')
@csrf_exempt
def tbb(request,sid):

    engineerlist =  Engineer.objects.all()
    serviceRef = Service.objects.get(sid=sid)

    if request.method == "POST":
        try:
            post_data = json.loads(request.body.decode("utf-8"))
            data = post_data[:len(post_data)-1]
            info_data = post_data[-1]
            engineerRef = Engineer.objects.get(engineer_id = str(info_data['selected_engineer']))
            engineerRef.is_available = False
            engineerRef.serviceRef = serviceRef
            serviceRef.status = "EI"
            engineer_bag_setter(data,engineerRef)
            engineerRef.save()
            serviceRef.save()

            return HttpResponse(json.dumps({"response":"This is the response"}),content_type = 'application/json')
        except:
            HttpResponse(json.dumps({"Error":"There was an error"}),content_type = 'application/json')
        

    context = {
        'service':serviceRef,
        'engineerlist':engineerlist,

    }
    return render(request,'main/tbb.html',context)


def engineer_bag_setter(data,engineerRef,serviceRef=None):
    totalVal = 0
    if serviceRef == None:
        for product in data:
            partcodeRef = Product.objects.get(partcode = product['partcode'])
            productInInventory = Inventory.objects.get(productRef = partcodeRef)
            productInInventory.quantity -= int(product['quantity'])
            productInInventory.save()
            EngineerBag.objects.create(
                engineer_id = engineerRef,
                partcode = partcodeRef,
                serviceRef = engineerRef.serviceRef,
                price = product['price'],
                quantity = product['quantity']
            )
            totalVal += (int(product['price'])*int(product['quantity']))
    else:
        for product in data:
            partcodeRef = Product.objects.get(partcode = product['partcode'])
            productInInventory = Inventory.objects.get(productRef = partcodeRef)
            productInInventory.quantity -= int(product['quantity'])
            productInInventory.save()
            EngineerBag.objects.create(
                engineer_id = engineerRef,
                partcode = partcodeRef,
                serviceRef = serviceRef,
                price = product['price'],
                quantity = product['quantity']
            )

            totalVal += (int(product['price'])*int(product['quantity']))

    engineerRef.current_bag_value = totalVal
    engineerRef.save()
    return 201


@login_required(login_url='/main/userlogin/')
def tbc(request,sid):
    service = Service.objects.get(sid=sid)
    if request.method=="POST" and "accept" in request.POST:
        special_remark = request.POST['specialremark']
        service.special_remark = special_remark
        service.is_determined = True
        service.status = "TBB"
        service.save()
        messages.success(request,"Service Accepted !")

    return render(request,'main/tbc.html',{'service':service})

def latestuserid():
    user = Customer.objects.all().latest('customer_id')
    return user

def getuserid(userid):
    user = Customer.objects.get(customer_id = userid)
    return user

@login_required(login_url='/main/userlogin/')
def newservice(request):
    form = NewServiceForm()
    if request.method == "POST":
        form = NewServiceForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            contact_number = form.cleaned_data['contact_number']
            alternate_number = form.cleaned_data['alternate_number']
            gender = form.cleaned_data['gender']
            appelation = form.cleaned_data['appelation']
            email_id = form.cleaned_data['email_id']
            address = form.cleaned_data['address']
            city = form.cleaned_data['city']
            State = form.cleaned_data['State']
            pincode = form.cleaned_data['pincode']
            remark = form.cleaned_data['remark']
            complain = form.cleaned_data['complain']
            # print(name,contact_number,alternate_number,gender,appelation,email_id,address,city,State,pincode,remark,complain)
            Customer.objects.create(
                name = name,
                contact_number = contact_number,
                alternate_number = alternate_number,
                gender = gender,
                appelation = appelation,
                email_id = email_id,
                address = address,
                city = city,
                State = State,
                pincode = pincode,
            )
            creteduser = latestuserid()
            print(creteduser)
            user = getuserid(creteduser)
            print(user)
            Service.objects.create(
                customer_id = user,
                complain = complain,
                remark = remark,
            )
            messages.success(request,"Service Created Successfully!")
    else:
        form = NewServiceForm()
        
    context = {
        "form" : form,
    }
    return render(request,"main/newservice.html",context)

@login_required(login_url='/main/userlogin/')
def inspection_list(request):
    in_list = Service.objects.filter(status = "EI")
    context = {
        "in_list":in_list
    }
    return render(request,"main/inspectionlist.html",context)

@login_required(login_url='/main/userlogin/')
@csrf_exempt
def engineerinspection(request,sid):
    serviceObj = Service.objects.get(sid = sid)
    if serviceObj.status == "EI":
        engineers_assigned = Engineer.objects.filter(serviceRef = serviceObj)
        engineerlist =  Engineer.objects.all()
        inwarranty_used_stock = EngineerBag.objects.filter(serviceRef=serviceObj).filter(is_used=True).filter(is_inwarranty = True)
        outwarranty_used_stock = EngineerBag.objects.filter(serviceRef=serviceObj).filter(is_used=True).filter(is_inwarranty = False)
        products = EngineerBag.objects.filter(serviceRef=serviceObj).filter(is_used=False)
        
        if request.method == "POST" and "determine" in request.POST:
            try:
                post_data = json.loads(request.body.decode("utf-8"))
                print(post_data)

                data = post_data[:len(post_data)-1]
                info_data = post_data[-1]
                print(info_data)

                engineerRef = Engineer.objects.get(engineer_id = str(info_data['selected_engineer']))
                engineerRef.is_available = False
                engineerRef.serviceRef = serviceObj
                print(engineerRef,serviceObj)
                engineer_bag_setter(data,engineerRef,serviceObj)
                engineerRef.save()
                messages.success(request,"Engineer Assigned !")
                return HttpResponse(json.dumps({"response":"This is the response"}),content_type = 'application/json')
            except:
                messages.error(request,"Cant Assign Engineer !")
                return HttpResponse(json.dumps({"response":"Error"}),content_type = 'application/json')

        if request.method == "POST" and "rollback" in request.POST:
            if serviceObj.can_rollback == True:
                if products.count()>0:
                    for product in products:
                        inventoryProduct = Inventory.objects.get(productRef = product.partcode)
                        inventoryProduct.quantity += product.quantity
                        inventoryProduct.save()
                        products.delete()
                        messages.success(request,"Products rolledback to inventory successfully !")
            else:
                messages.warning(request,"Cannot Rollback until outbound is clear !")

        if request.method == "POST" and "inwarranty_outbound" in request.POST:
            if inwarranty_used_stock.count()>0:
                objectlist = []
                number_of_products = 0
                for product in inwarranty_used_stock:
                    obj = PendingForOutbound(
                        productRef = product.partcode,
                        quantity = product.quantity,
                        serviceRef = product.serviceRef,
                        in_warranty = True,
                    )
                    number_of_products += 1
                    objectlist.append(obj)
                # print(objectlist)
                if len(objectlist) > 0:
                    outboundStockHandlerRef = OutboundStockHandler(
                        serviceRef = serviceObj,
                        numberofproducts = number_of_products,
                    )
                    outboundStockHandlerRef.save()
                    PendingForOutbound.objects.bulk_create(objectlist)
                    PendingForOutbound.objects.filter(serviceRef=serviceObj).filter(in_warranty=True).update(pforef = outboundStockHandlerRef)
                    inwarranty_used_stock.delete()
                    messages.success(request,"successfully sent to outbound !")
                    if outwarranty_used_stock.count() == 0:
                        serviceObj.can_rollback = True
                        serviceObj.save()
            else:
                messages.error(request,"No inwarranty product added !")
                        
        if request.method == "POST" and "outwarranty_outbound" in request.POST:
            if outwarranty_used_stock.count()>0:
                objectlist = []
                number_of_products = 0
                for product in outwarranty_used_stock:
                    obj = StockPayment(
                        productRef = product.partcode,
                        quantity = product.quantity,
                        serviceRef = product.serviceRef,
                    )
                    number_of_products += 1
                    objectlist.append(obj)
                print(objectlist)
                
                if len(objectlist) > 0:
                    stockPaymentHandlerRef = StockPaymentHandler(
                        serviceRef = serviceObj,
                        numberofproducts = number_of_products,
                    )
                    stockPaymentHandlerRef.save()
                    StockPayment.objects.bulk_create(objectlist)
                    StockPayment.objects.filter(serviceRef = serviceObj).update(stockPaymentHandlerRef = stockPaymentHandlerRef)
                    outwarranty_used_stock.delete()
                    messages.success(request,"Products sent to pending for payment !")
                    if inwarranty_used_stock.count() == 0:
                        serviceObj.can_rollback = True
                        serviceObj.save()
            else:
                messages.error(request,"No Out-warranty product !")

        if request.method == "POST" and 'proceed' in request.POST:
            if inwarranty_used_stock.count()==0 and outwarranty_used_stock.count()==0 and products.count() == 0:
                serviceObj.status = "PFO"
                engineers_assigned.update(is_available=True)
                serviceObj.save()
                messages.success(request,"Successfull Proceeded !")
            else:
                messages.info(request,"Cant Proceed Yet Clear all the products !")
    else:
        return HttpResponse(404)


    context = {
        'service':serviceObj,
        'engineers_assigned':engineers_assigned,
        'engineerlist':engineerlist,
        'products':products,
        'inwarranty_used_stock':inwarranty_used_stock,
        'outwarranty_used_stock':outwarranty_used_stock,
    }
    return render(request,'main/engineerinspection.html',context)


@csrf_exempt
def productlist(request):
    products = Product.objects.all()
    allProducts = []   
    for i in range(len(products)):
        productobj = {}
        productobj.update({
            "partcode":products[i].partcode,
            "description":products[i].description,
            "modelnumber":products[i].modelnumber,
            "price":products[i].price,
            "warranty":products[i].warranty,
            "unit":products[i].unit,
        })
        allProducts.append(productobj)

    if request.method == "GET":
        return HttpResponse(json.dumps(allProducts,indent=4),content_type = 'application/json')
        # return JsonResponse(json.dumps(allProducts,indent=4),safe=False)
    if request.method == "POST":
        post_data = json.loads(request.body.decode("utf-8"))
        print(post_data)
        return HttpResponse(json.dumps({"response":"This is the response"}),content_type = 'application/json')

def getInventoryProduct(request,partcode):
    try:
        productobj = Product.objects.get(partcode = partcode)
        product = Inventory.objects.get(productRef = productobj)
    except:
        return HttpResponse("null")
    if request.method == "GET":
        return HttpResponse(json.dumps({"quantity":product.quantity},indent=4),content_type = 'application/json')

@csrf_exempt
def testingapi(request):
    if request.method == "POST":
        try:
            json_data = JSONParser().parse(request)
            logserializer = ComingStockLogSerializer(data = json_data[-1])
            # stock_data = json_data[:len(json_data)-1]
            print(logserializer)
            if logserializer.is_valid():
                logserializer.save()
                print("saved")
            # log_id = ComingStockLog.objects.latest('log_id')
            # print(log_id)
            # for data in stock_data:
            #     data['log_id'] = log_id
            #     stockserializer = ComingStockSerializer(data = data)
            #     if stockserializer.is_valid():
            #         stockserializer.save()
            #         print("saved")
                return JsonResponse(logserializer.data,status=201)
            return JsonResponse(logserializer.errors,status=400)
        except:
            return HttpResponse(status = 400)
    return HttpResponse(status=404)


def stockapproval(request):
    return render(request,"main/stockapproval.html")

@csrf_exempt
def testing(request):
    if request.method == "POST":
        customerobj = Customer(
            name = 'adityakumardev',
            contact_number = 7999414059,
            gender = 'Male',
            appelation = 'Mr',
            email_id = 'adityakumar79300@gmail.com',
            address = 'waidhan',
            city = 'Indore',
            State = 'MP',
            pincode = 486886,
        )
        customerobj.save()
        print(customerobj.customer_id)

        return HttpResponse(status = 200)

@login_required(login_url='/main/userlogin/')
def inventory(request):
    products = Inventory.objects.all()
    return render(request,'main/inventory.html',{"products":products})

@login_required(login_url='/main/userlogin/')
def pfolist(request):
    pfo_list = OutboundStockHandler.objects.filter(is_done=False).filter(is_done=False)
    return render(request,"main/pfolist.html",{'pfo_list':pfo_list})

@login_required(login_url='/main/userlogin/')
def pfplist(request):
    pfp_list = StockPaymentHandler.objects.filter(is_payed = False)
    return render(request,"main/pfplist.html",{'pfp_list':pfp_list})

@login_required(login_url='/main/userlogin/')
def inpfolist(request):
    in_pfo_list = StockPaymentHandler.objects.filter(is_payed = True).filter(is_done=False)
    return render(request,"main/inpfolist.html",{"inpfolist":in_pfo_list})

@login_required(login_url='/main/userlogin/')

def pendingforpayment(request,osid):
    stockRef = StockPaymentHandler.objects.get(osid = osid)
    if stockRef.is_payed == True:
        serviceRef = stockRef.serviceRef
        products = StockPayment.objects.filter(stockPaymentHandlerRef = stockRef)

        if request.method == "POST" and "determine" in request.POST:
            object_list = []
            for product in products:
                obj = PendingForOutbound(
                        productRef = product.productRef,
                        quantity = product.quantity,
                        serviceRef = product.serviceRef,
                        pfpref = product.stockPaymentHandlerRef,
                    )
                object_list.append(obj)
            if len(object_list)>0:
                PendingForOutbound.objects.bulk_create(object_list)
                stockRef.is_payed = True
                products.delete()
                stockRef.save()
                messages.success(request,"Successfull !! Products sent to outbound !")
    else:
        HttpResponse(404)


    context = {
        "service":serviceRef,
        "products":products,
    }
    return render (request,"main/pendingforpayment.html",context)

@login_required(login_url='/main/userlogin/')
def pendingforoutbound(request,isid):
    stockRef = OutboundStockHandler.objects.get(isid = isid)
    if stockRef.is_done == False:
        serviceRef = stockRef.serviceRef
        products = PendingForOutbound.objects.filter(pforef = stockRef)
        if request.method == "POST" and 'determine' in request.POST:
            closingLog = ClosedLog.objects.filter(serviceRef = serviceRef)
            if  not closingLog.exists():
                log = ClosedLog(
                    serviceRef = serviceRef,
                    cutomerId = serviceRef.customer_id,
                    pforef = stockRef,
                )
                log.save()
                # print(log)
                objectlist = []
                for product in products:
                    obj = OutboundStock(
                        productRef = product.productRef,
                        quantity = product.quantity,
                        serviceRef = product.serviceRef,
                        pforef = product.pforef,
                        in_warranty = True,
                    )
                    objectlist.append(obj)
                if products.count() == PendingForOutbound.objects.filter(serviceRef = serviceRef).count():
                    log.is_complete = True
                    log.save()
                OutboundStock.objects.bulk_create(objectlist)
                stockRef.is_done = True
                products.delete()
                stockRef.save()
                messages.success(request,"Products Outbound Successfully !")
            else:
                objectlist = []
                for product in products:
                    obj = OutboundStock(
                        productRef = product.productRef,
                        quantity = product.quantity,
                        serviceRef = product.serviceRef,
                        pforef = product.pforef,
                        in_warranty = True,
                    )
                    objectlist.append(obj)
                OutboundStock.objects.bulk_create(objectlist)
                stockRef.is_done = True
                products.delete()
                stockRef.save()
                messages.success(request,"Products Outbound Successfully !")

        context = {
        'stock':stockRef,
        "service":serviceRef,
        "products":products,
        }
        return render (request,"main/pendingforoutbound.html",context)
    else:
        return HttpResponse(404)


@login_required(login_url='/main/userlogin/')
def inwarrantypendingforoutbound(request,osid):
    stockRef = StockPaymentHandler.objects.get(osid = osid)
    if stockRef.is_done == False:
        serviceRef = stockRef.serviceRef
        products = PendingForOutbound.objects.filter(pfpref = stockRef)

        if request.method == "POST" and 'determine' in request.POST:

            closingLog = ClosedLog.objects.filter(serviceRef = serviceRef)
            if  not closingLog.exists():
                log = ClosedLog(
                    serviceRef = serviceRef,
                    cutomerId = serviceRef.customer_id,
                    pforef = stockRef,
                )
                log.save()
                objectlist = []
                for product in products:
                    obj = OutboundStock(
                        productRef = product.productRef,
                        quantity = product.quantity,
                        serviceRef = product.serviceRef,
                        pfpref = product.pfpref,
                    )
                    objectlist.append(obj)
                if products.count() == PendingForOutbound.objects.filter(serviceRef = serviceRef).count():
                    log.is_complete = True
                    log.save()
                OutboundStock.objects.bulk_create(objectlist)
                stockRef.is_done=True
                products.delete()
                stockRef.save()
                messages.success(request,"Products Outbound Successfully !")
            else:
                objectlist = []
                for product in products:
                    obj = OutboundStock(
                        productRef = product.productRef,
                        quantity = product.quantity,
                        serviceRef = product.serviceRef,
                        pfpref = product.pfpref,
                    )
                    objectlist.append(obj)
                OutboundStock.objects.bulk_create(objectlist)
                stockRef.is_done=True
                products.delete()
                stockRef.save()
                messages.success(request,"Products Outbound Successfully !")
            
        context = {
            'stock':stockRef,
            "service":serviceRef,
            "products":products,
        }
        return render (request,"main/inwarrantypendingforoutbound.html",context)
    
    else:
        return HttpResponse(404)

@login_required(login_url='/main/userlogin/')
def tbdlist(request):
    logs = ClosedLog.objects.filter(is_close = False).filter(is_complete = True)
    context = {
        'logs':logs,
    }
    return render(request,"main/tbdlist.html",context)

@login_required(login_url='/main/userlogin/')
def tbd(request,logid):
    try:
        log = ClosedLog.objects.get(logId = logid)
        if log.is_close == False:
            in_warranty_products = OutboundStock.objects.filter(pforef = log.pforef)
            out_warranty_products = OutboundStock.objects.filter(pfpref = log.pfpref)
            
            if request.method == "POST" and 'closelog' in request.POST:
                remark = request.POST.get('remark') # remark for the log
                log.is_close = True # close the log to remove it form the tbd List
                log.save()
                messages.success(request,f"Log ID {log.logId} Closed Successfully !")
            context = {
                'log':log,
                "inproduct":in_warranty_products,
                "outproduct":out_warranty_products,
            }
            
            return render(request,"main/tbd.html",context)
    except:
        return HttpResponse(404)
    return HttpResponse(404)
    
@login_required(login_url='/main/userlogin/')
def closedloglist(request):
    logs = ClosedLog.objects.all()
    return render(request,"main/closedloglist.html",{"logs":logs})

@csrf_exempt
def logapi(request):
    if request.method == "GET":
        log_det = Log.readLog("SERNIOG668")
        print(log_det,log_det.orderid)

        return HttpResponse(200)
    if request.method == "POST":
        data = {
            'state':"madhya pradesh",
            'remark':"testing api",
            'complain':"not testing api",
            'total_amt':111111,
            'orderid':'ORPDJFLS65446',
            'jobsheetnumber':'SERNIOG668',
            'created_by':"aditya",
        }
        log1 = Log.createLog(data)
        return HttpResponse(200)

    return HttpResponse(202)


@csrf_exempt
def approvalapi(request):
    if request.method == 'POST':
        post_data = json.loads(request.body.decode("utf-8"))
        print(post_data)
        return HttpResponse(200)
    return HttpResponse(404)