from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
from ultralytics import YOLO
import numpy as np
from PIL import Image
import os
from django.conf import settings
import pandas as pd
from urllib.parse import quote

# Path to save annotated images
MEDIA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'media')

def upload_image(request):
    if request.method == 'POST' and request.FILES['file']:
        # Save the uploaded file
        uploaded_file = request.FILES['file']
        fs = FileSystemStorage()
        file_name = fs.save(uploaded_file.name, uploaded_file)
        file_url = fs.url(file_name)

        # Load the YOLO model
        model_path = '/home/qasim/Desktop/langchain/attendance_system/best(1).pt'  # Replace with the path to your trained model
        model = YOLO(model_path)

        # Run inference on the uploaded image
        image_path = os.path.join(MEDIA_DIR, file_name)
        results = model(image_path)

        # Extract detected classes (as student IDs)
        detected_classes = [model.names[int(cls)] for cls in results[0].boxes.cls.cpu().numpy()]

        # Annotate the image
        annotated_image_array = results[0].plot()  # Returns the annotated image as a NumPy array
        annotated_image = Image.fromarray(np.uint8(annotated_image_array))  # Convert to PIL Image
        annotated_image_path = os.path.join(MEDIA_DIR, 'annotated_' + file_name)
        annotated_image.save(annotated_image_path)

        # Generate Excel file with detected students
        excel_file_path = os.path.join(MEDIA_DIR, 'attendance.xlsx')
        attendance_data = [{"Student ID": cls, "Presence": "Present"} for cls in detected_classes]
        df = pd.DataFrame(attendance_data)
        df.to_excel(excel_file_path, index=False)

        # Redirect to the result page with the file name and Excel file path
        return redirect(f'/result/?file_name={file_name}&excel_file={quote("attendance.xlsx")}')

    return render(request, 'attendance/upload.html')


def display_result(request):
    file_name = request.GET.get('file_name')  # Retrieve the uploaded file name
    excel_file = request.GET.get('excel_file')  # Retrieve the Excel file name
    if file_name:
        # Construct file paths
        file_path = os.path.join(settings.MEDIA_ROOT, file_name)
        annotated_image_path = os.path.join(settings.MEDIA_ROOT, 'annotated_' + file_name)
        excel_file_path = os.path.join(settings.MEDIA_ROOT, excel_file)

        # Load the YOLO model
        model_path = '/home/qasim/Desktop/langchain/attendance_system/best(1).pt'  # Replace with the path to your trained model
        model = YOLO(model_path)

        # Run inference on the uploaded image
        results = model(file_path)

        # Extract detected classes
        detected_classes = [model.names[int(cls)] for cls in results[0].boxes.cls.cpu().numpy()]

        # Pass relative URL for the annotated image
        annotated_image_url = f"{settings.MEDIA_URL}annotated_{quote(file_name)}"
        attendance_file  = f"{settings.MEDIA_URL}{quote(excel_file)}"  # URL to download the Excel file

        return render(request, 'attendance/result.html', {
            'detected_classes': detected_classes,
            'annotated_image_url': annotated_image_url,
            'attendance_file': attendance_file 
        })
    return render(request, 'attendance/result.html')
