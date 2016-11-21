# crawler and requests User-Agent
REQUEST = {
    'allow_redirects': True,
    'verify': False
}
HEADERS = {
    'User-Agent': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
}

# save crawler's log and result
CRAWLER_LOG = 'crawler.log'
CRAWLER_RESULT = 'crawler.json'

# plugins' payload file
SCANFILE_PAYLOAD = 'payloads/hidden_file.txt'
SCANTEMP_PAYLOAD = 'payloads/temp_file.txt'
FUZZHEADER_PAYLOAD = 'payloads/fuzz_header.txt'
FUZZPARAM_PAYLOAD = 'payloads/fuzz_param.txt'

# plugin FuzzHeader's param
URL = 'http://127.0.0.1:8080/'  # your url for reverse connection
HOST = '127.0.0.1'  # your host for reverse shell
PORT = '10080'  # your port for reverse shell
R_PORT = '8080'  # remote port for backdoor
