from django.urls import path
from main import views
app_name = "main"

urlpatterns = [
    path("userlogin/",views.userlogin,name="userlogin"),
    path("userlogout/",views.userlogout,name="userlogout"),
    path("index/",views.index,name="index"),
    path('newservice/',views.newservice,name="newservice"),
    path('tbclist/',views.tbclist,name='tbclist'),
    path('tbblist/',views.tbblist,name='tbblist'),
    path('pfolist/',views.pfolist,name='pfolist'),
    path('inpfolist/',views.inpfolist,name='inpfolist'),
    path('pfplist/',views.pfplist,name='pfplist'),
    path('tbdlist/',views.tbdlist,name='tbdlist'),
    path('closedloglist/',views.closedloglist,name='closedloglist'),
    path('tbc/<str:sid>/',views.tbc,name='tbc'),
    path('tbb/<str:sid>/',views.tbb,name='tbb'),
    path('engineerinspection/<str:sid>/',views.engineerinspection,name='engineerinspection'),
    path('pendingforpayment/<str:osid>/',views.pendingforpayment,name='pendingforpayment'),
    path('pendingforoutbound/<str:isid>/',views.pendingforoutbound,name='pendingforoutbound'),
    path('inwarrantypendingforoutbound/<str:osid>/',views.inwarrantypendingforoutbound,name='inwarrantypendingforoutbound'),
    path('tbd/<str:logid>/',views.tbd,name='tbd'),
    path('productslist/',views.productlist,name='productlist'),
    path('iproduct/<str:partcode>/',views.getInventoryProduct,name='iproduct'),

    path('inventory/',views.inventory,name="inventory"),

    path('inpspectionlist/',views.inspection_list,name='inspection_list'),

    path('pending-inbound/',views.stockapproval,name="pending_inbound"),
    path('testing/',views.testingapi),

    path('test/',views.testing),

    path('logapi/',views.logapi),
    path('approval/',views.approvalapi),
]
