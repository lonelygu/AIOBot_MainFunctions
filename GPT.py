import http.client
import base64
import json

proxy_host = '38.152.247.95'
proxy_port = 9375
proxy_user = 'NTQsXG'
proxy_pass = 'mb9vzP'
proxy_auth = base64.b64encode(f'{proxy_user}:{proxy_pass}'.encode()).decode()

openai_api_key = 'sk-proj-xE2bBGQGRdZcdcBlJSXoT3BlbkFJ1pPtIml2yZxHLIwLuc2W'
openai_api_base = 'api.openai.com'

headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {openai_api_key}',
}
def get_response(prompt):
    data = json.dumps({
        'model': 'gpt-3.5-turbo',
        'messages': [
            {'role': 'system', 'content': 'You are a helpful assistant.'},
            {'role': 'user', 'content': prompt},
        ],
        'max_tokens': 500,
        'temperature': 0.5,
    }).encode()

    conn = http.client.HTTPSConnection(proxy_host, proxy_port)

    conn.set_tunnel(openai_api_base, headers={"Proxy-Authorization": f"Basic {proxy_auth}"})

    conn.request('POST', '/v1/chat/completions', data, headers)

    try:
        res = conn.getresponse()
        if res.status == 200:
            response_data = res.read().decode()
            response_json = json.loads(response_data)
            response_text = response_json['choices'][0]['message']['content']
            return response_text
        else:
            return (f"Error: {res.status} {res.reason}")
    except http.client.ResponseNotReady:
        return "Error: Response not ready"
    finally:
        conn.close()

