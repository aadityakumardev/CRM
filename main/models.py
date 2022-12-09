from django.db import models
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _

class STATE_CHOICES(models.TextChoices):
   AN =  "AN",_("Andaman and Nicobar Islands"),
   AP =  "AP",_("Andhra Pradesh"),
   AR =  "AR",_("Arunachal Pradesh"),
   AS =  "AS",_("Assam"),
   BR =  "BR",_("Bihar"),
   CG =  "CG",_("Chhattisgarh"),
   CH =  "CH",_("Chandigarh"),
   DN =  "DN",_("Dadra and Nagar Haveli"),
   DD =  "DD",_("Daman and Diu"),
   DL =  "DL",_("Delhi"),
   GA =  "GA",_("Goa"),
   GJ =  "GJ",_("Gujarat"),
   HR =  "HR",_("Haryana"),
   HP =  "HP",_("Himachal Pradesh"),
   JK =  "JK",_("Jammu and Kashmir"),
   JH =  "JH",_("Jharkhand"),
   KA =  "KA",_("Karnataka"),
   KL =  "KL",_("Kerala"),
   LA =  "LA",_("Ladakh"),
   LD =  "LD",_("Lakshadweep"),
   MP =  "MP",_("Madhya Pradesh"),
   MH =  "MH",_("Maharashtra"),
   MN =  "MN",_("Manipur"),
   ML =  "ML",_("Meghalaya"),
   MZ =  "MZ",_("Mizoram"),
   NL =  "NL",_("Nagaland"),
   OD =  "OD",_("Odisha"),
   PB =  "PB",_("Punjab"),
   PY =  "PY",_("Pondicherry"),
   RJ =  "RJ",_("Rajasthan"),
   SK =  "SK",_("Sikkim"),
   TN =  "TN",_("Tamil Nadu"),
   TS =  "TS",_("Telangana"),
   TR =  "TR",_("Tripura"),
   UP =  "UP",_("Uttar Pradesh"),
   UK =  "UK",_("Uttarakhand"),
   WB =  "WB",_("West Bengal")

class GENDER_CHOICES(models.TextChoices):
    M = "M",_("Male"),
    F = "F",_("Female"),

class APPELETION_CHOICES(models.TextChoices):
    Mr = "Mr",_("Mr."),
    Miss = "Miss",_("Miss"),
    Mrs = "Mrs",_("Mrs."),

class Customer(models.Model):
    phoneNumberRegex = RegexValidator(regex = r"^\+?1?\d{8,15}$")
    pincodeRegex = RegexValidator(regex = r"^[1-9]{1}[0-9]{2}\s{0,1}[0-9]{3}$")
    nameRegex = RegexValidator(regex = r"^[A-Za-z][A-Za-z0-9_]{7,29}$")

    customer_id = models.CharField(max_length=10,primary_key=True,null=False,default="")
    name = models.CharField(max_length=32)
    contact_number = models.CharField(validators = [phoneNumberRegex], max_length = 16, unique = True)
    alternate_number = models.CharField(validators = [phoneNumberRegex], max_length = 16, unique = True, blank=True, null=True)
    gender = models.CharField(max_length=6,choices=GENDER_CHOICES.choices)
    appelation = models.CharField(max_length=4,choices=APPELETION_CHOICES.choices)
    email_id = models.EmailField(max_length=128)
    address = models.CharField(max_length=128)
    city = models.CharField(max_length=32)
    State = models.CharField(max_length=2,choices=STATE_CHOICES.choices)
    pincode = models.CharField(validators = [pincodeRegex],max_length=7)

    def save(self,*args,**kwargs):
        if self.customer_id == "":
            existing_customer_id = Customer.objects.all().order_by('-customer_id')
            if existing_customer_id.count()>0:
                new_customer_id = int(existing_customer_id[0].customer_id[4:])+1
            else:
                new_customer_id = 1
            self.customer_id = 'CUID%05d' % new_customer_id
        super(Customer,self).save(*args,**kwargs)

    def __str__(self):
        return self.customer_id


