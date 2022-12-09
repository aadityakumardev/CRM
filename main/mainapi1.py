from typing import Dict, List
from firebase_admin import firestore
from datetime import datetime
from google.cloud.firestore_v1.document import DocumentReference
from .store import insertFile
def add_data_one(collection,data,doc_id=None):
    db = firestore.Client()
    if doc_id==None:
        doc_ref = db.collection(collection).document()
        
    else:
        doc_ref = db.collection(collection).document(doc_id)
    doc_ref.set(data,merge=True)
    return doc_ref


class User:
    uid : str
    email : str
    display_name : str
    created_time : datetime
    phone_number : str
    photo_url : str
    have_address : bool
    deactivate  : bool
    address : DocumentReference=None
    addresses : List[DocumentReference]

    @classmethod
    def getUser(cls,uid:str):
        db = firestore.Client()
        ref=db.collection('users').document(uid).get().to_dict()
        cls.uid = ref['uid'] if "uid" in ref else ''
        cls.email = ref['email'] if "email" in ref else ''
        cls.display_name = ref['display_name'] if "display_name" in ref else ''
        cls.created_time = ref['created_time'] if "created_time" in ref else datetime.now()
        cls.phone_number = ref['phone_number'] if "phone_number" in ref else ''
        cls.photo_url = ref['photo_url'] if "photo_url" in ref else ''
        cls.have_address = ref['have_address'] if "have_address" in ref else False
        cls.deactivate = ref['deactivate'] if "deactivate" in ref else False
        cls.address = ref['address'] if "address" in ref else None
        cls.addresses = ref['addresses'] if "addresses" in ref else []
        return cls
    
class Product:
    part_code : str
    p_name : str
    description : str
    brand: str
    price : float
    model_number : str
    categories : DocumentReference=None
    images : List[str]
    have_serial_no : bool

    @classmethod
    def getProduct(cls,part_code:str):
        db = firestore.Client()
        ref=db.collection('product').document(part_code).get().to_dict()
        cls.part_code = ref['part_code'] if 'part_code' in ref else ''
        cls.p_name = ref['p_name'] if 'p_name' in ref else ''
        cls.description = ref['description'] if 'description' in ref else ''
        cls.brand = ref['brand'] if 'brand' in ref else ''
        cls.price = ref['price'] if 'price' in ref else 0.0
        cls.model_number = ref['model_number'] if 'model_number' in ref else ''
        cls.categories = ref['categories'] if 'categories' in ref else None
        cls.images = ref['images'] if 'images' in ref else []
        cls.have_serial_no = ref['have_serial_no'] if 'have_serial_no' in ref else False
        return cls
    @classmethod
    def createProduct(cls , part_code : str,p_name:str,description:str,brand:str,price: float,model_number:str ,categories: str ,images:str = [],have_serial_no : bool = False):
        add_data_one(
            collection='product',
            data={
                'part_code':part_code,
                'p_name':p_name,
                'description':description,
                'brand':brand,
                'price':price,
                'model_number':model_number,
                'categories':Categories.getCategories(categories),
                'images':images,
                'have_serial_no':have_serial_no
                },
            doc_id=part_code
            )
        cls.part_code=part_code
        cls.p_name=p_name
        cls.description=description
        cls.brand=brand
        cls.price=price
        cls.model_number=model_number
        cls.categories=categories
        cls.images=images
        cls.have_serial_no=have_serial_no
        return cls()
    @classmethod
    def updateProduct(cls , part_code : str , p_name:str = None,description:str = None,brand:str = None,price: float = None,model_number:str =None ,categories: str = None,images: List[str] = None,have_serial_no : bool = None):
        dic={}
        if p_name!=None : dic['p_name']=p_name
        if description!=None : dic['description']=description
        if brand!=None : dic['brand']=brand
        if price!=None : dic['price']=price
        if model_number!=None : dic['model_number']=model_number
        if categories!=None : dic['categories']=Categories.getCategories(categories) 
        if images!=None : dic['images']=images
        if have_serial_no!=None : dic['have_serial_no']=have_serial_no
        add_data_one(
            collection='product',
            data=dic,
            doc_id=part_code
            )
        cls.part_code=part_code
        cls.p_name=p_name
        cls.description=description
        cls.brand=brand
        cls.price=price
        cls.model_number=model_number
        cls.categories=categories
        cls.images=images
        cls.have_serial_no=have_serial_no
        return cls()

    def inserImages(self,no_of_imgs : int):
        lis=list()
        for i in range(no_of_imgs):
            lis.append(insertFile('product',self.part_code))
        self.updateProduct(part_code=self.part_code,images=lis)

