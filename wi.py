import requests

url = "https://api.gowinston.ai/v2/ai-content-detection"
text_to_check = "In the fabrication of silicon wafers to create integrated circuits, chemistry and physics play a significant role. It is important to change the silicon wafer surface conditions and properties using both innocuous and harmful compounds, particular and uncommon circumstances, plasma-state elements, and RF (Radio Frequency) energies. Starting with the production of silicon wafers, sands are molten under high temperature in order to change its molecular structure. In this process, silicon ingot with particular diameter is formed and sliced into pieces of wafer. Following by chemical manufacture, wafer would be prepared to be fabricated into integrated circuits. Then, the circuits would be drawn onto the wafer through oxidation, photolithography, etching, diffusion, and ion implanation. After those fabrication, all these components (transistors, resistors, capacitors, and so on) were only accessible as discrete units, would have taken up most of a medium-sized room 20 years ago, the devices currently fill a one-inch square IC's surface. When it comes to wafer sorting, a systematic mode will be used to take each bad die from the whole die pie. The researchers will use the relative finder and tester to gain the situation for each die and this work will bring foundation to the following stages including packaging and final test. The packaging process comes to the next consideration. This work divides the packaging process into five steps. All those steps are listed clearly in the essay below, from sawing up the wafer into an individual die to marking the packages. The final process after packaging is the final test. The final test is not such complicated. So this work only introduces the devices that it will use and its purpose."
payload = {
    "text": text_to_check,
    "version": "4.0",
    "sentences": True,
    "language": "en"
}
headers = {
    "Authorization": "Bearer cknGUo0JaCSNRcjzA9HjYnYciF4EZo774pQjV9wEde26fdcf",
    "Content-Type": "application/json"
}

response = requests.request("POST", url, json=payload, headers=headers)

print(response.text)