class Service(models.Model):

    STATUS_CHOICES = (
        ("TBC","To Be Clear"),
        ("TBB","To be Bypass"),
        ("EI","Engineer Inspection"),
        ("PFO","Pending For Outbound"),
        ("PFP","Pending For Payment"),
        ("TBD","To Be Delievered"),
        ("C","Closed"),
    )

    SERVICE_TYPE_CHOICES = (
        ("NYS","Not Yet Set"),
        ("IW","In warranty"),
        ("OW","Out Warranty"),
        ("WSN","Without Serial Nuumber"),


    )
    sid = models.CharField(max_length=10,primary_key=True,null=False,default="")
    customer_id = models.ForeignKey("main.Customer",on_delete=models.SET_NULL,null=True,blank=True)
    complain = models.CharField(max_length=127)
    remark = models.CharField(max_length=255)
    is_determined = models.BooleanField(default=False)
    status = models.CharField(max_length=4,choices=STATUS_CHOICES,default="TBC")
    service_type = models.CharField(max_length=4,choices=SERVICE_TYPE_CHOICES,default="NYS")
    timestamp = models.DateTimeField(auto_now_add=True)    
    special_remark = models.CharField(max_length=127)
    number_of_engineer_assigned = models.PositiveIntegerField(default=0)
    can_rollback = models.BooleanField(default=False)
    
    def save(self,*args,**kwargs):
        if self.sid == "":
            existing_sid = Service.objects.all().order_by('-sid')
            if existing_sid.count()>0:
                new_sid = int(existing_sid[0].sid[3:])+1
            else:
                new_sid = 1
            self.sid = 'SID%06d' % new_sid
        super(Service,self).save(*args,**kwargs)

    def __str__(self):
        return self.sid

class Product(models.Model):
    partcode = models.CharField(max_length=10,primary_key=True,null=False)
    description = models.CharField(max_length=255)
    serialnumber = models.CharField(max_length=12,null=True,blank=True)
    modelnumber = models.CharField(max_length=12,null=True,blank=True)
    price = models.PositiveIntegerField()
    warranty = models.PositiveIntegerField()
    unit = models.CharField(max_length=10,null=True,blank=True)

    def __str__(self):
        return self.partcode +" | "+self.description


class Engineer(models.Model):
    phoneNumberRegex = RegexValidator(regex = r"^\+?1?\d{8,15}$")

    engineer_id = models.CharField(max_length=8)
    serviceRef = models.ForeignKey("main.Service",on_delete=models.SET_NULL,null=True,blank=True)
    name = models.CharField(max_length=63)
    contact_number = models.CharField(validators = [phoneNumberRegex], max_length = 16, unique = True)
    alternate_number = models.CharField(validators = [phoneNumberRegex], max_length = 16, unique = True, blank=True, null=True)
    email_id = models.EmailField(max_length=128)
    is_available = models.BooleanField(default=True)
    is_multitasking = models.BooleanField(default=False)
    current_bag_value = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.engineer_id+" "+self.name 

class Inventory(models.Model):
    productRef = models.ForeignKey("main.Product", on_delete=models.CASCADE)
    serialnumber = models.CharField(max_length=12,null=True,blank=True)
    modelnumber = models.CharField(max_length=23,null=True,blank=True)
    price = models.PositiveIntegerField(default=0)
    quantity = models.PositiveSmallIntegerField(default=0)
    cgst = models.FloatField(default=9.0)
    igst = models.FloatField(default=9.0)
    msrp = models.DecimalField(max_digits=10,decimal_places=2,default=0.0)
    amount = models.DecimalField(max_digits=10,decimal_places=2,default=0.0)

    def save(self):
        self.price = self.productRef.price
        self.msrp = self.price + (self.price * (self.cgst + self.igst))/100
        self.amount = self.msrp*self.quantity
        super().save()


    def __str__(self):
        return self.productRef.partcode


class EngineerBag(models.Model):
    engineer_id = models.ForeignKey("main.Engineer",on_delete=models.CASCADE)
    partcode = models.ForeignKey("main.Product", on_delete=models.CASCADE)
    serviceRef = models.ForeignKey("main.Service",on_delete=models.SET_NULL,null=True)
    # serialnumber = models.CharField(max_length=12,null=True,blank=True)
    modelnumber = models.CharField(max_length=23,null=True,blank=True)
    price = models.PositiveIntegerField()
    quantity = models.PositiveSmallIntegerField()
    is_used = models.BooleanField(default=False)
    is_inwarranty = models.BooleanField(default=False)

    def __str__(self):
        return self.engineer_id.engineer_id + " | " + self.partcode.partcode + " | " + self.partcode.description