class InProduct:
    productRef : DocumentReference=None
    selected_out_q : int 
    quantity : int
    selected_in_q : int 
    serial_number : List[str]
    defectives : List[Dict]
    put : List[str]

    @classmethod
    def getInProduct(cls,ref):
        db = firestore.Client()
        ref=ref.to_dict()
        cls.productRef = ref['productRef'] if 'productRef' in ref else None
        cls.selected_out_q = ref['selected_out_q'] if 'selected_out_q' in ref else 0
        cls.quantity = ref['quantity'] if 'quantity' in ref else 0
        cls.selected_in_q = ref['selected_in_q'] if 'selected_in_q' in ref else 0
        cls.serial_number = ref['serial_number'] if 'serial_number' in ref else []
        cls.defectives = ref['defectives'] if 'defectives' in ref else []
        cls.put = ref['put'] if 'put' in ref else []
        return cls


class Categories : 
    name : str
    image : str 
    @classmethod
    def getCategories(cls,name :str):
        '''this method will give you reference of the category by passing name of category'''
        db = firestore.Client()
        doc_ref = db.collection(u'Categories').where(u'name', u'==', name).stream()
        for i in doc_ref:
            return i.reference

    @classmethod
    def getall(cls) -> list:
        '''this method will give you all categories'''
        db = firestore.Client()
        doc_ref = list(map((lambda x: x.to_dict()['name']),db.collection(u'Categories').stream()))
        return doc_ref

class Log :
    date : datetime
    state : str
    addressref : DocumentReference=None
    remark : str
    complain : str
    created_for : DocumentReference=None
    out_bucket : List[DocumentReference]
    products : List[DocumentReference]
    total_amt : float
    in_bucket : List[DocumentReference]
    orderid : str
    jobsheetnumber : str
    created_by : str

    @classmethod
    def createLog(cls,data):
        # data = data.to_dict()
        # print("Running add data")
        add_data_one(
            collection='logs_list',
            data = data,
            doc_id=data['jobsheetnumber']
        )
        cls.date = data['date'] if "date" in data else None
        cls.state = data['state'] if "state" in data else str
        cls.addressref = data['addressref'] if "addressref" in data else None
        cls.remark = data['remark'] if "remark" in data else str
        cls.complain = data['complain'] if "complain" in data else str
        #cls.created_for = data['created_for'] if "created_for" in data else None
        cls.out_bucket = data['out_bucket'] if "out_bucket" in data else []
        #cls.products = data['products'] if "products" in data else []
        cls.total_amt = data['total_amt'] if "total_amt" in data else 0
        cls.in_bucket = data['in_bucket'] if "in_bucket" in data else []
        cls.orderid = data['orderid'] if "orderid" in data else str
        cls.jobsheetnumber = data['jobsheetnumber'] if "jobsheetnumber" in data else str
        cls.created_by = data['created_by'] if "created_by" in data else str
        # print("fuction runed")
        return cls()
    def setEngineer(self,userRef):
        add_data_one(
            collection='logs_list',
            data = {'created_for':userRef},
            doc_id='testing_0001'
        )
        self.created_by=userRef
    def setProducts(self,productlist):
        add_data_one(
            collection='logs_list',
            data = {'created':productlist},
            doc_id='testing_0001'
        )
        self.products=productlist


    @classmethod
    def readLog(cls,jobsheetnumber:str):
        db = firestore.Client()
        doc_ref = db.collection(u'logs_list').document(jobsheetnumber)
        data = doc_ref.get().to_dict()

        cls.date = data['date'] if "date" in data else None
        cls.state = data['state'] if "state" in data else str
        cls.addressref = data['addressref'] if "addressref" in data else None
        cls.remark = data['remark'] if "remark" in data else str
        cls.complain = data['complain'] if "complain" in data else str
        cls.created_for = data['created_for'] if "created_for" in data else None
        cls.out_bucket = data['out_bucket'] if "out_bucket" in data else []
        cls.products = data['products'] if "products" in data else []
        cls.total_amt = data['total_amt'] if "total_amt" in data else 0
        cls.in_bucket = data['in_bucket'] if "in_bucket" in data else []
        cls.orderid = data['orderid'] if "orderid" in data else str
        cls.jobsheetnumber = data['jobsheetnumber'] if "jobsheetnumber" in data else str
        cls.created_by = data['created_by'] if "created_by" in data else str
        
        return cls()        

if "__main__" == __name__:
    # pro1=Product.createProduct( part_code='test004',
    #                             p_name='testing',
    #                             description='testing',
    #                             brand='test',
    #                             price=0,
    #                             model_number='test Ultra Pro',
    #                             categories='Accessories',
    #                             ).inserImages(2)
    data = {
        'state':"madhya pradesh",
        'remark':"testing api",
        'complain':"not testing api",
        'total_amt':800000,
        'orderid':'ORPDJFLS65446',
        'jobsheetnumber':'SERNIOG668',
        'created_by':"aditya",
    }
    log1 = Log.createLog(data)
    log_det = Log.readLog("SERNIOG668")
    print(log_det,log_det.orderid)
