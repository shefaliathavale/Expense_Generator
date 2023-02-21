# Expense Generator
A monthly expense generator web application which takes input as PDF files or images. Users can easily attach copies of their receipts directly to an expense record after logging in their account. The application allows users to add attachments by taking a picture of the receipt and uploading it on the website or directly uploading the PDF. The application converts it into text using Google Cloud Vision API. It extracts the bill value from the invoice and stores it in the database for the expense record. The bill value of the invoice is displayed to the user along with the total expenses for the current month. The application also takes the category of expense from the user and stores it in the database. The application will help the users keep a track of their expenses online and provide expense details like total expense value for the current month, expense value according to categories when required.

# Technologies Used
- Google Cloud Vision API to extract text from PDF files and use OCR to extract the final bill value. 
- RabbitMQ as a message queue to process tasks asynchronously.
- Google Storage Bucket is used to store images/PDF files when user uploads a file.
- Flask as a web server.
- Docker is used for containerization.
- Kubernetes is used for deployment. 
- ReactJS is used to develop the website. 
