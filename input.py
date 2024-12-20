import requests

# url = "http://52.220.178.236:6000/generate-pdf"
url = "http://localhost:5001/generate-pdf"
html_string = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test HTML</title>
</head>
<body>
    <h1>Hello, FastAPI!</h1>
    <p>This is a test HTML string.</p>
</body>
</html>
"""

data = {"html": html_string}

response = requests.post(url, json=data)
print(response.content)
