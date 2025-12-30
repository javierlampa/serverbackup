import qrcode
import os
from io import BytesIO

def generate_qr_code(product_id, product_code):
    """
    Generate a QR code for a product and save it to static/qr_codes/
    
    Args:
        product_id: ID of the product
        product_code: Code of the product (e.g., PROD-001)
    
    Returns:
        str: Relative path to the saved QR code image
    """
    # Create QR code directory if it doesn't exist
    qr_dir = os.path.join('static', 'qr_codes')
    os.makedirs(qr_dir, exist_ok=True)
    
    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    
    # QR content: product code
    qr.add_data(product_code)
    qr.make(fit=True)
    
    # Create image
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save to file
    filename = f"qr_{product_id}_{product_code}.png"
    filepath = os.path.join(qr_dir, filename)
    img.save(filepath)
    
    # Return relative path
    return os.path.join('qr_codes', filename)