class ComingStockLog(models.Model):
    STATE_CHOICES = (
        ('pending','pending'),
        ('accepted','accepted'),
        ('declined','declined'),
    )
    cmlog_id = models.CharField(max_length=12,primary_key=True,null=False,default="")
    timestamp = models.DateTimeField(auto_now_add=True)
    stock_value = models.DecimalField(max_digits=20,decimal_places=2)
    supplier_id = models.CharField(max_length = 15)
    material_type = models.CharField(max_length = 15)
    state = models.CharField(max_length=10,choices=STATE_CHOICES,default = "pending")

    def save(self,*args,**kwargs):
        if self.log_id == "":
            existing_log_id = ComingStockLog.objects.all().order_by('-log_id')
            if existing_log_id.count()>0:
                new_log_id = int(existing_log_id[0].log_id[5:])+1
            else:
                new_log_id = 1
            self.log_id = 'CMLOG%05d' % new_log_id
        super(ComingStockLog,self).save(*args,**kwargs)

    def __str__(self):
        return self.log_id



class ComingStock(models.Model):
    cmlogRef = models.ForeignKey("main.ComingStockLog",on_delete=models.SET_NULL,null=True)
    partcode = models.CharField(max_length=12)
    quantity = models.PositiveIntegerField()
    serial_numbers = models.JSONField(default = None,null=True,blank=True)

    def __str__(self):
        return self.log_id.lod_id



# ALREADY CREATED TO HANDLE COMING STOCK

# class Agency(models.Model):
#     agency_id = models.CharField(max_length=12,primary_key=True,null=False,default='')
#     name = models.CharField(max_length=50)
#     email_id = models.EmailField()

# class PendingStock(models.Model):
#     pendingstockid = models.CharField(max_length=10,primary_key=True,null=False)
#     agencyRef = models.ForeignKey("main.Agency",on_delete=models.SET_NULL,null=True)
#     timestamp = models.DateTimeField(auto_now_add=True)
#     stockvalue = models.PositiveIntegerField()

#     def save(self,*args,**kwargs):
#         if self.pendingstockid == "":
#             existing_pendingstockid = PendingStock.objects.all().order_by('-pendingstockid')
#             if existing_pendingstockid.count()>0:
#                 new_pendingstockid = int(existing_pendingstockid[0].pendingstockid[4:])+1
#             else:
#                 new_pendingstockid = 1
#             self.pendingstockid = 'PSID%06d' % new_pendingstockid
#         super(PendingStock,self).save(*args,**kwargs)


# class PendingStockProducts(models.Model):
#     productRef = models.ForeignKey("main.Product",on_delete=models.SET_NULL,null=True)
#     pendingstockRef = models.ForeignKey("main.PendingStock",on_delete=models.SET_NULL,null=True)
#     quantity = models.PositiveIntegerField()


class PendingForOutbound(models.Model):
    productRef = models.ForeignKey("main.Product",on_delete=models.SET_NULL,null=True)
    quantity = models.PositiveIntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    serviceRef = models.ForeignKey("main.Service", on_delete=models.SET_NULL,null=True)
    pforef = models.ForeignKey("main.OutboundStockHandler", on_delete=models.SET_NULL,null=True,blank=True)
    pfpref = models.ForeignKey("main.StockPaymentHandler", on_delete=models.SET_NULL,null=True,blank=True)
    is_payed = models.BooleanField(default=False)
    in_warranty = models.BooleanField(default=False)

