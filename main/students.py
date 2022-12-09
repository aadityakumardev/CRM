
import firebase_admin
from firebase_admin import auth,firestore,credentials
from google.cloud.firestore_v1.document import DocumentReference
from typing import List
import datetime
import csv
cred = credentials.Certificate("cred.json")
firebase_admin.initialize_app(cred)
db = firestore.Client()
def add_data_one(collection,data,doc_id=None):
    if doc_id==None:
        doc_ref = db.collection(collection).document()
        
    else:
        doc_ref = db.collection(collection).document(doc_id)
    doc_ref.set(data,merge=True)
    return doc_ref

def updateByRef(docRef,data):
    docRef.set(data,merge=True)
    return docRef
def csv_students(path):
    Classlist=[]
    with open(path) as csvfile:
        a=list(csv.reader(csvfile))
        for row in a[1:]:
            email=row[1]
            name=row[2]
            enrollment=row[3].upper()
            phone_number=row[4] if '+91'==row[4][:3] else '+91'+row[4]
            semester=row[5]
            program=row[6]
            branch=row[7]
            section=row[8]
            department=row[9]
            present=False
            for Classes in Classlist:
                if Classes.department==department or Classes.semester==semester or Classes.program==program or Classes.branch==branch or Classes.section==section:
                    Classes.addStudent(
                        display_name=name,
                        email=email,
                        phone_number=phone_number,
                        enrollment=enrollment,
                    )
                    present=True
                    break
            if not present:
                Classlist.append(Class(
                    department=department,
                    semester=semester,
                    program=program,
                    branch=branch,
                    section=section,
                ).addStudent(
                    display_name=name,
                    email=email,
                    phone_number=phone_number,
                    enrollment=enrollment,
                ))

class Student:
    display_name:str
    email:str
    email_verified:bool
    phone_number:str
    password:str
    disabled:bool
    enrollment:str
    photo_url:str
    tg:DocumentReference
    documentrefrence:DocumentReference
    def create(self,display_name:str,email:str,phone_number:str,enrollment:str,disabled:bool=False,email_verified:bool=True,password:str=None):
        self.display_name=display_name
        self.email=email
        self.email_verified=email_verified
        self.phone_number=phone_number
        self.enrollment=enrollment
        self.password=password if password !=None else enrollment[-3:]+phone_number[-3:] 
        print(self.password)
        self.disabled=disabled
        s=auth.create_user(
            display_name=self.display_name,
            email=self.email,
            email_verified=self.email_verified,
            phone_number=self.phone_number,
            password=self.password,
            disabled=self.disabled,
        )
        self.documentrefrence=add_data_one('Users',data={u'enrollment':enrollment,u'display_name':display_name, 'email':email,"phone_number":phone_number,'created_time':datetime.datetime.now()},doc_id=s.uid)
        return self.documentrefrence
    def getStudent(self,email):
        pass
    def addPhoto(self):
        pass

    def assignTG(self,teacherRef):
        return updateByRef(docRef=self.documentrefrence,data={u'tg':teacherRef})
class Class:
    department:str 
    student: List[DocumentReference]
    semester:str
    program:str
    branch:str
    section:str
    documentreference:DocumentReference
    def __init__(self,department,semester,program,branch,section) -> None:
        self.department=department
        self.semester=semester
        self.program=program
        self.branch=branch
        self.section=section
        self.student=[]
        data={
            u'department':department,
            u'semester':semester,
            u'program':program,
            u'branch':branch,
            u'section':section,
        }
        self.documentreference= add_data_one('Sclass',data=data)
    def addStudent(self,display_name,email,phone_number,enrollment,guardians={},tg=None):
        stud=Student().create(
            display_name=display_name,
            email=email,
            phone_number=phone_number,
            enrollment=enrollment,
        )
        if tg!=None:
            stud.assignTG(tg)
        self.student.append(stud)
        self.documentreference= updateByRef(self.documentreference,data={'student':self.student})
        return self
csv_students('Untitled form.csv')

    

# Student().create(
#     display_name='Yogita Bhargava',
#     email='yogitabhargava1@gmail.com',
#     phone_number='+916264431923',
#     enrollment='20BTE3CSE10037',
# )
