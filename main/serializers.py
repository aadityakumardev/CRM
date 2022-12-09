from email.policy import default
from rest_framework import serializers
from .models import ComingStock, ComingStockLog

class ComingStockLogSerializer(serializers.ModelSerializer):
    cmlog_id = serializers.CharField(default="")
    class Meta:
        model = ComingStockLog
        fields = ['stock_value','supplier_id','material_type']


class ComingStockSerializer(serializers.ModelSerializer):
    cmlog_id = ComingStockLogSerializer()
    class Meta:
        model = ComingStock
        fields = ['cmlog_id','partcode','quantity']


