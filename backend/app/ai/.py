import qrcode

# The URL for your local closet application
url = "http://localhost:3000/closet"

# Create a QR code instance
qr = qrcode.QRCode(
    version=1, # Controls the size of the QR Code (1 is the smallest)
    error_correction=qrcode.constants.ERROR_CORRECT_L, # About 7% or less errors can be corrected
    box_size=10, # How many pixels each “box” of the QR code is
    border=4, # How many boxes thick the border should be
)

# Add the URL data to the instance
qr.add_data(url)
qr.make(fit=True)

# Create an image from the QR Code instance
img = qr.make_image(fill_color="black", back_color="white")

# Save the image file
img.save("closet_qr.png")

print("QR code generated and saved as closet_qr.png")