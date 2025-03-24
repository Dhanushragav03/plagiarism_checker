import http.client

conn = http.client.HTTPSConnection("plagiarism-checker-and-auto-citation-generator-multi-lingual.p.rapidapi.com")

payload = "{\"text\":\"In the fabrication of silicon wafers to create integrated circuits, chemistry and physics play a significant role. It is important to change the silicon wafer surface conditions and properties using both innocuous and harmful compounds, particular and uncommon circumstances, plasma-state elements, and RF (Radio Frequency) energies. Starting with the production of silicon wafers, sands are molten under high temperature in order to change its molecular structure. In this process, silicon ingot with particular diameter is formed and sliced into pieces of wafer. Following by chemical manufacture, wafer would be prepared to be fabricated into integrated circuits. Then, the circuits would be drawn onto the wafer through oxidation, photolithography, etching, diffusion, and ion implanation. After those fabrication, all these components (transistors, resistors, capacitors, and so on) were only accessible as discrete units, would have taken up most of a medium-sized room 20 years ago, the devices currently fill a one-inch square IC's surface. When it comes to wafer sorting, a systematic mode will be used to take each bad die from the whole die pie. The researchers will use the relative finder and tester to gain the situation for each die and this work will bring foundation to the following stages including packaging and final test. The packaging process comes to the next consideration. This work divides the packaging process into five steps\",\"language\":\"en\",\"includeCitations\":false,\"scrapeSources\":false}"

headers = {
    'x-rapidapi-key': "157b9a8a77msh04a917fa712c05bp1651a3jsnf68dea423317",
    'x-rapidapi-host': "plagiarism-checker-and-auto-citation-generator-multi-lingual.p.rapidapi.com",
    'Content-Type': "application/json"
}

conn.request("POST", "/plagiarism", payload, headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))