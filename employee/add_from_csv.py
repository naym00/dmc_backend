import csv
from rest_framework.decorators import api_view,authentication_classes,permission_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from .serializers import TrainEmployeeFromCSVSerializer
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
def add_from_csv(request):
    data=request.data["file"]
    print("data csv:",data)
    file=TrainEmployeeFromCSVSerializer(data)
    print("file :")
    # Specify the file path
    csv_file_path = 'your_file.csv'

    # Open the CSV file
    with open(csv_file_path, 'r') as file:
        # Create a CSV reader
        csv_reader = csv.reader(file)

        # Iterate through each row in the CSV file
        for row in csv_reader:
            # Access individual elements in each row
            print(row)
