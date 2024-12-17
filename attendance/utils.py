import torch
from PIL import Image
import os

# YOLOv8 Processing Function
def process_image(image_path):
    # Load YOLOv8 model with your custom weights
    model = torch.hub.load('ultralytics/yolov8', 'custom', path='best.pt')  # Path to your custom model

    # Run inference on the uploaded image
    results = model(image_path)

    # Extract detected classes (IDs or custom class names from training)
    detected_classes = [model.names[int(cls)] for cls in results.pred[0][:, -1].cpu().numpy()]

    # Save the annotated image
    annotated_image = results.render()[0]  # Annotated image as a NumPy array
    annotated_image_path = os.path.join('media/annotated', os.path.basename(image_path))
    Image.fromarray(annotated_image).save(annotated_image_path)

    return detected_classes, annotated_image_path
