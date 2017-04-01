# NOT REQUIRED AT THE MOMENT
# from rest_framework import serializers
# from .models import Cubes
#
#
# class CubesSerializer(serializers.Serializer):
#     """Serializer to map the Model instance into JSON format."""
#
#     def create(self, validated_data):
#         return Cubes.objects.create(**validated_data)
#
#     def update(self, instance, validated_data):
#         pass
#
#     class Meta:
#         """Meta class to map serializer's fields with the model fields."""
#         model = Cubes
#         fields = ('prodID', 'consID', 'topic', 'cnt')
#         # read_only_fields = ('date_created')
#
#         # # id = serializers.IntegerField(read_only=True)
#         # # title = serializers.CharField(required=False, allow_blank=True, max_length=100)
#         # # code = serializers.CharField(style={'base_template': 'textarea.html'})
#         # # linenos = serializers.BooleanField(required=False)
#         # # language = serializers.ChoiceField(choices=LANGUAGE_CHOICES, default='python')
#         # # style = serializers.ChoiceField(choices=STYLE_CHOICES, default='friendly')
#         #
#         #
#         # prodID = serializers.CharField(max_length=255, blank=False, unique=False)
#         # consID = serializers.CharField(max_length=255, blank=False, unique=False)
#         # topic = serializers.CharField(max_length=255, blank=False, unique=False)
#         # timestamp = serializers.DateTimeField(blank=False, unique=False)
#         # cnt = serializers.IntegerField(blank=False, unique=False)
#         # date_created = serializers.DateTimeField(auto_now_add=True)