class OutboundStockHandler(models.Model):
    isid = models.CharField(max_length=10,primary_key=True,null=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    serviceRef = models.ForeignKey("main.Service",on_delete=models.SET_NULL,null=True)
    numberofproducts = models.PositiveIntegerField(default=0)
    is_done = models.BooleanField(default=False)

    
    def save(self,*args,**kwargs):
        if self.isid == "":
            existing_isid = OutboundStockHandler.objects.all().order_by('-isid')
            if existing_isid.count()>0:
                new_isid = int(existing_isid[0].isid[4:])+1
            else:
                new_isid = 1
            self.isid = 'ISID%05d' % new_isid
        super(OutboundStockHandler,self).save(*args,**kwargs)

class StockPaymentHandler(models.Model):
    osid = models.CharField(max_length=10,primary_key=True,null=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    serviceRef = models.ForeignKey("main.Service",on_delete=models.SET_NULL,null=True)
    numberofproducts = models.PositiveIntegerField(default=0)
    is_payed = models.BooleanField(default=False)
    is_done = models.BooleanField(default=False)

    def save(self,*args,**kwargs):
        if self.osid == "":
            existing_osid = StockPaymentHandler.objects.all().order_by('-osid')
            if existing_osid.count()>0:
                new_osid = int(existing_osid[0].osid[4:])+1
            else:
                new_osid = 1
            self.osid = 'OSID%05d' % new_osid
        super(StockPaymentHandler,self).save(*args,**kwargs)


class PendingForInbound(models.Model):
    productRef = models.ForeignKey("main.Product",on_delete=models.SET_NULL,null=True)
    quantity = models.PositiveIntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    serviceRef = models.ForeignKey("main.Service",  on_delete=models.SET_NULL,null=True)

    def __str__(self):
        return self.productRef.partcode


class OutboundStock(models.Model):
    productRef = models.ForeignKey("main.Product",on_delete=models.SET_NULL,null=True)
    quantity = models.PositiveIntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    serviceRef = models.ForeignKey("main.Service", on_delete=models.SET_NULL,null=True)
    pforef = models.ForeignKey("main.OutboundStockHandler", on_delete=models.SET_NULL,null=True,blank=True)
    pfpref = models.ForeignKey("main.StockPaymentHandler", on_delete=models.SET_NULL,null=True,blank=True)
    in_warranty = models.BooleanField(default=False)


class StockPayment(models.Model):
    productRef = models.ForeignKey("main.Product",on_delete=models.SET_NULL,null=True)
    quantity = models.PositiveIntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    serviceRef = models.ForeignKey("main.Service", on_delete=models.SET_NULL,null=True)
    stockPaymentHandlerRef = models.ForeignKey("main.StockPaymentHandler",on_delete=models.SET_NULL,null=True)


class PAYMENT_METHOD_CHOICES(models.TextChoices):
    Online = "Online",_("Online"),
    COD = "Cash On Delivery",_("Cash On Delivery"),

class PaymentRecord(models.Model):
    transaction_id = models.CharField(max_length=32)
    timestamp = models.DateTimeField(auto_now_add=True)
    customerRef = models.ForeignKey("main.Customer",on_delete=models.SET_NULL,null=True)
    name = models.CharField(max_length=32)
    payment_method = models.CharField(max_length=20,choices=PAYMENT_METHOD_CHOICES.choices)
    amount = models.PositiveIntegerField()


class ClosedLog(models.Model):
    logId = models.CharField(max_length=50,primary_key=True,null=False,default="")
    timestamp = models.DateTimeField(auto_now_add=True)
    serviceRef = models.ForeignKey("main.Service",on_delete=models.SET_NULL,null=True)
    cutomerId = models.ForeignKey("main.Customer",on_delete=models.SET_NULL,null=True)
    # orderRef = models.ForeignKey("main.Order",on_delete=models.SET_NULL,null=True,blank=True)
    productRef = models.ForeignKey("main.Product",on_delete=models.SET_NULL,null=True,blank=True)
    # serialnumber = models.JSONField(default=list)
    remark = models.CharField(max_length=64,null=True,blank=True)
    pforef = models.ForeignKey("main.OutboundStockHandler", on_delete=models.SET_NULL,null=True,blank=True)
    pfpref = models.ForeignKey("main.StockPaymentHandler", on_delete=models.SET_NULL,null=True,blank=True)
    is_complete = models.BooleanField(default=False)
    is_close = models.BooleanField(default=False)


    def save(self,*args, **kwargs):
        if self.logId == "":
            # will fail in race condition fix it with Q() 
            existinglogId = ClosedLog.objects.all().order_by('-logId')
            if existinglogId.count()>0:
                new_logId = int(existinglogId[0].logId[4:])+1
            else:
                new_logId = 1
            self.logId = 'SCLG%05d' % new_logId
        super(ClosedLog,self).save(*args,**kwargs)
