import requests
import time
import json

# URL for the request to extract content
stream_url = "https://deployment-r89ftdnxa7jwwhyr97wq9lkg.stag-vxzy.zettablock.com/main"
# URL for the report_usage API
report_url = "https://quests-usage-dev.prod.zettablock.com/api/report_usage"

headers = {
    "accept": "text/event-stream",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "en,en-US;q=0.9,si-LK;q=0.8,si;q=0.7",
    "connection": "keep-alive",
    "content-type": "application/json",
    "dnt": "1",
    "origin": "https://agents.testnet.gokite.ai",
    "referer": "https://agents.testnet.gokite.ai/",
    "sec-ch-ua": '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133")',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "cross-site",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
}

# List of messages (request texts) that the user wants to process
messages = [
    "tell me more about AI automation",
    "what is decentralized AI?",
    "how can AI benefit in business?",
    # Add more messages as needed
]

# Loop through each message
for msg in messages:
    print(f"\nProcessing message: {msg}")

    # Payload with the current request text
    payload = {
        "message": msg,
        "stream": True
    }

    # Start the timer for the stream request
    start_time = time.time()

    # Make the POST request to the stream URL
    response = requests.post(stream_url, headers=headers, json=payload, stream=True)

    # Initialize an empty string to store the extracted content
    extracted_content = ""

    # Extracting content from the response stream
    for line in response.iter_lines():
        if line:
            try:
                # Decode the line to a string and load it as JSON
                decoded_line = line.decode('utf-8')
                if decoded_line.startswith("data: "):
                    json_data = json.loads(decoded_line[6:])  # Removing the "data: " prefix
                    content = json_data["choices"][0]["delta"].get("content", "")
                    if content:  # Check if content is not None or empty
                        extracted_content += content
            except json.JSONDecodeError:
                print("Error decoding line:", line)

    # End the timer for the stream request
    end_time = time.time()

    # Calculate the time taken to receive the response
    elapsed_time = end_time - start_time
    print(f"Time taken to receive all responses: {elapsed_time:.2f} seconds")

    # Print the full content as a paragraph
    print("\nFull content extracted:")
    print(extracted_content)

    # Prepare the payload for the report_usage API
    wallet_address = "0x835d262d3a5fe2df98962659ec6b22d7d55ceae8"
    agent_id = "deployment_R89FtdnXa7jWWHyr97WQ9LKG"
    ttft = elapsed_time  # Time to first byte (using stream elapsed time)
    total_time = elapsed_time  # For simplicity, we use the same elapsed time as total time
    request_text = msg
    response_text = extracted_content

    # Payload for reporting the usage
    report_data = {
        "wallet_address": wallet_address,
        "agent_id": agent_id,
        "request_text": request_text,
        "response_text": response_text,
        "ttft": ttft,
        "total_time": total_time,
        "request_metadata": {}
    }

    # Send the POST request to report_usage API
    report_response = requests.post(report_url, headers=headers, json=report_data)

    # Check if the request was successful
    if report_response.status_code == 200:
        print("Request to report_usage API was successful.")
    else:
        print(f"Failed to report usage with status code: {report_response.status_code}")
